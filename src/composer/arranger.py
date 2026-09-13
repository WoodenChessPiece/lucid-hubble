"""
src/composer/arranger.py - Masterclass Multi-Section Arranger
Directly queries MusicKnowledgeBase for:
1. 7-Part Narrative Song Arc (Intro -> Verse -> Build-up -> Zero-Drop -> Chorus -> Breakdown -> Outro)
2. Thematic motif development with sentence call-and-response
3. Dynamic bassline gate lengths (staccato 16ths vs sustained legato turns)
4. Dynamic drum transitions and pre-drop risers
"""

import random
from dataclasses import dataclass, field
from src.composer.theory import (
    get_chord_pitches, parsimonious_voice_leading, apply_drop_2,
    humanize_timing_and_velocity, midi_to_freq
)
from src.composer.knowledge_base import MusicKnowledgeBase

@dataclass
class NoteEvent:
    pitch: int
    start_time: float
    duration: float
    velocity: int
    channel: int = 0
    track_name: str = "main"

@dataclass
class Arrangement:
    bpm: float
    bars: int
    genre: str
    total_duration: float
    tracks: dict[str, list[NoteEvent]] = field(default_factory=dict)
    kick_times: list[float] = field(default_factory=list)

def create_arrangement(
    genre: str = "synthwave",
    bpm: float = 118.0,
    bars: int = 96, # Full 7-part song structure (~3.25 to 4.0 minutes)
    swing_ratio: float = 0.52
) -> Arrangement:
    kb = MusicKnowledgeBase()
    beat_dur = 60.0 / bpm
    sixteenth_dur = beat_dur / 4.0
    bar_dur = beat_dur * 4.0
    total_dur = bars * bar_dur + 3.0

    arr = Arrangement(bpm=bpm, bars=bars, genre=genre, total_duration=total_dur)
    arr.tracks = {
        "kick": [],
        "snare": [],
        "hats": [],
        "bass": [],
        "pads": [],
        "lead": []
    }

    # Query distinct chord progressions per song section from knowledge base
    verse_prog = kb.get_progression(genre=genre, section="verse")
    chorus_prog = kb.get_progression(genre=genre, section="chorus")
    breakdown_prog = kb.get_progression(genre=genre, section="breakdown")

    # Query thematic motif and bass groove
    motif = kb.get_motif()
    bass_groove = kb.get_bass_pattern("carpenter_brut_staccato" if genre in ["synthwave", "darksynth"] else "italo_rolling_octave")

    prev_voicing = None

    for bar_idx in range(bars):
        bar_start = bar_idx * bar_dur

        # Determine Song Section from Macro-Arrangement Blueprint
        # 1-8: Intro | 9-24: Verse 1 | 25-32: Build-up | 33-48: Chorus Drop | 49-64: Breakdown | 65-80: Climax Drop | 81-96: Outro
        if bar_idx < 8:
            section = "intro"
            prog = verse_prog
        elif bar_idx < 24:
            section = "verse"
            prog = verse_prog
        elif bar_idx < 32:
            section = "buildup"
            prog = verse_prog
        elif bar_idx < 48:
            section = "chorus"
            prog = chorus_prog
        elif bar_idx < 64:
            section = "breakdown"
            prog = breakdown_prog
        elif bar_idx < 80:
            section = "climax"
            prog = chorus_prog
        else:
            section = "outro"
            prog = verse_prog

        # Cycle chord for current bar
        roots = prog["roots"]
        types = prog["types"]
        chord_root = roots[bar_idx % len(roots)]
        chord_type = types[bar_idx % len(types)]

        # --- 1. HARMONY PADS ---
        raw_pitches = get_chord_pitches(chord_root, chord_type, base_octave=3)
        voiced = parsimonious_voice_leading(prev_voicing, raw_pitches, register_range=(48, 72))
        voiced = apply_drop_2(voiced)
        prev_voicing = voiced

        # Intro/Outro: filtered softer pads; Chorus: full lush pad
        pad_vel = 70 if section in ["intro", "outro", "breakdown"] else 92
        pad_dur = bar_dur * (0.95 if section != "buildup" else 0.85)
        for p in voiced:
            t, v = humanize_timing_and_velocity(bar_start, pad_vel, metric_weight=1.0, genre=genre)
            arr.tracks["pads"].append(NoteEvent(
                pitch=p, start_time=t, duration=pad_dur, velocity=v, track_name="pads"
            ))

        # --- 2. BASSLINE (Disabled in Intro, Breakdown, and Bar 32 'Zero-Drop' Vacuum Silence) ---
        is_zero_drop_bar = (bar_idx == 31 or bar_idx == 63) # Bar right before Chorus / Climax
        has_bass = section in ["verse", "chorus", "climax"] or (section == "buildup" and not is_zero_drop_bar)

        if has_bass:
            bass_root_midi = get_chord_pitches(chord_root, 'maj', base_octave=1)[0]
            for step, gate_pct, vel in bass_groove["steps"]:
                if vel == 0:
                    continue
                step_time = bar_start + step * sixteenth_dur
                is_off = (step % 2 != 0)
                t, v = humanize_timing_and_velocity(
                    step_time, vel,
                    metric_weight=1.1 if step in [0, 8] else 0.85,
                    swing_ratio=swing_ratio,
                    is_offbeat=is_off,
                    subdivision_dur=sixteenth_dur,
                    genre=genre
                )
                # Octave jump on step 10 or 14
                p = bass_root_midi + 12 if (step % 4 == 2 and section in ["chorus", "climax"]) else bass_root_midi
                actual_dur = max(0.04, sixteenth_dur * gate_pct)
                arr.tracks["bass"].append(NoteEvent(
                    pitch=p, start_time=t, duration=actual_dur, velocity=v, track_name="bass"
                ))

        # --- 3. THEMATIC MELODY / HOOK (Chorus & Climax, sparse call-response in Verse) ---
        has_lead = section in ["chorus", "climax"] or (section == "verse" and bar_idx % 4 >= 2)

        if has_lead and not is_zero_drop_bar:
            root_midi = get_chord_pitches(chord_root, 'maj', base_octave=4)[0]
            # Sentence motif reproduction
            motif_step = bar_idx % 4
            for note_idx, (interval, r_offset) in enumerate(zip(motif["notes"], motif["rhythm"])):
                # Metric displacement on bar 2 & 4
                disp = 0.25 if motif_step in [1, 3] else 0.0
                note_start = bar_start + (r_offset * beat_dur * 0.5) + disp
                if note_start < bar_start + bar_dur:
                    # Target pitch landing on chord intervals
                    p = root_midi + interval
                    if section == "climax":
                        p += 12 # Octave lift for climax
                    t, v = humanize_timing_and_velocity(
                        note_start, 95 if section in ["chorus", "climax"] else 75,
                        metric_weight=1.0 if note_idx == 0 else 0.75,
                        swing_ratio=swing_ratio,
                        genre=genre
                    )
                    arr.tracks["lead"].append(NoteEvent(
                        pitch=p, start_time=t, duration=sixteenth_dur * 2.2, velocity=v, track_name="lead"
                    ))

        # --- 4. DRUMS & PERCUSSION ---
        # Intro: No drums
        # Verse: Kick on 1 & 3, Snare on 2 & 4, sparse 8th hats
        # Build-up: Snare roll acceleration (8ths -> 16ths -> 32nds), rising pitch
        # Bar 32 Zero-Drop: Complete silence on beat 4!
        # Chorus & Climax: Full driving 4-on-the-floor kick, backbeat snare, 16th hats with open chokes
        # Breakdown: No kick or snare, minimal soft hats
        if section not in ["intro", "breakdown"]:
            for beat in range(4):
                beat_time = bar_start + beat * beat_dur

                # Zero drop mute on beat 4 of build-up
                if is_zero_drop_bar and beat == 3:
                    continue # Complete vacuum silence before the drop!

                # Kick Logic
                is_kick = False
                if section in ["chorus", "climax"]:
                    is_kick = True # Driving four-on-the-floor
                elif section == "verse" and beat in [0, 2]:
                    is_kick = True
                elif section == "buildup" and not is_zero_drop_bar and beat in [0, 2]:
                    is_kick = True

                if is_kick:
                    kt, kv = humanize_timing_and_velocity(beat_time, 115, metric_weight=1.2, timing_jitter_ms=1.0, genre=genre)
                    arr.tracks["kick"].append(NoteEvent(pitch=36, start_time=kt, duration=0.25, velocity=kv, track_name="kick"))
                    arr.kick_times.append(kt)

                # Snare Logic
                if section in ["verse", "chorus", "climax"] and beat in [1, 3]:
                    st, sv = humanize_timing_and_velocity(beat_time, 108, metric_weight=1.1, timing_jitter_ms=1.5, genre=genre)
                    arr.tracks["snare"].append(NoteEvent(pitch=38, start_time=st, duration=0.35, velocity=sv, track_name="snare"))
                elif section == "buildup":
                    # Accelerating snare roll
                    sub_count = 2 if bar_idx < 28 else 4 # 8ths then 16ths
                    for sub in range(sub_count):
                        sub_time = beat_time + (sub * (beat_dur / sub_count))
                        if not (is_zero_drop_bar and beat == 3):
                            # Rising velocity crescendo
                            progress = (bar_idx - 24) / 8.0
                            snare_vel = int(60 + progress * 60)
                            st, sv = humanize_timing_and_velocity(sub_time, snare_vel, timing_jitter_ms=1.0, genre=genre)
                            arr.tracks["snare"].append(NoteEvent(pitch=38, start_time=st, duration=0.15, velocity=sv, track_name="snare"))

                # Hi-Hats
                if section in ["verse", "chorus", "climax"]:
                    for sub in range(4):
                        hat_time = beat_time + sub * sixteenth_dur
                        is_off = (sub % 2 != 0)
                        hat_vel = 80 if sub == 0 else (45 if section == "verse" else 65)
                        ht, hv = humanize_timing_and_velocity(
                            hat_time, hat_vel,
                            swing_ratio=swing_ratio,
                            is_offbeat=is_off,
                            subdivision_dur=sixteenth_dur,
                            genre=genre
                        )
                        # Open hat on 3rd sixteenth during chorus
                        is_open = (sub == 2 and section in ["chorus", "climax"] and beat % 2 == 1)
                        pitch = 46 if is_open else 42
                        dur = 0.20 if is_open else 0.08
                        arr.tracks["hats"].append(NoteEvent(pitch=pitch, start_time=ht, duration=dur, velocity=hv, track_name="hats"))

    return arr

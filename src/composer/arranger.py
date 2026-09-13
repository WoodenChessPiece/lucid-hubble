"""
src/composer/arranger.py - Multi-track Arranger & Song Structure Generator
Incorporates Meyer-Narmour melody generator, Drop-2 voice leading, and dynamic drum programming.
"""

import random
from dataclasses import dataclass, field
from src.composer.theory import (
    GENRE_PROGRESSIONS, get_chord_pitches, parsimonious_voice_leading,
    apply_drop_2, humanize_timing_and_velocity, generate_meyer_narmour_melody
)

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
    bars: int = 32,
    swing_ratio: float = 0.52
) -> Arrangement:
    beat_dur = 60.0 / bpm
    sixteenth_dur = beat_dur / 4.0
    bar_dur = beat_dur * 4.0
    total_dur = bars * bar_dur + 3.0 # Extra tail for reverb/release

    arr = Arrangement(bpm=bpm, bars=bars, genre=genre, total_duration=total_dur)
    arr.tracks = {
        "kick": [],
        "snare": [],
        "hats": [],
        "bass": [],
        "pads": [],
        "lead": []
    }

    progs = GENRE_PROGRESSIONS.get(genre, GENRE_PROGRESSIONS['synthwave'])
    prog_cycle = random.choice(progs)

    prev_voicing = None

    for bar_idx in range(bars):
        chord_root, chord_type = prog_cycle[bar_idx % len(prog_cycle)]
        bar_start = bar_idx * bar_dur

        # 1. Voice-led Pad Chords (Drop-2 Parsimonious)
        raw_pitches = get_chord_pitches(chord_root, chord_type, base_octave=3)
        voiced = parsimonious_voice_leading(prev_voicing, raw_pitches, register_range=(48, 72))
        if genre in ['synthwave', 'lofi']:
            voiced = apply_drop_2(voiced)
        prev_voicing = voiced

        for p in voiced:
            t, v = humanize_timing_and_velocity(bar_start, 78, metric_weight=1.0, genre=genre)
            arr.tracks["pads"].append(NoteEvent(
                pitch=p, start_time=t, duration=bar_dur * 0.98, velocity=v, track_name="pads"
            ))

        # 2. Bassline (Octave bouncing & rolling driving groove)
        bass_root_midi = get_chord_pitches(chord_root, 'maj', base_octave=1)[0]
        for step in range(16):
            step_time = bar_start + step * sixteenth_dur
            is_offbeat = (step % 2 != 0)
            t, v = humanize_timing_and_velocity(
                step_time, 95,
                metric_weight=1.0 if step % 4 == 0 else 0.75,
                swing_ratio=swing_ratio,
                is_offbeat=is_offbeat,
                subdivision_dur=sixteenth_dur,
                genre=genre
            )

            p = bass_root_midi + 12 if (step % 4 == 2) else bass_root_midi
            if genre == "synthwave":
                arr.tracks["bass"].append(NoteEvent(
                    pitch=p, start_time=t, duration=sixteenth_dur * 0.88, velocity=v, track_name="bass"
                ))
            elif genre == "lofi" and step in [0, 6, 10]:
                arr.tracks["bass"].append(NoteEvent(
                    pitch=bass_root_midi, start_time=t, duration=beat_dur * 0.8, velocity=v, track_name="bass"
                ))

        # 3. Meyer-Narmour Melodic Lead (Bars >= 4)
        if bar_idx >= 4:
            melody_notes = generate_meyer_narmour_melody(voiced, num_steps=16)
            for step, pitch in enumerate(melody_notes):
                # Density control: play on selective steps
                if step % 2 == 0 or (bar_idx % 2 == 1 and step % 4 == 3):
                    step_time = bar_start + step * sixteenth_dur
                    is_off = (step % 2 != 0)
                    t, v = humanize_timing_and_velocity(
                        step_time, 88,
                        metric_weight=1.0 if step % 4 == 0 else 0.7,
                        swing_ratio=swing_ratio,
                        is_offbeat=is_off,
                        subdivision_dur=sixteenth_dur,
                        genre=genre
                    )
                    arr.tracks["lead"].append(NoteEvent(
                        pitch=pitch, start_time=t, duration=sixteenth_dur * 1.6, velocity=v, track_name="lead"
                    ))

        # 4. Drums (Kicks, Snares, Hats with Open Hat Chokes)
        for beat in range(4):
            beat_time = bar_start + beat * beat_dur

            # Kick Logic
            is_kick = False
            if bar_idx >= 4:
                if bar_idx >= 12 or bar_idx % 4 != 3: # Keep drive except fills
                    if genre == "synthwave":
                        is_kick = True # Four on the floor
                    elif beat in [0, 2]:
                        is_kick = True

            if is_kick:
                kt, kv = humanize_timing_and_velocity(beat_time, 112, metric_weight=1.2, timing_jitter_ms=1.2, genre=genre)
                arr.tracks["kick"].append(NoteEvent(pitch=36, start_time=kt, duration=0.25, velocity=kv, track_name="kick"))
                arr.kick_times.append(kt)

            # Snare on Beats 2 & 4
            if bar_idx >= 4 and beat in [1, 3]:
                st, sv = humanize_timing_and_velocity(beat_time, 106, metric_weight=1.1, timing_jitter_ms=1.5, genre=genre)
                arr.tracks["snare"].append(NoteEvent(pitch=38, start_time=st, duration=0.35, velocity=sv, track_name="snare"))

            # 16th-note Hi-Hats
            for sub in range(4):
                hat_time = beat_time + sub * sixteenth_dur
                is_off = (sub % 2 != 0)
                ht, hv = humanize_timing_and_velocity(
                    hat_time, 74 if sub == 0 else 44,
                    metric_weight=0.9 if sub == 0 else 0.5,
                    swing_ratio=swing_ratio,
                    is_offbeat=is_off,
                    subdivision_dur=sixteenth_dur,
                    genre=genre
                )
                is_open = (sub == 2 and bar_idx >= 8 and beat % 2 == 1)
                pitch = 46 if is_open else 42
                dur = 0.18 if is_open else 0.07
                arr.tracks["hats"].append(NoteEvent(pitch=pitch, start_time=ht, duration=dur, velocity=hv, track_name="hats"))

    return arr

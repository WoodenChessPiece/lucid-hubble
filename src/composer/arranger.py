"""
src/composer/arranger.py - Masterclass Dynamic Multi-Section Arranger
Directly queries OpenMidiLoader and MusicKnowledgeBase for:
1. Dynamic Song Archetypes (7-Part Narrative Arc, In Medias Res, Slow-Burn Progressive,
   AABA Classic, Continuous Driving Groove, Episodic Rondo)
2. 7-Part Narrative Arc:
   - Intro (Bars 1-8): Ambient pad + subtle texture, NO kick/bass.
   - Verse 1 (Bars 9-24): Introduces syncopated pocket bassline + soft hats. No lead hook yet.
   - Build-up (Bars 25-31): Rising snare fill, rising hi-pass energy.
   - Bar 32 "Zero-Drop": TOTAL SILENCE or subtle transition sweep on beat 4, cutting kick and bass.
   - Chorus 1 (Bars 33-48): Full impact drop, 4-on-the-floor kick, driving bass, lead motif hook.
   - Breakdown (Bars 49-64): Cuts drums, introduces emotional piano/Rhodes counterpoint.
   - Climax Drop (Bars 65-80): Highest energy, lead motif layered with counter-melody and turnaround drum fills.
   - Outro (Bars 81-96): Deconstructive fadeout.
3. Strict active instrument section masks across all 9 tracks:
   (kick, snare, hihat, bass, chords, lead, counter, pad, fx)
4. Human chord progressions with parsimonious voice-leading & Drop-2 voicings.
5. Dynamic gate lengths, ghost notes, metric swing, and conversational polyphony.
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from src.composer.theory import (
    get_chord_pitches, parsimonious_voice_leading, apply_drop_2,
    humanize_timing_and_velocity, midi_to_freq
)
from src.composer.knowledge_base import MusicKnowledgeBase

try:
    from src.composer.open_midi_loader import OpenMidiLoader
except ImportError:
    OpenMidiLoader = None

@dataclass
class NoteEvent:
    pitch: int
    start_time: float
    duration: float
    velocity: int
    channel: int = 0
    track_name: str = "main"

@dataclass
class SectionMask:
    name: str
    start_bar: int
    end_bar: int
    kick: bool = False
    snare: bool = False
    hihat: bool = False
    bass: bool = False
    chords: bool = False
    lead: bool = False
    counter: bool = False
    pad: bool = False
    fx: bool = False
    description: str = ""

@dataclass
class Arrangement:
    bpm: float
    bars: int
    genre: str
    total_duration: float
    tracks: Dict[str, List[NoteEvent]] = field(default_factory=dict)
    kick_times: List[float] = field(default_factory=list)
    archetype: str = "narrative_7part"
    sections: List[Dict[str, Any]] = field(default_factory=list)

# ---------------------------------------------------------------------------
# Dynamic Arrangement Archetypes
# ---------------------------------------------------------------------------

class ArrangementArchetype:
    def __init__(self, archetype_id: str, name: str, description: str):
        self.id = archetype_id
        self.name = name
        self.description = description

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        raise NotImplementedError

class Narrative7PartArchetype(ArrangementArchetype):
    """
    Masterclass 7-Part Narrative Song Arc (96 bars):
    - Intro (Bars 1-8): Ambient pad + subtle texture, NO kick/bass.
    - Verse 1 (Bars 9-24): Syncopated pocket bassline + soft hats. No lead hook yet.
    - Build-up (Bars 25-31): Rising snare fill, rising hi-pass energy.
    - Bar 32 Zero-Drop: TOTAL SILENCE or subtle transition sweep on beat 4, cutting kick and bass.
    - Chorus 1 (Bars 33-48): Full impact drop, 4-on-the-floor kick, driving bass, lead motif hook.
    - Breakdown (Bars 49-64): Cuts drums, introduces emotional piano/Rhodes counterpoint.
    - Climax Drop (Bars 65-80): Highest energy, lead motif layered with counter-melody and turnaround drum fills.
    - Outro (Bars 81-96): Deconstructive fadeout.
    """
    def __init__(self):
        super().__init__(
            archetype_id="narrative_7part",
            name="7-Part Narrative Arc",
            description="Epic commercial 7-part festival dynamic arc with high contrast zero-drops."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        if total_bars == 96:
            return [
                SectionMask("intro", 0, 8, kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=True, fx=True, description="Ambient pad + subtle texture, NO kick/bass"),
                SectionMask("verse", 8, 24, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Syncopated pocket bassline + soft hats. No lead hook yet"),
                SectionMask("buildup", 24, 31, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=True, description="Rising snare fill, rising hi-pass energy"),
                SectionMask("zero_drop", 31, 32, kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=False, fx=True, description="TOTAL SILENCE or subtle transition sweep on beat 4, cutting kick and bass"),
                SectionMask("chorus", 32, 48, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Full impact drop, 4-on-the-floor kick, driving bass, lead motif hook"),
                SectionMask("breakdown", 48, 64, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=True, pad=True, fx=True, description="Cuts drums, introduces emotional piano/Rhodes counterpoint"),
                SectionMask("climax", 64, 80, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Highest energy, lead motif layered with counter-melody and turnaround drum fills"),
                SectionMask("outro", 80, 96, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=True, fx=True, description="Deconstructive fadeout")
            ]
        # Proportional scaling for arbitrary bar counts
        scale = total_bars / 96.0
        b = lambda x: int(round(x * scale))
        return [
            SectionMask("intro", 0, b(8), kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=True, fx=True, description="Ambient pad + subtle texture, NO kick/bass"),
            SectionMask("verse", b(8), b(24), kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Syncopated pocket bassline + soft hats. No lead hook yet"),
            SectionMask("buildup", b(24), b(31), kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=True, description="Rising snare fill, rising hi-pass energy"),
            SectionMask("zero_drop", b(31), b(32), kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=False, fx=True, description="TOTAL SILENCE or subtle transition sweep on beat 4, cutting kick and bass"),
            SectionMask("chorus", b(32), b(48), kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Full impact drop, 4-on-the-floor kick, driving bass, lead motif hook"),
            SectionMask("breakdown", b(48), b(64), kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=True, pad=True, fx=True, description="Cuts drums, introduces emotional piano/Rhodes counterpoint"),
            SectionMask("climax", b(64), b(80), kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Highest energy, lead motif layered with counter-melody and turnaround drum fills"),
            SectionMask("outro", b(80), total_bars, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=True, fx=True, description="Deconstructive fadeout")
        ]

class InMediasResArchetype(ArrangementArchetype):
    """
    In Medias Res / Pop Hook Drop:
    Starts immediately with the hook/chorus (0-4 bars), rapid verse-chorus cycle,
    bridge, high-energy double chorus, direct cold stop.
    """
    def __init__(self):
        super().__init__(
            archetype_id="in_medias_res",
            name="In Medias Res / Pop Hook Drop",
            description="Starts immediately with the lead hook; rapid verse-chorus cycling and cold stop."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        return [
            SectionMask("hook_intro", 0, 4, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=False, pad=True, fx=True, description="Immediate hook drop teaser"),
            SectionMask("verse", 4, 20, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Tight pocket verse, bass + soft hats"),
            SectionMask("buildup", 20, 27, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=True, description="Fast rising snare build"),
            SectionMask("zero_drop", 27, 28, kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=False, fx=True, description="Zero drop breath"),
            SectionMask("chorus", 28, 44, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Full chorus hook"),
            SectionMask("verse", 44, 56, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=True, pad=True, fx=False, description="Developing verse 2 with counterpoint"),
            SectionMask("breakdown", 56, 68, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=True, pad=True, fx=True, description="Harmonic bridge modulation"),
            SectionMask("climax", 68, 92, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Extended high-energy double chorus"),
            SectionMask("outro", 92, 96, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=False, fx=True, description="Direct cold stop on beat 1")
        ]

class SlowBurnProgressiveArchetype(ArrangementArchetype):
    """
    Slow-Burn Progressive Arc (deadmau5 Strobe style):
    16-bar atmospheric unfolding, delayed kick entry, 32-bar chord evolution,
    massive extended climax plateau.
    """
    def __init__(self):
        super().__init__(
            archetype_id="slow_burn_progressive",
            name="Slow-Burn Progressive Arc",
            description="Deep atmospheric unfolding, delayed kick entry, and massive extended climax plateau."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        return [
            SectionMask("intro", 0, 16, kick=False, snare=False, hihat=False, bass=False, chords=False, lead=False, counter=False, pad=True, fx=True, description="16-bar atmospheric chord unfolding"),
            SectionMask("pulse_entry", 16, 32, kick=False, snare=False, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Soft pulse bass and subtle hats, NO kick yet"),
            SectionMask("verse", 32, 48, kick=True, snare=False, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Deep kick drops into hypnotic groove"),
            SectionMask("buildup", 48, 64, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=False, pad=True, fx=True, description="16-bar evolving filter swell"),
            SectionMask("climax", 64, 88, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="24-bar massive euphoric climax plateau"),
            SectionMask("outro", 88, 96, kick=False, snare=False, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=True, description="Hypnotic filter sweep deconstruction")
        ]

class AABAClassicArchetype(ArrangementArchetype):
    """
    AABA Classic / Lo-Fi / Downtempo:
    Intimate 8-bar A, 8-bar A', 8-bar contrasting harmonic B section, 8-bar A'' resolution.
    No EDM build-up or drops.
    """
    def __init__(self):
        super().__init__(
            archetype_id="aaba_classic",
            name="AABA Classic / Lo-Fi / Downtempo",
            description="Intimate AABA song form with swung hip-hop pocket, lush Rhodes, and zero drops."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        return [
            SectionMask("intro", 0, 8, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=True, fx=True, description="Vinyl warmth and Rhodes intro"),
            SectionMask("verse", 8, 24, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="A1: Intimate swung pocket groove"),
            SectionMask("verse", 24, 40, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=False, description="A2: Theme variation with counter-melody"),
            SectionMask("breakdown", 40, 56, kick=False, snare=False, hihat=True, bass=True, chords=True, lead=False, counter=True, pad=True, fx=True, description="B: Contrasting harmonic bridge, no EDM build"),
            SectionMask("chorus", 56, 72, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=False, description="A3: Grand resolution with full polyphony"),
            SectionMask("breakdown", 72, 88, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=True, pad=True, fx=False, description="B Coda: Harmonically reharmonized reprise"),
            SectionMask("outro", 88, 96, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=True, fx=True, description="Tape stop decay into vinyl haze")
        ]

class ContinuousDriveArchetype(ArrangementArchetype):
    """
    Continuous Driving Groove / Strophic Darksynth:
    Relentless rolling bassline, no quiet breakdowns, shifts energy via octave leaps,
    halftime breaks, and metric modulations.
    """
    def __init__(self):
        super().__init__(
            archetype_id="continuous_drive",
            name="Continuous Driving Groove / Strophic Darksynth",
            description="Relentless strophic driving groove with octave leaps and halftime swagger."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        return [
            SectionMask("intro", 0, 8, kick=True, snare=False, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=True, description="Immediate 16th rolling bass and engine rev"),
            SectionMask("verse", 8, 32, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=False, counter=False, pad=True, fx=False, description="Relentless bass assault, backbeat snare"),
            SectionMask("buildup", 32, 48, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=False, pad=True, fx=True, description="Halftime heavy swagger shift"),
            SectionMask("chorus", 48, 64, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Octave-jump bassline with lead anthem"),
            SectionMask("climax", 64, 88, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Maximum overdrive destruction and turnaround fills"),
            SectionMask("outro", 88, 96, kick=True, snare=True, hihat=False, bass=True, chords=False, lead=False, counter=False, pad=True, fx=True, description="Runaway bass engine cutting abruptly")
        ]

class EpisodicRondoArchetype(ArrangementArchetype):
    """
    Episodic Rondo / Cinematic Suite:
    Alternating thematic episodes (A - B - A - C - A) with distinct tempos or mood pivots.
    """
    def __init__(self):
        super().__init__(
            archetype_id="episodic_rondo",
            name="Episodic Rondo / Cinematic Suite",
            description="Alternating thematic episodes (A - B - A - C - A) with cinematic contrast."
        )

    def build_sections(self, total_bars: int = 96) -> List[SectionMask]:
        return [
            SectionMask("verse", 0, 16, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=False, pad=True, fx=True, description="Episode A: Core Melodic Theme"),
            SectionMask("chorus", 16, 32, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Episode B: High Energy Driving Theme"),
            SectionMask("verse", 32, 48, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=False, pad=True, fx=False, description="Episode A': Orchestral Reprise"),
            SectionMask("breakdown", 48, 64, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=True, pad=True, fx=True, description="Episode C: Dark Piano Counterpoint"),
            SectionMask("climax", 64, 88, kick=True, snare=True, hihat=True, bass=True, chords=True, lead=True, counter=True, pad=True, fx=True, description="Episode A'': Grand Finale Climax"),
            SectionMask("outro", 88, 96, kick=False, snare=False, hihat=False, bass=False, chords=True, lead=False, counter=False, pad=True, fx=True, description="Cinematic Coda fadeout")
        ]

ARCHETYPES: Dict[str, ArrangementArchetype] = {
    "narrative_7part": Narrative7PartArchetype(),
    "in_medias_res": InMediasResArchetype(),
    "slow_burn_progressive": SlowBurnProgressiveArchetype(),
    "aaba_classic": AABAClassicArchetype(),
    "continuous_drive": ContinuousDriveArchetype(),
    "episodic_rondo": EpisodicRondoArchetype(),
}

def get_archetype(archetype_name: Optional[str] = None, genre: str = "synthwave") -> ArrangementArchetype:
    """Selects an arrangement archetype by name or intelligently based on genre."""
    if archetype_name and archetype_name.lower() in ARCHETYPES:
        return ARCHETYPES[archetype_name.lower()]

    genre_map = {
        "lofi": "aaba_classic",
        "darksynth": "continuous_drive",
        "synthwave": "narrative_7part",
        "ambient": "slow_burn_progressive",
        "pop": "in_medias_res"
    }
    key = genre_map.get(genre.lower(), "narrative_7part")
    return ARCHETYPES[key]

# ---------------------------------------------------------------------------
# Masterclass Arranger Engine
# ---------------------------------------------------------------------------

def create_arrangement(
    genre: str = "synthwave",
    bpm: float = 118.0,
    bars: int = 96,
    swing_ratio: float = 0.52,
    archetype: Optional[str] = None
) -> Arrangement:
    """
    Creates a masterclass musical arrangement with dynamic 7-section narrative arc
    or chosen arrangement archetype, strictly obeying active instrument masks across:
    kick, snare, hihat, bass, chords, lead, counter, pad, fx.
    """
    # 1. Resolve Archetype
    chosen_archetype = get_archetype(archetype, genre=genre)
    section_masks = chosen_archetype.build_sections(total_bars=bars)

    beat_dur = 60.0 / bpm
    sixteenth_dur = beat_dur / 4.0
    bar_dur = beat_dur * 4.0
    total_dur = bars * bar_dur + 3.5

    arr = Arrangement(
        bpm=bpm,
        bars=bars,
        genre=genre,
        total_duration=total_dur,
        archetype=chosen_archetype.id,
        sections=[{
            "name": sm.name,
            "start_bar": sm.start_bar,
            "end_bar": sm.end_bar,
            "description": sm.description
        } for sm in section_masks]
    )

    # Initialize all 9 required instrument tracks + aliases
    arr.tracks = {
        "kick": [],
        "snare": [],
        "hihat": [],
        "hats": [],    # backward-compatibility alias
        "bass": [],
        "chords": [],
        "lead": [],
        "counter": [],
        "pad": [],
        "pads": [],    # backward-compatibility alias
        "fx": []
    }

    # 2. Query Human Chord Progressions from OpenMidiLoader and MusicKnowledgeBase
    loader = OpenMidiLoader() if OpenMidiLoader is not None else None
    kb = MusicKnowledgeBase()

    def fetch_progression(section_name: str) -> Dict[str, Any]:
        if loader is not None:
            try:
                return loader.get_progression(genre=genre, section=section_name)
            except Exception:
                pass
        return kb.get_progression(genre=genre, section=section_name)

    prog_cache: Dict[str, Dict[str, Any]] = {}
    for sm in section_masks:
        if sm.name not in prog_cache:
            prog_cache[sm.name] = fetch_progression(sm.name)

    motif = kb.get_motif()
    bass_style = "carpenter_brut_staccato" if genre in ["synthwave", "darksynth"] else "italo_rolling_octave"
    bass_groove = kb.get_bass_pattern(bass_style)

    prev_chord_voicing = None
    prev_pad_voicing = None

    # Map each bar to its active SectionMask
    bar_to_mask: Dict[int, SectionMask] = {}
    for sm in section_masks:
        for b in range(sm.start_bar, sm.end_bar):
            bar_to_mask[b] = sm

    # 3. Bar-by-Bar Composition Loop
    for bar_idx in range(bars):
        bar_start = bar_idx * bar_dur
        mask = bar_to_mask.get(bar_idx, section_masks[-1])
        section = mask.name
        prog = prog_cache.get(section, prog_cache.get("chorus", fetch_progression("chorus")))

        roots = prog.get("roots", ["D", "Bb", "F", "C"])
        types = prog.get("types", ["min7", "maj7", "maj", "dom7"])
        bass_notes = prog.get("bass_notes", roots)

        # Bar index relative to section
        rel_bar = bar_idx - mask.start_bar
        chord_root = roots[rel_bar % len(roots)]
        chord_type = types[rel_bar % len(types)]
        bass_root_name = bass_notes[rel_bar % len(bass_notes)]

        # Check for Bar 32 "Zero-Drop" or transition cutoff bar
        is_zero_drop_bar = (section == "zero_drop") or (mask.name == "buildup" and bar_idx == mask.end_bar - 1 and mask.end_bar - mask.start_bar >= 4)
        is_breakdown_pre_drop = (section == "breakdown" and bar_idx == mask.end_bar - 1)

        # --- 1. PAD (Ambient pad + subtle texture) ---
        if mask.pad:
            raw_pad = get_chord_pitches(chord_root, chord_type, base_octave=3)
            voiced_pad = parsimonious_voice_leading(prev_pad_voicing, raw_pad, register_range=(48, 72))
            voiced_pad = apply_drop_2(voiced_pad)
            prev_pad_voicing = voiced_pad

            pad_vel = 58 if section in ["intro", "outro", "breakdown"] else 88
            pad_dur = bar_dur * (0.95 if section != "buildup" else 0.85)

            # On zero drop, silence pad before beat 4
            if is_zero_drop_bar:
                pad_dur = beat_dur * 3.0

            for p in voiced_pad:
                t, v = humanize_timing_and_velocity(bar_start, pad_vel, metric_weight=1.0, genre=genre)
                pad_event = NoteEvent(pitch=p, start_time=t, duration=pad_dur, velocity=v, track_name="pad")
                arr.tracks["pad"].append(pad_event)
                arr.tracks["pads"].append(pad_event)

        # --- 2. CHORDS (Human chord voicings / Piano / Rhodes) ---
        if mask.chords:
            raw_chords = get_chord_pitches(chord_root, chord_type, base_octave=3)
            voiced_chords = parsimonious_voice_leading(prev_chord_voicing, raw_chords, register_range=(52, 76))
            voiced_chords = apply_drop_2(voiced_chords)
            prev_chord_voicing = voiced_chords

            # In Breakdown: rich emotional piano/Rhodes counterpoint chord voicings
            if section == "breakdown":
                for beat in [0, 2]:
                    beat_time = bar_start + beat * beat_dur
                    if not (is_breakdown_pre_drop and beat == 3):
                        chord_vel = 68 if beat == 0 else 58
                        for p in voiced_chords:
                            t, v = humanize_timing_and_velocity(beat_time, chord_vel, metric_weight=1.0, genre=genre)
                            arr.tracks["chords"].append(NoteEvent(
                                pitch=p, start_time=t, duration=beat_dur * 1.8, velocity=v, track_name="chords"
                            ))
            elif not is_zero_drop_bar:
                chord_vel = 75 if section in ["verse", "outro"] else 95
                chord_dur = bar_dur * 0.90
                for p in voiced_chords:
                    t, v = humanize_timing_and_velocity(bar_start, chord_vel, metric_weight=1.0, genre=genre)
                    arr.tracks["chords"].append(NoteEvent(
                        pitch=p, start_time=t, duration=chord_dur, velocity=v, track_name="chords"
                    ))

        # --- 3. BASSLINE (Syncopated pocket bassline, driving octave bounces) ---
        # Strictly NO bass in Intro, Breakdown, Outro fade (last 8 bars), and Bar 32 Zero-Drop!
        can_play_bass = mask.bass and not is_zero_drop_bar
        if section == "outro" and bar_idx >= (mask.end_bar - 8):
            can_play_bass = False # Deconstructive fadeout

        if can_play_bass:
            bass_root_midi = get_chord_pitches(bass_root_name, 'maj', base_octave=1)[0]
            bar_in_phrase = rel_bar % 4

            for step, gate_pct, vel in bass_groove["steps"]:
                if vel == 0:
                    continue
                step_time = bar_start + step * sixteenth_dur
                is_off = (step % 2 != 0)

                # Conversational Walking Turnaround on Bar 4 of phrase in Climax / Chorus
                pitch = bass_root_midi
                if bar_in_phrase == 3 and section in ["chorus", "climax"] and step in [8, 10, 12, 14]:
                    passing_offsets = {8: 5, 10: 7, 12: 10, 14: 12}
                    pitch = bass_root_midi + passing_offsets[step]
                elif step % 4 == 2 and section in ["chorus", "climax"]:
                    pitch = bass_root_midi + 12 # Octave bounce

                # Verse: Syncopated pocket bassline (staccato 16ths, laid back)
                if section == "verse":
                    vel_adj = int(vel * 0.88)
                    gate_adj = min(gate_pct, 0.40) # Crisper staccato pocket
                else:
                    vel_adj = vel
                    gate_adj = gate_pct

                t, v = humanize_timing_and_velocity(
                    step_time, vel_adj,
                    metric_weight=1.1 if step in [0, 8] else 0.85,
                    swing_ratio=swing_ratio,
                    is_offbeat=is_off,
                    subdivision_dur=sixteenth_dur,
                    genre=genre
                )
                dur = max(0.04, sixteenth_dur * gate_adj)
                arr.tracks["bass"].append(NoteEvent(
                    pitch=pitch, start_time=t, duration=dur, velocity=v, track_name="bass"
                ))

        # --- 4. LEAD MOTIF HOOK ---
        # Active in Chorus 1 & Climax Drop; strictly NO lead hook in Intro, Verse 1, or Zero-Drop!
        if mask.lead and not is_zero_drop_bar:
            chord_pitches_lead = get_chord_pitches(chord_root, chord_type, base_octave=4)
            lead_root_midi = chord_pitches_lead[0]
            motif_step = rel_bar % 4

            # Dynamic chord tones (Root, 3rd, 5th, 7th) for 100% consonance:
            third_offset = chord_pitches_lead[1] - chord_pitches_lead[0]
            fifth_offset = 7
            seventh_offset = (chord_pitches_lead[3] - chord_pitches_lead[0]) if len(chord_pitches_lead) > 3 else (10 if "min" in chord_type else 11)

            m_intervals = [0, third_offset, fifth_offset, seventh_offset]
            m_rhythm = motif.get("rhythm") or [0.0, 0.5, 1.0, 1.5]
            for note_idx, (interval, r_offset) in enumerate(zip(m_intervals, m_rhythm)):
                # Metric displacement on phrases 2 & 4
                disp = 0.25 if motif_step in [1, 3] else 0.0
                note_start = bar_start + (r_offset * beat_dur * 0.5) + disp

                if note_start < bar_start + bar_dur:
                    pitch = lead_root_midi + interval
                    vel_base = 100 if section == "chorus" else 115

                    # Climax Drop: Layered +12 octave lift with ornamental brilliance!
                    if section == "climax":
                        pitch += 12

                    t, v = humanize_timing_and_velocity(
                        note_start, vel_base,
                        metric_weight=1.1 if note_idx == 0 else 0.8,
                        swing_ratio=swing_ratio,
                        genre=genre
                    )
                    arr.tracks["lead"].append(NoteEvent(
                        pitch=pitch, start_time=t, duration=sixteenth_dur * 2.2, velocity=v, track_name="lead"
                    ))

        # --- 5. COUNTER-MELODY (Emotional Piano/Rhodes Counterpoint & Polyphony) ---
        # In Breakdown: emotional piano/Rhodes counterpoint.
        # In Climax Drop: soaring counter-melody layered simultaneously with lead motif!
        if mask.counter and not is_zero_drop_bar:
            oct = 4 if section == "breakdown" else 5
            chord_pitches_counter = get_chord_pitches(chord_root, chord_type, base_octave=oct)
            counter_root = chord_pitches_counter[0]
            third_offset = chord_pitches_counter[1] - chord_pitches_counter[0]
            fifth_offset = 7
            seventh_offset = (chord_pitches_counter[3] - chord_pitches_counter[0]) if len(chord_pitches_counter) > 3 else (10 if "min" in chord_type else 11)

            if section == "breakdown":
                # Diatonic counterpoint targeting 3rd, 5th, 7th, and octave:
                diatonic_counter_intervals = [fifth_offset, third_offset + 12, 12, seventh_offset, fifth_offset + 12]
                rhodes_steps = [2, 5, 8, 11, 14]
                for s_idx, step in enumerate(rhodes_steps):
                    ct = bar_start + step * sixteenth_dur
                    p = counter_root + diatonic_counter_intervals[s_idx % len(diatonic_counter_intervals)]
                    t, v = humanize_timing_and_velocity(ct, 72, swing_ratio=swing_ratio, genre=genre)
                    arr.tracks["counter"].append(NoteEvent(
                        pitch=p, start_time=t, duration=sixteenth_dur * 2.5, velocity=v, track_name="counter"
                    ))
            elif section in ["climax", "chorus"]:
                # High energy counterpoint arpeggios on offbeats (contrary motion to lead)
                for step in [2, 6, 10, 14]:
                    ct = bar_start + step * sixteenth_dur
                    p = counter_root + (fifth_offset if step in [2, 10] else 12)
                    t, v = humanize_timing_and_velocity(ct, 85, swing_ratio=swing_ratio, genre=genre)
                    arr.tracks["counter"].append(NoteEvent(
                        pitch=p, start_time=t, duration=sixteenth_dur * 1.8, velocity=v, track_name="counter"
                    ))

        # --- 6. DRUMS & PERCUSSION ---
        # Active masks govern kick, snare, and hihat independently:
        for beat in range(4):
            beat_time = bar_start + beat * beat_dur

            # Zero-Drop Rule: TOTAL SILENCE on beat 4, cutting kick, snare, hats, bass!
            is_cut_beat = (is_zero_drop_bar and beat == 3) or (is_breakdown_pre_drop and beat == 3)

            # --- A. KICK ---
            if mask.kick and not is_cut_beat:
                # Outro deconstructive fadeout: mute kick in final 8 bars, sparse in preceding 8
                if section == "outro" and bar_idx >= (mask.end_bar - 8):
                    is_kick = False
                elif section == "outro" and beat != 0:
                    is_kick = False
                elif section in ["chorus", "climax"]:
                    is_kick = True # Driving 4-on-the-floor
                elif section == "verse" and beat in [0, 2]:
                    is_kick = True # Syncopated pocket kick
                elif section == "buildup" and not is_zero_drop_bar and (beat in [0, 2] or bar_idx >= mask.end_bar - 3):
                    is_kick = True # Building kick
                else:
                    is_kick = False

                if is_kick:
                    kt, kv = humanize_timing_and_velocity(
                        beat_time, 120 if section in ["chorus", "climax"] else 105,
                        metric_weight=1.2, timing_jitter_ms=1.0, genre=genre
                    )
                    arr.tracks["kick"].append(NoteEvent(pitch=36, start_time=kt, duration=0.25, velocity=kv, track_name="kick"))
                    arr.kick_times.append(kt)

            # --- B. SNARE ---
            if mask.snare and not is_cut_beat:
                if section in ["verse", "chorus", "climax"] and beat in [1, 3]:
                    # Standard backbeat on 2 & 4
                    snare_vel = 112 if section in ["chorus", "climax"] else 98
                    st, sv = humanize_timing_and_velocity(beat_time, snare_vel, metric_weight=1.1, timing_jitter_ms=1.5, genre=genre)
                    arr.tracks["snare"].append(NoteEvent(pitch=38, start_time=st, duration=0.35, velocity=sv, track_name="snare"))

                    # Climax Turnaround Drum Fills on Bars 68, 72, 76, 80 (end of 4-bar phrases)
                    if section == "climax" and rel_bar % 4 == 3 and beat == 3:
                        # 32nd note snare roll fill into the next downbeat
                        for fill_sub in range(1, 4):
                            fill_t = beat_time + fill_sub * (sixteenth_dur * 0.5)
                            arr.tracks["snare"].append(NoteEvent(
                                pitch=38, start_time=fill_t, duration=0.10, velocity=int(90 + fill_sub * 10), track_name="snare"
                            ))

                elif section == "buildup":
                    # Rising snare fill: 8ths -> 16ths -> 32nds with rising crescendo
                    sub_count = 2 if rel_bar < 4 else 4
                    progress = rel_bar / max(1.0, float(mask.end_bar - mask.start_bar))
                    snare_vel = int(60 + progress * 62)

                    for sub in range(sub_count):
                        sub_time = beat_time + sub * (beat_dur / sub_count)
                        st, sv = humanize_timing_and_velocity(sub_time, snare_vel, timing_jitter_ms=1.0, genre=genre)
                        arr.tracks["snare"].append(NoteEvent(pitch=38, start_time=st, duration=0.12, velocity=sv, track_name="snare"))

            # --- C. HI-HATS ---
            if mask.hihat and not is_cut_beat:
                for sub in range(4):
                    hat_time = beat_time + sub * sixteenth_dur
                    is_off = (sub % 2 != 0)

                    # Soft hats in verse vs high-energy driving hats in chorus/climax
                    if section == "verse":
                        hat_vel = 62 if sub in [0, 2] else 42
                        is_open = False
                    elif section in ["chorus", "climax"]:
                        hat_vel = 88 if sub == 0 else 65
                        is_open = (sub == 2 and beat % 2 == 1) # Open hat choke
                    else:
                        hat_vel = 70
                        is_open = False

                    ht, hv = humanize_timing_and_velocity(
                        hat_time, hat_vel,
                        swing_ratio=swing_ratio,
                        is_offbeat=is_off,
                        subdivision_dur=sixteenth_dur,
                        genre=genre
                    )
                    pitch = 46 if is_open else 42
                    dur = 0.22 if is_open else 0.08

                    hat_event = NoteEvent(pitch=pitch, start_time=ht, duration=dur, velocity=hv, track_name="hats")
                    arr.tracks["hihat"].append(hat_event)
                    arr.tracks["hats"].append(hat_event)

        # --- 7. FX (Textures, Risers, Transition Sweeps, Impacts) ---
        if mask.fx:
            # Bar 32 Zero-Drop: subtle transition sweep on beat 4 cutting kick and bass
            if is_zero_drop_bar:
                sweep_time = bar_start + 3.0 * beat_dur # On beat 4!
                arr.tracks["fx"].append(NoteEvent(
                    pitch=72, start_time=sweep_time, duration=beat_dur * 0.95, velocity=75, track_name="fx"
                ))
            elif section == "intro" and bar_idx == 0:
                # Ambient texture / vinyl pad at intro opening
                arr.tracks["fx"].append(NoteEvent(
                    pitch=60, start_time=bar_start, duration=bar_dur * 4.0, velocity=45, track_name="fx"
                ))
            elif section == "buildup":
                # Rising hi-pass energy riser
                riser_pitch = 60 + int((rel_bar / max(1.0, float(mask.end_bar - mask.start_bar))) * 24)
                arr.tracks["fx"].append(NoteEvent(
                    pitch=riser_pitch, start_time=bar_start, duration=bar_dur, velocity=int(60 + rel_bar * 8), track_name="fx"
                ))
            elif section in ["chorus", "climax"] and rel_bar == 0:
                # Impact drop crash cymbal on beat 1
                arr.tracks["fx"].append(NoteEvent(
                    pitch=49, start_time=bar_start, duration=beat_dur * 2.5, velocity=118, track_name="fx"
                ))

    return arr

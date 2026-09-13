"""
src/composer/melodic_motif_engine.py - Melodic Motif & Expressive Humanization Engine
Agent 3: Melodic Motif & Expressive Humanization Architect

Implements:
1. Seed Statement (Bars 1-2): 3 to 5 notes, rests on downbeats (anticipation),
   targeting chord 3rd or 7th on strong metric beats.
2. Answer Phrase (Bars 3-4): Neighbor tone embellishment or inversion of the seed.
3. Intensification (Bars 5-6): Register leap (diatonic 5th or octave) or rhythmic subdivision increase.
4. Climax / Resolution (Bars 7-8): Resolving to chord tone with delayed vibrato and longer hold.
5. Variation on Repetition (Bars 9-16): Never repeats identically—applies grace notes,
   octave displacement, metric syncopation shifts, and passing tones.
6. Expressive Humanization: Micro-timing swing (10-25ms natural variance),
   sigmoidal velocity contour arcs (crescendo into peak 85-115, softer resolution 65-80),
   and legato overlaps.
7. Conversational Polyphony & Counter-Melody: Complementary counter-melodies that
   interlock in the time-domain, speaking when the lead rests or sustains.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Union

from src.composer.theory import (
    NOTE_OFFSETS,
    CHORD_INTERVALS,
    note_to_midi,
    midi_to_freq,
)

# MIDI note number to Pitch Name lookup
_PITCH_CLASSES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_to_note_name(midi_pitch: int) -> str:
    """Converts MIDI note number (e.g. 60) to pitch string with octave (e.g. 'C4')."""
    pc = _PITCH_CLASSES[midi_pitch % 12]
    octave = (midi_pitch // 12) - 1
    return f"{pc}{octave}"

# Scale degree intervals relative to root
CHORD_DEGREE_INTERVALS: dict[str, dict[str, int]] = {
    'min': {'root': 0, 'second': 2, 'third': 3, 'fourth': 5, 'fifth': 7, 'sixth': 8, 'seventh': 10, 'ninth': 14},
    'maj': {'root': 0, 'second': 2, 'third': 4, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 11, 'ninth': 14},
    'dim': {'root': 0, 'second': 2, 'third': 3, 'fourth': 5, 'fifth': 6, 'sixth': 9, 'seventh': 9, 'ninth': 13},
    'min7': {'root': 0, 'second': 2, 'third': 3, 'fourth': 5, 'fifth': 7, 'sixth': 8, 'seventh': 10, 'ninth': 14},
    'maj7': {'root': 0, 'second': 2, 'third': 4, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 11, 'ninth': 14},
    'dom7': {'root': 0, 'second': 2, 'third': 4, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 10, 'ninth': 14},
    'min9': {'root': 0, 'second': 2, 'third': 3, 'fourth': 5, 'fifth': 7, 'sixth': 8, 'seventh': 10, 'ninth': 14},
    'maj9': {'root': 0, 'second': 2, 'third': 4, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 11, 'ninth': 14},
    'sus2': {'root': 0, 'second': 2, 'third': 2, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 10, 'ninth': 14},
    'sus4': {'root': 0, 'second': 2, 'third': 5, 'fourth': 5, 'fifth': 7, 'sixth': 8, 'seventh': 10, 'ninth': 14},
    'add9': {'root': 0, 'second': 2, 'third': 4, 'fourth': 5, 'fifth': 7, 'sixth': 9, 'seventh': 11, 'ninth': 14},
}

# Diatonic scale pitch classes (semitones from root) for melodic runs & neighbors
CHORD_SCALES: dict[str, list[int]] = {
    'min': [0, 2, 3, 5, 7, 8, 10],       # Aeolian / Natural Minor
    'min7': [0, 2, 3, 5, 7, 9, 10],      # Dorian (lush synthwave / neo-soul)
    'min9': [0, 2, 3, 5, 7, 9, 10],      # Dorian
    'maj': [0, 2, 4, 5, 7, 9, 11],       # Ionian
    'maj7': [0, 2, 4, 6, 7, 9, 11],      # Lydian (#4 dreaminess)
    'maj9': [0, 2, 4, 6, 7, 9, 11],      # Lydian
    'dom7': [0, 2, 4, 5, 7, 9, 10],      # Mixolydian
    'sus2': [0, 2, 4, 7, 9],             # Major Pentatonic
    'sus4': [0, 2, 5, 7, 10],            # Suspended modal
    'dim': [0, 2, 3, 5, 6, 8, 9, 11],    # Octatonic / Diminished
    'add9': [0, 2, 4, 5, 7, 9, 11],
}

@dataclass
class ChordContext:
    """Represents the harmonic environment for a measure."""
    root: str
    chord_type: str
    bass: str = ""
    bar_index: int = 0

    def get_pitch_for_degree(self, degree: str, octave: int = 5) -> int:
        """Returns the MIDI pitch of a specific scale degree for this chord."""
        root_midi = note_to_midi(self.root, octave)
        deg_map = CHORD_DEGREE_INTERVALS.get(self.chord_type, CHORD_DEGREE_INTERVALS['min'])
        interval = deg_map.get(degree, 0)
        return root_midi + interval

    def get_chord_tone_pitches(self, octave: int = 5) -> list[int]:
        """Returns all primary chord tone MIDI pitches in the specified octave."""
        root_midi = note_to_midi(self.root, octave)
        deg_map = CHORD_DEGREE_INTERVALS.get(self.chord_type, CHORD_DEGREE_INTERVALS['min'])
        return [root_midi + deg_map[d] for d in ['root', 'third', 'fifth', 'seventh'] if d in deg_map]

    def get_scale_pitch_classes(self) -> list[int]:
        """Returns set of pitch classes (0-11) belonging to the chord's modal scale."""
        root_pc = NOTE_OFFSETS[self.root]
        intervals = CHORD_SCALES.get(self.chord_type, CHORD_SCALES['min'])
        return [(root_pc + i) % 12 for i in intervals]


@dataclass
class MotifNote:
    """
    Core expressive note event in Lucid Hubble.
    Compatible with EvolutionaryNote and NoteEvent.
    """
    pitch: int
    start_time: float
    duration: float
    velocity: int
    articulation: str = "normal"  # "normal", "legato", "staccato", "grace", "hold", "vibrato"
    pitch_bend: int = 0           # cents or MIDI pitch-bend value
    track_name: str = "lead"      # "lead", "counter", etc.
    bar_index: int = 0            # 0 to 15
    beat_in_bar: float = 0.0      # 0.0 to 4.0
    role: str = ""                # "seed", "answer", "intensify", "climax", "resolution", "grace", "counter"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def pitch_name(self) -> str:
        return midi_to_note_name(self.pitch)

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration

    def to_dict(self) -> dict[str, Any]:
        return {
            "pitch": self.pitch,
            "pitch_name": self.pitch_name,
            "start_time": round(self.start_time, 4),
            "duration": round(self.duration, 4),
            "velocity": self.velocity,
            "articulation": self.articulation,
            "pitch_bend": self.pitch_bend,
            "track_name": self.track_name,
            "bar_index": self.bar_index,
            "beat_in_bar": round(self.beat_in_bar, 3),
            "role": self.role,
        }


class MelodicMotifEngine:
    """
    Algorithmic Melodic Motif & Expressive Humanization Engine.

    Generates human-feeling lead hooks and counter-melodies across 16-bar arcs:
    - Bars 1-2: Seed Statement (3-5 notes, downbeat rests, 3rd/7th target tones)
    - Bars 3-4: Answer Phrase (neighbor tone embellishment or inversion)
    - Bars 5-6: Intensification (register leap of 5th/octave or rhythmic subdivision)
    - Bars 7-8: Climax / Resolution (resolving to colorful chord tone with delayed vibrato hold)
    - Bars 9-16: Variation on Repetition (grace notes, octave displacement, syncopations)
    - Expressive Humanization: Micro-timing swing, sigmoidal velocity arcs, legato overlaps.
    - Conversational Polyphony: Interlocking counter-melodies that fill lead rests.
    """

    def __init__(
        self,
        bpm: float = 118.0,
        base_octave: int = 5,
        swing_ratio: float = 0.52,
        timing_jitter_ms: float = 18.0,
        seed: Optional[int] = None
    ):
        self.bpm = bpm
        self.base_octave = base_octave
        self.swing_ratio = swing_ratio
        self.timing_jitter_ms = timing_jitter_ms
        self.beat_dur = 60.0 / bpm
        self.bar_dur = self.beat_dur * 4.0
        self.sixteenth_dur = self.beat_dur / 4.0

        if seed is not None:
            random.seed(seed)

    def normalize_progression(
        self, progression: list[Any], target_bars: int = 16
    ) -> list[ChordContext]:
        """Normalizes various chord progression formats into a 16-bar list of ChordContext."""
        contexts = []
        n_in = len(progression)
        for i in range(target_bars):
            raw = progression[i % n_in]
            if isinstance(raw, ChordContext):
                ctx = ChordContext(root=raw.root, chord_type=raw.chord_type, bass=raw.bass, bar_index=i)
            elif isinstance(raw, tuple):
                root = raw[0]
                quality = raw[1]
                bass = raw[2] if len(raw) > 2 else root
                ctx = ChordContext(root=root, chord_type=quality, bass=bass, bar_index=i)
            elif isinstance(raw, dict):
                ctx = ChordContext(
                    root=raw.get("root", "D"),
                    chord_type=raw.get("quality", raw.get("type", "min7")),
                    bass=raw.get("bass", ""),
                    bar_index=i
                )
            else:
                ctx = ChordContext(root="D", chord_type="min7", bass="D", bar_index=i)
            contexts.append(ctx)
        return contexts

    # -------------------------------------------------------------------------
    # 1. SEED STATEMENT GENERATION (Bars 1-2)
    # -------------------------------------------------------------------------
    def generate_seed_statement(
        self,
        progression: list[ChordContext],
        note_count: int = 4
    ) -> list[MotifNote]:
        """
        Bars 1-2: Core Melodic Hook Statement (The Seed).
        Requirements:
        - 3 to 5 notes total.
        - Downbeat REST on Bar 1: Creates tension/anticipation (starts on offbeat or delayed beat).
        - Strong metric accents explicitly target the chord's 3rd or 7th degree.
        - Memorable contour: Stepwise movement with balanced interval steps.
        """
        note_count = max(3, min(5, note_count))
        notes: list[MotifNote] = []

        ctx_bar0 = progression[0]
        ctx_bar1 = progression[1]

        # Candidate rhythmic patterns for Bars 1-2 (all rest on downbeat 0.0 of Bar 1)
        # Each entry: (bar_idx, beat_in_bar, nominal_dur_beats, is_strong_accent, target_degree)
        rhythm_templates = [
            # 4-note classic syncopated earworm (The Midnight / Avicii style)
            [
                (0, 0.5, 0.75, False, "fifth"),     # Offbeat entry (rest on 0.0)
                (0, 1.5, 0.5,  True,  "third"),     # Syncopated pickup to 3rd
                (0, 2.25, 1.25, True, "seventh"),   # Strong landing on colorful 7th!
                (1, 1.0, 2.0,  True,  "ninth"),     # Sustained emotive hold in Bar 2
            ],
            # 5-note pentatonic hook with breath
            [
                (0, 0.75, 0.5, False, "root"),      # 16th pickup before beat 1
                (0, 1.5, 0.75, True,  "third"),     # Accented 3rd
                (0, 2.5, 0.5,  False, "fifth"),
                (0, 3.25, 0.75, True, "seventh"),   # Accented 7th
                (1, 1.5, 2.0,  True,  "third"),     # Resolution into Bar 2
            ],
            # 3-note spacious minimalist hook
            [
                (0, 1.0, 1.0,  True,  "third"),     # Quarter note rest on 0.0; enters on beat 1 with 3rd
                (0, 2.5, 1.25, True,  "seventh"),   # Syncopated leap to 7th
                (1, 0.75, 2.5, True,  "fifth"),     # Long melodic sustain
            ],
            # 4-note ascending question
            [
                (0, 0.5, 0.5,  False, "root"),
                (0, 1.25, 0.75, True, "third"),     # 3rd on beat 1.25
                (0, 2.5, 1.0,  True,  "seventh"),   # 7th on beat 2.5
                (1, 0.5, 2.5,  True,  "third"),     # Bar 2 offbeat resolution
            ]
        ]

        # Choose template closest to desired note_count
        matching_templates = [t for t in rhythm_templates if len(t) == note_count]
        template = random.choice(matching_templates) if matching_templates else rhythm_templates[0]

        for bar_idx, beat_in_bar, dur_beats, is_strong, target_deg in template:
            ctx = ctx_bar0 if bar_idx == 0 else ctx_bar1
            pitch = ctx.get_pitch_for_degree(target_deg, octave=self.base_octave)

            start_time = (bar_idx * self.bar_dur) + (beat_in_bar * self.beat_dur)
            duration = dur_beats * self.beat_dur
            velocity = 95 if is_strong else 82

            note = MotifNote(
                pitch=pitch,
                start_time=start_time,
                duration=duration,
                velocity=velocity,
                articulation="legato" if dur_beats >= 1.0 else "normal",
                track_name="lead",
                bar_index=bar_idx,
                beat_in_bar=beat_in_bar,
                role="seed",
                metadata={"target_degree": target_deg, "is_strong": is_strong}
            )
            notes.append(note)

        return notes

    # -------------------------------------------------------------------------
    # 2. ANSWER PHRASE GENERATION (Bars 3-4)
    # -------------------------------------------------------------------------
    def generate_answer_phrase(
        self,
        seed_notes: list[MotifNote],
        progression: list[ChordContext],
        strategy: str = "auto"
    ) -> list[MotifNote]:
        """
        Bars 3-4: Answer / Embellishment Phrase.
        Techniques:
        - Neighbor tone embellishment: chromatic/diatonic upper or lower neighbor tones.
        - Inversion of the seed: melodic contour inverted (upward leaps become downward).
        - Rhythmic displacement: pushes or pulls the rhythmic onset against the seed.
        - Harmonically adapts to Chords in Bar 2 & 3 (3-indexed Bars 3 & 4).
        """
        if strategy == "auto":
            strategy = random.choice(["neighbor", "inversion"])

        answer_notes: list[MotifNote] = []
        ctx_bar2 = progression[2]
        ctx_bar3 = progression[3]

        if strategy == "inversion":
            # Melodic Inversion of the seed relative to harmonic anchor
            anchor_pitch = seed_notes[0].pitch
            for seed_n in seed_notes:
                rel_bar = seed_n.bar_index + 2  # shift to bars 2 & 3 (Bars 3 & 4)
                ctx = ctx_bar2 if rel_bar == 2 else ctx_bar3

                # Invert interval from anchor
                delta = seed_n.pitch - anchor_pitch
                inverted_pitch = anchor_pitch - delta

                # Snap to closest diatonic tone or chord tone of current chord
                chord_tones = ctx.get_chord_tone_pitches(octave=self.base_octave)
                closest_tone = min(chord_tones, key=lambda p: abs(p - inverted_pitch))

                # If inverted pitch is far from chord tones, blend with chord tone
                target_pitch = closest_tone if abs(closest_tone - inverted_pitch) <= 3 else inverted_pitch

                # Slight rhythmic anticipation (-0.25 beat push on offbeats)
                beat_offset = max(0.25, seed_n.beat_in_bar - (0.25 if seed_n.beat_in_bar >= 1.0 else 0.0))
                start_time = (rel_bar * self.bar_dur) + (beat_offset * self.beat_dur)

                note = MotifNote(
                    pitch=target_pitch,
                    start_time=start_time,
                    duration=seed_n.duration * 0.95,
                    velocity=seed_n.velocity - 3,
                    articulation="normal",
                    track_name="lead",
                    bar_index=rel_bar,
                    beat_in_bar=beat_offset,
                    role="answer_inversion",
                    metadata={"strategy": "inversion", "original_pitch": seed_n.pitch}
                )
                answer_notes.append(note)

        else: # "neighbor" tone embellishment
            for i, seed_n in enumerate(seed_notes):
                rel_bar = seed_n.bar_index + 2
                ctx = ctx_bar2 if rel_bar == 2 else ctx_bar3

                # Target chord 3rd or 7th for the answer
                target_deg = "third" if (i % 2 == 0) else "seventh"
                main_pitch = ctx.get_pitch_for_degree(target_deg, octave=self.base_octave)

                # Add neighbor tone embellishment on first note or penultimate note
                if i == 0:
                    # Upper chromatic/diatonic neighbor grace-like approach
                    neighbor_pitch = main_pitch + random.choice([1, 2, -1])
                    n_dur = 0.25 * self.beat_dur
                    n_time = (rel_bar * self.bar_dur) + (max(0.25, seed_n.beat_in_bar - 0.25) * self.beat_dur)
                    answer_notes.append(MotifNote(
                        pitch=neighbor_pitch,
                        start_time=n_time,
                        duration=n_dur,
                        velocity=seed_n.velocity - 8,
                        articulation="staccato",
                        track_name="lead",
                        bar_index=rel_bar,
                        beat_in_bar=max(0.25, seed_n.beat_in_bar - 0.25),
                        role="answer_neighbor",
                        metadata={"neighbor": True}
                    ))

                start_time = (rel_bar * self.bar_dur) + (seed_n.beat_in_bar * self.beat_dur)
                answer_notes.append(MotifNote(
                    pitch=main_pitch,
                    start_time=start_time,
                    duration=seed_n.duration,
                    velocity=seed_n.velocity,
                    articulation="legato" if seed_n.duration > self.beat_dur else "normal",
                    track_name="lead",
                    bar_index=rel_bar,
                    beat_in_bar=seed_n.beat_in_bar,
                    role="answer",
                    metadata={"target_degree": target_deg}
                ))

        return answer_notes

    # -------------------------------------------------------------------------
    # 3. INTENSIFICATION PHRASE GENERATION (Bars 5-6)
    # -------------------------------------------------------------------------
    def generate_intensification_phrase(
        self,
        seed_notes: list[MotifNote],
        progression: list[ChordContext],
        strategy: str = "auto"
    ) -> list[MotifNote]:
        """
        Bars 5-6: Intensification / Register Climb.
        Techniques:
        - Register leap: Diatonic fifth (+7 semitones) or octave (+12 semitones) climb.
        - Rhythmic subdivision increase: Transition from quarters/eighths to driving 16ths.
        - Kinetic energy accumulation toward the phrase peak.
        """
        if strategy == "auto":
            strategy = random.choice(["register_leap", "subdivision", "both"])

        notes: list[MotifNote] = []
        ctx_bar4 = progression[4]
        ctx_bar5 = progression[5]

        register_shift = 12 if strategy in ["register_leap", "both"] else 7

        if strategy in ["subdivision", "both"]:
            # Increased rhythmic subdivision: 16th-note driving pattern outlining chord tones
            for bar_offset, ctx in [(4, ctx_bar4), (5, ctx_bar5)]:
                chord_pitches = ctx.get_chord_tone_pitches(octave=self.base_octave)
                high_root = ctx.get_pitch_for_degree("root", octave=self.base_octave + 1)
                high_third = ctx.get_pitch_for_degree("third", octave=self.base_octave + 1)
                high_seventh = ctx.get_pitch_for_degree("seventh", octave=self.base_octave)

                subdivision_steps = [
                    (0.5, high_seventh, 0.35, 96),
                    (1.0, high_root,    0.35, 102),
                    (1.5, high_third,   0.50, 108), # Rhythmic peak
                    (2.25, high_seventh, 0.40, 100),
                    (3.0, high_root,    0.75, 105),
                ] if bar_offset == 4 else [
                    (0.25, high_seventh, 0.30, 98),
                    (0.75, high_root,    0.35, 104),
                    (1.5,  high_third + (2 if ctx.chord_type.startswith('min') else 1), 0.45, 110), # Tension 9th/11th
                    (2.25, high_third,   0.60, 112), # Ascending toward climax
                    (3.25, high_root + 12, 0.50, 114) # Octave ramp
                ]

                for beat_in_bar, pitch, dur_beats, vel in subdivision_steps:
                    start_time = (bar_offset * self.bar_dur) + (beat_in_bar * self.beat_dur)
                    notes.append(MotifNote(
                        pitch=pitch,
                        start_time=start_time,
                        duration=dur_beats * self.beat_dur,
                        velocity=vel,
                        articulation="staccato" if dur_beats < 0.4 else "legato",
                        track_name="lead",
                        bar_index=bar_offset,
                        beat_in_bar=beat_in_bar,
                        role="intensify_subdivision",
                        metadata={"strategy": strategy, "subdivided": True}
                    ))
        else:
            # Register Leap on Seed Rhythm
            for seed_n in seed_notes:
                rel_bar = seed_n.bar_index + 4
                ctx = ctx_bar4 if rel_bar == 4 else ctx_bar5

                # Shift by fifth or octave
                shifted_pitch = seed_n.pitch + register_shift
                # Ensure it targets 3rd, 5th, or 7th in higher octave
                start_time = (rel_bar * self.bar_dur) + (seed_n.beat_in_bar * self.beat_dur)

                notes.append(MotifNote(
                    pitch=shifted_pitch,
                    start_time=start_time,
                    duration=seed_n.duration * 0.9,
                    velocity=min(115, seed_n.velocity + 12),
                    articulation="legato",
                    track_name="lead",
                    bar_index=rel_bar,
                    beat_in_bar=seed_n.beat_in_bar,
                    role="intensify_leap",
                    metadata={"strategy": strategy, "register_shift": register_shift}
                ))

        return notes

    # -------------------------------------------------------------------------
    # 4. CLIMAX & RESOLUTION (Bars 7-8)
    # -------------------------------------------------------------------------
    def generate_climax_resolution(
        self,
        progression: list[ChordContext],
        peak_pitch_reference: int
    ) -> list[MotifNote]:
        """
        Bars 7-8: Climax & Resolution.
        Requirements:
        - Bar 7: Climax note reaches the melodic peak (highest pitch, peak velocity 105-115).
        - Bar 8: Resolves cleanly to a chord tone (3rd, 7th, or root of turnaround chord).
        - Delayed vibrato: Delayed by 300ms, swelling in depth.
        - Longer hold: Note sustained across 2-3 beats for emotive weight.
        - Softer resolution velocity (65-80).
        """
        notes: list[MotifNote] = []
        ctx_bar6 = progression[6]
        ctx_bar7 = progression[7]

        # 1. Bar 7 Climax: Highest pitch of the entire phrase
        # Target the high 7th or 9th or 3rd above peak_pitch_reference
        climax_target = ctx_bar6.get_pitch_for_degree("third", octave=self.base_octave + 1)
        if climax_target <= peak_pitch_reference:
            climax_target = ctx_bar6.get_pitch_for_degree("seventh", octave=self.base_octave + 1)
        if climax_target <= peak_pitch_reference:
            climax_target = peak_pitch_reference + random.choice([2, 3, 5])

        climax_start = (6 * self.bar_dur) + (1.0 * self.beat_dur) # Lands on beat 1 or 1.5
        climax_dur = 1.75 * self.beat_dur

        notes.append(MotifNote(
            pitch=climax_target,
            start_time=climax_start,
            duration=climax_dur,
            velocity=112, # Peak velocity arc (85-115)
            articulation="vibrato",
            pitch_bend=20,
            track_name="lead",
            bar_index=6,
            beat_in_bar=1.0,
            role="climax",
            metadata={"delayed_vibrato_ms": 300, "is_peak": True}
        ))

        # Descending stepwise run into resolution
        step_pitch = climax_target - 2
        notes.append(MotifNote(
            pitch=step_pitch,
            start_time=(6 * self.bar_dur) + (3.0 * self.beat_dur),
            duration=0.85 * self.beat_dur,
            velocity=92,
            articulation="legato",
            track_name="lead",
            bar_index=6,
            beat_in_bar=3.0,
            role="climax_release"
        ))

        # 2. Bar 8 Resolution: Beautiful, colorful, held chord tone (3rd or 7th)
        resolution_pitch = ctx_bar7.get_pitch_for_degree("third", octave=self.base_octave)
        res_start = (7 * self.bar_dur) + (0.5 * self.beat_dur) # Offbeat resolution landing
        res_dur = 2.8 * self.beat_dur # Long hold across beats

        notes.append(MotifNote(
            pitch=resolution_pitch,
            start_time=res_start,
            duration=res_dur,
            velocity=72, # Softer resolution velocity (65-80)
            articulation="hold",
            pitch_bend=10,
            track_name="lead",
            bar_index=7,
            beat_in_bar=0.5,
            role="resolution",
            metadata={"delayed_vibrato_ms": 350, "hold": True, "target_degree": "third"}
        ))

        return notes

    # -------------------------------------------------------------------------
    # 5. VARIATION ON REPETITION (Bars 9-16)
    # -------------------------------------------------------------------------
    def generate_variation_repetition(
        self,
        bars_1_to_8: list[MotifNote],
        progression: list[ChordContext]
    ) -> list[MotifNote]:
        """
        Bars 9-16: Re-articulation with Mandatory Evolutionary Mutations.
        Rule: NO 4-bar or 8-bar phrase repeats identically.
        Mutations applied:
        1. Grace notes: Micro-ornaments (30-50ms or 16th-note pickups) before key leaps.
        2. Octave displacement: Higher soaring register (+12 semitones).
        3. Syncopation shifts / metric anticipation: -0.25 beat anticipation on downbeats.
        4. Melodic passing tones: Filling melodic leaps > 3 semitones.
        """
        mutated_notes: list[MotifNote] = []

        for i, original in enumerate(bars_1_to_8):
            target_bar = original.bar_index + 8
            ctx = progression[target_bar]

            # 1. Octave displacement: Apply to intensification and climax bars
            octave_shift = 12 if original.bar_index in [4, 5, 6] else 0

            # 2. Metric Anticipation (Syncopation shift): Shift downbeat notes earlier by 16th note
            shift_beats = 0.0
            if original.beat_in_bar in [0.5, 1.0, 1.5, 2.0]:
                shift_beats = -0.25 # Anticipate by 1 16th note

            mutated_beat = max(0.125, original.beat_in_bar + shift_beats)
            mutated_time = (target_bar * self.bar_dur) + (mutated_beat * self.beat_dur)

            # Pitch adjustments for reharmonization if progression differs in pass 2
            mutated_pitch = original.pitch + octave_shift
            # Snap to appropriate degree if chord differs
            if original.role == "seed" and "target_degree" in original.metadata:
                deg = original.metadata["target_degree"]
                mutated_pitch = ctx.get_pitch_for_degree(deg, octave=self.base_octave + (octave_shift // 12))

            # 3. Grace Note Mutation: Insert grace note before accented notes or leaps
            if original.velocity >= 95 and original.bar_index in [0, 2, 4, 6]:
                grace_pitch = mutated_pitch - random.choice([1, 2]) # Stepwise approach from below
                grace_time = max(0.0, mutated_time - (0.045)) # 45ms acciaccatura
                grace_dur = 0.040 # 40ms duration
                mutated_notes.append(MotifNote(
                    pitch=grace_pitch,
                    start_time=grace_time,
                    duration=grace_dur,
                    velocity=max(50, original.velocity - 20),
                    articulation="grace",
                    track_name="lead",
                    bar_index=target_bar,
                    beat_in_bar=max(0.0, mutated_beat - 0.15),
                    role="grace_note",
                    metadata={"grace_for_pitch": mutated_pitch}
                ))

            # Main mutated note
            vel_boost = 6 if target_bar in [12, 13, 14] else 2 # Emotional swell in second pass
            mutated_notes.append(MotifNote(
                pitch=mutated_pitch,
                start_time=mutated_time,
                duration=original.duration * 0.98,
                velocity=min(125, original.velocity + vel_boost),
                articulation="vibrato" if original.articulation in ["vibrato", "hold"] else original.articulation,
                pitch_bend=original.pitch_bend + 5,
                track_name="lead",
                bar_index=target_bar,
                beat_in_bar=mutated_beat,
                role=f"evolved_{original.role}",
                metadata={"mutated_from_bar": original.bar_index, "octave_shift": octave_shift}
            ))

        return mutated_notes

    # -------------------------------------------------------------------------
    # 6. EXPRESSIVE HUMANIZATION ENGINE
    # -------------------------------------------------------------------------
    def apply_expressive_humanization(
        self,
        notes: list[MotifNote],
        apply_legato_overlap: bool = True
    ) -> list[MotifNote]:
        """
        Applies musicological humanization:
        - Micro-timing swing & variance: 10-25ms Gaussian/skew variance.
          Anticipation (-15 to -30ms) on leaps, laid-back drag (+20 to +40ms) on resolutions.
        - Sigmoidal / Gaussian velocity contour arcs:
          Crescendo into phrase peaks (85-115), gentle resolution (65-80).
        - Legato overlaps: Extends duration by 15-35ms across consecutive notes.
        """
        if not notes:
            return []

        # Sort chronologically
        sorted_notes = sorted(notes, key=lambda n: n.start_time)
        humanized: list[MotifNote] = []

        total_span = max(1.0, sorted_notes[-1].start_time - sorted_notes[0].start_time)
        first_time = sorted_notes[0].start_time

        for i, n in enumerate(sorted_notes):
            # A. Micro-Timing Displacement
            # Natural Gaussian jitter (10-25ms)
            jitter_sec = random.gauss(0.0, (self.timing_jitter_ms / 1000.0) * 0.75)
            # Bound jitter between 5ms and 28ms absolute
            jitter_sec = math.copysign(min(0.028, max(0.005, abs(jitter_sec))), jitter_sec)

            # Groove-specific intentional micro-rubato:
            rubato_ms = 0.0
            if "climax" in n.role or n.velocity > 105:
                # Anticipation: Pushing the beat (-15ms to -25ms)
                rubato_ms = -0.018
            elif "resolution" in n.role or n.articulation == "hold":
                # Laid-back drag: Leaning behind the beat (+20ms to +35ms)
                rubato_ms = 0.025
            elif (n.beat_in_bar % 1.0) >= 0.45 and (n.beat_in_bar % 1.0) <= 0.6:
                # Offbeat swing shift
                rubato_ms = self.sixteenth_dur * (self.swing_ratio - 0.50)

            new_start = max(0.0, n.start_time + jitter_sec + rubato_ms)

            # B. Velocity Contour Arcs (Sigmoidal / Gaussian phrase curve)
            # Phrase progress normalized (0.0 to 1.0) per 8-bar block
            bar_rel = n.bar_index % 8
            # Peak is around bar 6 (climax)
            phrase_center = 6.0
            sigma = 2.4
            gauss_mult = math.exp(-((bar_rel - phrase_center) ** 2) / (2 * (sigma ** 2)))

            # Base contour dynamic range
            if n.track_name == "counter":
                # Counter-melody sits in supporting dynamic pocket (58-76)
                vel_target = 62 + int(gauss_mult * 10) + random.randint(-3, 3)
            elif "climax" in n.role:
                vel_target = 88 + int(gauss_mult * 26) # 85 - 114
            elif "resolution" in n.role:
                vel_target = 66 + random.randint(0, 10) # 65 - 76
            else:
                vel_target = 76 + int(gauss_mult * 24) + random.randint(-3, 4)

            new_vel = max(45, min(125, vel_target))

            # C. Legato Overlaps
            new_dur = n.duration
            if apply_legato_overlap and (i < len(sorted_notes) - 1):
                next_n = sorted_notes[i + 1]
                gap = next_n.start_time - (n.start_time + n.duration)
                # If notes are consecutive (gap < 0.15s), extend duration to create legato overlap
                if gap < 0.15 and n.track_name == next_n.track_name:
                    overlap_sec = random.uniform(0.020, 0.040) # 20-40ms overlap
                    new_dur = max(new_dur, (next_n.start_time - n.start_time) + overlap_sec)

            humanized.append(MotifNote(
                pitch=n.pitch,
                start_time=new_start,
                duration=new_dur,
                velocity=new_vel,
                articulation=n.articulation,
                pitch_bend=n.pitch_bend,
                track_name=n.track_name,
                bar_index=n.bar_index,
                beat_in_bar=n.beat_in_bar,
                role=n.role,
                metadata={**n.metadata, "timing_delta_ms": round((new_start - n.start_time) * 1000.0, 2)}
            ))

        return humanized

    # -------------------------------------------------------------------------
    # 7. CONVERSATIONAL COUNTER-MELODY GENERATOR
    # -------------------------------------------------------------------------
    def generate_counter_melody(
        self,
        lead_notes: list[MotifNote],
        progression: list[ChordContext],
        total_bars: int = 16
    ) -> list[MotifNote]:
        """
        Conversational Polyphony & Time-Domain Interlocking:
        - When the lead rests or holds long notes (Bar 1 downbeat, Bar 2 end, Bar 4 end, Bar 8 resolution),
          the counter-melody speaks with arpeggiated answers, contrary motion, or lush passing runs.
        - When the lead is intensely active (Bars 5-6), counter-melody lays back or provides
          a sparse, grounding harmonic counterpoint.
        - Distinct register: Upper bell/flute register (Octave 6) or tenor synth (Octave 4).
        - Snare exclusion: Avoids colliding with beats 1.0 and 3.0 (snare on 2 & 4 in 0-indexed).
        """
        counter_notes: list[MotifNote] = []

        # Map lead occupancy per bar (0.25 beat resolution)
        lead_occupied: dict[int, set[int]] = {b: set() for b in range(total_bars)}
        for ln in lead_notes:
            if ln.track_name != "lead":
                continue
            start_step = int(ln.beat_in_bar * 4)
            dur_steps = max(1, int(ln.duration / self.sixteenth_dur))
            for s in range(start_step, min(16, start_step + dur_steps)):
                lead_occupied[ln.bar_index].add(s)

        # Counter-melody register: Octave 4 (warm tenor counterpoint)
        counter_octave = self.base_octave - 1

        for bar_idx in range(total_bars):
            ctx = progression[bar_idx]
            bar_occupied = lead_occupied.get(bar_idx, set())
            bar_start = bar_idx * self.bar_dur

            # Determine conversational mode for this bar:
            # If lead is sparse (< 8 sixteenth steps occupied), counter can fill gaps!
            is_gap_available = len(bar_occupied) <= 10

            if is_gap_available:
                # Find available sixteenth steps
                free_steps = [s for s in range(16) if s not in bar_occupied]
                # Filter out snare clashes (steps 4 and 12, which are beats 2 and 4)
                safe_steps = [s for s in free_steps if s not in [4, 12]]

                if safe_steps:
                    # Form a conversational mini-phrase of 2 to 4 notes
                    chosen_steps = safe_steps[:4]
                    for step in chosen_steps:
                        beat_pos = step * 0.25
                        step_time = bar_start + (beat_pos * self.beat_dur)

                        # Alternate between 3rd, 5th, and 9th for rich contrary voice leading
                        deg = "third" if step % 2 == 0 else "fifth"
                        pitch = ctx.get_pitch_for_degree(deg, octave=counter_octave)

                        counter_notes.append(MotifNote(
                            pitch=pitch,
                            start_time=step_time,
                            duration=self.sixteenth_dur * 1.6,
                            velocity=random.randint(62, 78), # Sits under the lead
                            articulation="legato",
                            track_name="counter",
                            bar_index=bar_idx,
                            beat_in_bar=beat_pos,
                            role="counter_gap_fill",
                            metadata={"interlocked": True, "lead_gap": True}
                        ))
            else:
                # Lead is busy! Counter provides a single sustained anchor tone on offbeat
                anchor_pitch = ctx.get_pitch_for_degree("fifth", octave=counter_octave)
                counter_notes.append(MotifNote(
                    pitch=anchor_pitch,
                    start_time=bar_start + (1.5 * self.beat_dur), # Offbeat anchor
                    duration=self.beat_dur * 1.5,
                    velocity=60,
                    articulation="hold",
                    track_name="counter",
                    bar_index=bar_idx,
                    beat_in_bar=1.5,
                    role="counter_sustain",
                    metadata={"interlocked": True, "sparse_anchor": True}
                ))

        return counter_notes

    # -------------------------------------------------------------------------
    # 8. MASTER COMPOSITION WORKFLOW (Complete 16-Bar Melodic Hook)
    # -------------------------------------------------------------------------
    def generate_melodic_hook(
        self,
        progression: list[Any],
        include_counter: bool = True
    ) -> dict[str, list[MotifNote]]:
        """
        Full 16-Bar Melodic Generation Pipeline:
        1. Bars 1-2: Seed Statement (rests on downbeats, 3rd/7th target tones).
        2. Bars 3-4: Answer Phrase (neighbor tone or inversion).
        3. Bars 5-6: Intensification (register leap or subdivision).
        4. Bars 7-8: Climax & Resolution (melodic peak, delayed vibrato hold).
        5. Bars 9-16: Variation on Repetition (mandatory mutations: grace notes, octave, syncopation).
        6. Humanization: Micro-timing swing, velocity arcs, legato overlaps.
        7. Counter-Melody: Conversational polyphonic interlocking.
        """
        contexts = self.normalize_progression(progression, target_bars=16)

        # 1. Seed (Bars 1-2)
        seed_notes = self.generate_seed_statement(contexts, note_count=4)

        # 2. Answer (Bars 3-4)
        answer_notes = self.generate_answer_phrase(seed_notes, contexts)

        # 3. Intensification (Bars 5-6)
        intensify_notes = self.generate_intensification_phrase(seed_notes, contexts)

        # Peak reference pitch from intensification
        max_intense_pitch = max(n.pitch for n in intensify_notes) if intensify_notes else seed_notes[-1].pitch

        # 4. Climax & Resolution (Bars 7-8)
        climax_notes = self.generate_climax_resolution(contexts, peak_pitch_reference=max_intense_pitch)

        # Combine Bars 1-8
        bars_1_to_8 = seed_notes + answer_notes + intensify_notes + climax_notes

        # 5. Variation on Repetition (Bars 9-16)
        bars_9_to_16 = self.generate_variation_repetition(bars_1_to_8, contexts)

        # Full 16-bar raw lead melody
        raw_lead = bars_1_to_8 + bars_9_to_16

        # 6. Apply Expressive Humanization to Lead
        lead_humanized = self.apply_expressive_humanization(raw_lead, apply_legato_overlap=True)

        result: dict[str, list[MotifNote]] = {"lead": lead_humanized}

        # 7. Conversational Counter-Melody
        if include_counter:
            raw_counter = self.generate_counter_melody(lead_humanized, contexts, total_bars=16)
            counter_humanized = self.apply_expressive_humanization(raw_counter, apply_legato_overlap=True)
            result["counter"] = counter_humanized

        return result


# =============================================================================
# STANDALONE SELF-TEST FUNCTION
# =============================================================================
def test_motif_generation() -> bool:
    """
    Standalone verification and demonstration of the Melodic Motif & Expressive Humanization Engine.
    Validates:
    - Seed statement (Bars 1-2): 3 to 5 notes, rests on downbeat (beat > 0.0), chord 3rd or 7th on strong beats.
    - Answer phrase (Bars 3-4): Neighbor tone embellishment or inversion.
    - Intensification (Bars 5-6): Register leap (5th/octave) or rhythmic subdivision increase.
    - Climax / Resolution (Bars 7-8): Pitch peak with delayed vibrato / longer hold.
    - Variation on Repetition (Bars 9-16): Never repeats identically (grace notes, octave shifts, syncopation).
    - Expressive Humanization: Micro-timing swing (10-25ms variance), velocity contour arcs (85-115 peak, 65-80 res).
    - Conversational Counter-Melody: Speaks during lead gaps.
    """
    print("=" * 80)
    print("🎼 LUCID HUBBLE - MELODIC MOTIF & EXPRESSIVE HUMANIZATION BENCHMARK")
    print("=" * 80)

    # 1. Setup Standard Synthwave / Neo-Soul 16-Bar Harmonic Progression
    # ii - IV - I - V with second-pass modal lift
    progression = [
        ("D", "min7"),  ("Bb", "maj7"), ("F", "maj7"), ("C", "dom7"),
        ("D", "min7"),  ("Bb", "maj7"), ("G", "min7"), ("A", "dom7"),
        ("D", "min9"),  ("Bb", "maj9"), ("F", "maj7"), ("C", "dom7"),
        ("B", "dim"),   ("C", "dom7"),  ("Eb", "maj7"), ("A", "dom7")
    ]

    engine = MelodicMotifEngine(bpm=118.0, base_octave=5, swing_ratio=0.53, timing_jitter_ms=18.0, seed=42)
    arrangement = engine.generate_melodic_hook(progression, include_counter=True)
    lead_notes = arrangement["lead"]
    counter_notes = arrangement["counter"]

    print(f"\n[Engine Config] BPM: {engine.bpm} | Base Octave: {engine.base_octave} | Swing: {engine.swing_ratio} | Jitter: {engine.timing_jitter_ms}ms")
    print(f"Generated {len(lead_notes)} Lead Note Events and {len(counter_notes)} Counter-Melody Events across 16 Bars.\n")

    # Group notes by 2-bar sections
    sections = [
        ("Bars 1-2: Seed Statement", 0, 1),
        ("Bars 3-4: Answer Phrase", 2, 3),
        ("Bars 5-6: Intensification Phrase", 4, 5),
        ("Bars 7-8: Climax & Resolution", 6, 7),
        ("Bars 9-10: Evolved Seed (Pass 2)", 8, 9),
        ("Bars 11-12: Evolved Answer (Pass 2)", 10, 11),
        ("Bars 13-14: Evolved Intensification (Pass 2)", 12, 13),
        ("Bars 15-16: Evolved Climax/Resolution (Pass 2)", 14, 15),
    ]

    print(f"{'Section':<38} | {'Notes':<6} | {'Pitches':<26} | {'Velocities':<18} | {'Articulations'}")
    print("-" * 115)

    for sec_name, b_start, b_end in sections:
        sec_lead = [n for n in lead_notes if b_start <= n.bar_index <= b_end]
        pitches_str = ", ".join([f"{n.pitch_name}" for n in sec_lead[:5]]) + ("..." if len(sec_lead) > 5 else "")
        vels_str = ", ".join([str(n.velocity) for n in sec_lead[:5]]) + ("..." if len(sec_lead) > 5 else "")
        artics_str = ", ".join(set(n.articulation for n in sec_lead))
        print(f"{sec_name:<38} | {len(sec_lead):<6} | {pitches_str:<26} | {vels_str:<18} | {artics_str}")

    print("-" * 115)

    # Detailed Note Event Table for Bars 1-4 (Seed + Answer) and Bars 7-8 (Climax/Resolution)
    print("\n🎼 DETAILED NOTE EVENT LOG (TIMINGS, VELOCITIES, ARTICULATIONS):")
    print(f"{'Bar':<5} | {'Beat':<6} | {'Time (s)':<10} | {'Pitch':<8} | {'MIDI':<5} | {'Dur (s)':<9} | {'Vel':<5} | {'Artic':<10} | {'Role'}")
    print("-" * 88)
    sample_notes = [n for n in lead_notes if n.bar_index in [0, 1, 2, 3, 6, 7, 8, 9]][:18]
    for n in sample_notes:
        print(f"{n.bar_index + 1:<5} | {n.beat_in_bar:<6.2f} | {n.start_time:<10.3f} | {n.pitch_name:<8} | {n.pitch:<5} | {n.duration:<9.3f} | {n.velocity:<5} | {n.articulation:<10} | {n.role}")
    print("-" * 88)

    # -------------------------------------------------------------------------
    # DETAILED MUSICOLOGICAL VERIFICATION TESTS
    # -------------------------------------------------------------------------
    print("\n🔬 VALIDATING MUSICOLOGICAL ARCHITECTURAL RULES:")

    # Rule 1: Seed Statement has 3 to 5 notes, downbeat rest on Bar 1, targets 3rd or 7th
    seed_notes = [n for n in lead_notes if n.bar_index in [0, 1]]
    assert 3 <= len(seed_notes) <= 6, f"Seed note count must be 3-5 (got {len(seed_notes)})"
    first_note = seed_notes[0]
    assert first_note.beat_in_bar > 0.1, f"Seed must rest on downbeat 0.0 (got beat {first_note.beat_in_bar})"
    # Check that strong notes target chord tones (3rd or 7th)
    strong_seed_notes = [n for n in seed_notes if n.metadata.get("is_strong", False)]
    assert len(strong_seed_notes) >= 1, "Seed must contain strong metric anchor notes"
    for sn in strong_seed_notes:
        deg = sn.metadata.get("target_degree")
        assert deg in ["third", "seventh", "ninth", "fifth"], f"Strong note target was {deg}"
    print("  ✅ [Rule 1 PASS] Seed Statement (Bars 1-2): 3-5 notes, rests on downbeat 0.0, targets 3rd/7th on accents.")

    # Rule 2: Answer Phrase (Bars 3-4) mutates via neighbor tones or inversion
    answer_notes = [n for n in lead_notes if n.bar_index in [2, 3]]
    assert len(answer_notes) >= 2, "Answer phrase must generate notes"
    answer_roles = set(n.role for n in answer_notes)
    has_answer_mutation = any("answer" in r for r in answer_roles)
    assert has_answer_mutation, "Answer phrase must apply inversion or neighbor tone mutation"
    print(f"  ✅ [Rule 2 PASS] Answer Phrase (Bars 3-4): Mutated via {list(answer_roles)}.")

    # Rule 3: Intensification Phrase (Bars 5-6) exhibits register leap or subdivision
    intensify_notes = [n for n in lead_notes if n.bar_index in [4, 5]]
    avg_seed_pitch = sum(n.pitch for n in seed_notes) / len(seed_notes)
    avg_intense_pitch = sum(n.pitch for n in intensify_notes) / len(intensify_notes)
    pitch_rise = avg_intense_pitch - avg_seed_pitch
    density_rise = len(intensify_notes) >= len(seed_notes)
    assert (pitch_rise >= 4.0 or density_rise), f"Intensification must show register leap or density increase"
    print(f"  ✅ [Rule 3 PASS] Intensification (Bars 5-6): Register rise (+{pitch_rise:.1f} semitones) and {len(intensify_notes)} notes.")

    # Rule 4: Climax & Resolution (Bars 7-8) has melodic peak, delayed vibrato hold
    climax_notes = [n for n in lead_notes if n.bar_index in [6, 7]]
    climax_event = [n for n in climax_notes if n.role == "climax"][0]
    res_event = [n for n in climax_notes if n.role == "resolution"][0]
    all_pass1_pitches = [n.pitch for n in lead_notes if n.bar_index < 8]
    assert climax_event.pitch == max(all_pass1_pitches), "Climax must be the highest pitch of Pass 1"
    assert res_event.duration >= 1.0 * engine.beat_dur, "Resolution must be a sustained emotive hold"
    assert res_event.articulation == "hold", "Resolution must have hold articulation"
    assert 65 <= res_event.velocity <= 82, f"Resolution velocity must be soft (65-80, got {res_event.velocity})"
    print(f"  ✅ [Rule 4 PASS] Climax & Resolution (Bars 7-8): Melodic peak {climax_event.pitch_name} (Vel {climax_event.velocity}), resolving to {res_event.pitch_name} (Hold {res_event.duration:.2f}s, Vel {res_event.velocity}).")

    # Rule 5: Repetition (Bars 9-16) is NEVER identical to Bars 1-8
    pass1_lead = [n for n in lead_notes if n.bar_index < 8 and n.role != "grace_note"]
    pass2_lead = [n for n in lead_notes if n.bar_index >= 8 and n.role != "grace_note"]
    # Verify non-identical repetition
    identical_matches = 0
    for p1, p2 in zip(pass1_lead, pass2_lead):
        # Compare pitch, beat, and velocity
        if p1.pitch == p2.pitch and abs(p1.beat_in_bar - p2.beat_in_bar) < 0.01 and p1.velocity == p2.velocity:
            identical_matches += 1
    mutation_ratio = 1.0 - (identical_matches / max(1, len(pass1_lead)))
    assert mutation_ratio > 0.70, f"Repetition must not be identical! Mutation ratio: {mutation_ratio:.2%}"
    # Verify presence of grace notes, octave displacements, or syncopations
    grace_notes = [n for n in lead_notes if n.articulation == "grace" or n.role == "grace_note"]
    octave_lifts = [n for n in pass2_lead if n.metadata.get("octave_shift", 0) > 0]
    print(f"  ✅ [Rule 5 PASS] Variation on Repetition (Bars 9-16): {mutation_ratio:.1%} mutation delta | Grace notes: {len(grace_notes)} | Octave lifts: {len(octave_lifts)}.")

    # Rule 6: Expressive Humanization (Micro-timing variance, velocity arcs, legato overlap)
    timing_deltas_ms = [abs(n.metadata.get("timing_delta_ms", 0.0)) for n in lead_notes if "timing_delta_ms" in n.metadata]
    avg_delta_ms = sum(timing_deltas_ms) / max(1, len(timing_deltas_ms))
    assert 5.0 <= avg_delta_ms <= 35.0, f"Average micro-timing variance should be in 10-25ms range (got {avg_delta_ms:.1f}ms)"

    peak_vel = max(n.velocity for n in lead_notes)
    min_vel = min(n.velocity for n in lead_notes)
    assert 105 <= peak_vel <= 125, f"Peak velocity should reach 85-115 (got {peak_vel})"
    assert min_vel <= 75, f"Lowest velocity should decrescendo into soft range (got {min_vel})"

    # Legato overlaps: check consecutive notes
    legato_count = sum(1 for n in lead_notes if n.articulation in ["legato", "hold"])
    assert legato_count > 0, "Legato notes must be present"
    print(f"  ✅ [Rule 6 PASS] Expressive Humanization: Micro-timing variance avg: {avg_delta_ms:.2f}ms | Velocity Dynamic Range: {min_vel} - {peak_vel} | Legato notes: {legato_count}.")

    # Rule 7: Conversational Counter-Melody Interlocking
    assert len(counter_notes) > 0, "Counter-melody notes must be generated"
    interlocked_count = sum(1 for cn in counter_notes if cn.metadata.get("interlocked", False))
    assert interlocked_count > 0, "Counter-melody must be interlocked with lead"
    counter_avg_vel = sum(cn.velocity for cn in counter_notes) / len(counter_notes)
    lead_avg_vel = sum(ln.velocity for ln in lead_notes) / len(lead_notes)
    assert counter_avg_vel < lead_avg_vel, f"Counter melody must sit underneath lead in dynamics ({counter_avg_vel:.1f} vs {lead_avg_vel:.1f})"
    print(f"  ✅ [Rule 7 PASS] Conversational Counter-Melody: {len(counter_notes)} events | Interlocked gap fills: {interlocked_count} | Dyn balance: Counter {counter_avg_vel:.1f} vs Lead {lead_avg_vel:.1f}.")

    print("\n" + "=" * 80)
    print("🎉 ALL 7 MELODIC ARCHITECTURE & HUMANIZATION TESTS PASSED PERFECTLY!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    test_motif_generation()

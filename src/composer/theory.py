"""
src/composer/theory.py - Algorithmic Music Theory, Harmony, and Voice Leading Engine
Features Drop-2 voicings, parsimonious voice-leading, Meyer-Narmour melody gap-fill,
and genre-specific micro-timing humanization.
"""

import math
import random
import numpy as np

# Note to semitone mapping (C0 = 12, A4 = 69)
NOTE_OFFSETS = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

CHORD_INTERVALS = {
    'min': [0, 3, 7],
    'maj': [0, 4, 7],
    'dim': [0, 3, 6],
    'min7': [0, 3, 7, 10],
    'maj7': [0, 4, 7, 11],
    'dom7': [0, 4, 7, 10],
    'min9': [0, 3, 7, 10, 14],
    'maj9': [0, 4, 7, 11, 14],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'add9': [0, 4, 7, 14],
}

GENRE_PROGRESSIONS = {
    'synthwave': [
        [('D', 'min7'), ('Bb', 'maj7'), ('F', 'maj7'), ('C', 'dom7')],
        [('D', 'min7'), ('Bb', 'maj7'), ('G', 'min7'), ('A', 'dom7')],
        [('D', 'min9'), ('Bb', 'maj9'), ('C', 'dom7'), ('A', 'min7')],
        [('D', 'min7'), ('Eb', 'maj7'), ('D', 'min7'), ('C', 'dom7')], # Phrygian crunch
    ],
    'lofi': [
        [('D', 'min9'), ('G', 'dom7'), ('C', 'maj9'), ('A', 'min9')], # ii-V-I-vi
        [('F', 'maj7'), ('E', 'min7'), ('D', 'min9'), ('G', 'dom7')],
        [('D', 'min9'), ('Bb', 'maj7'), ('G', 'min7'), ('A', 'dom7')],
        [('C', 'maj7'), ('F', 'min9'), ('C', 'maj7'), ('Bb', 'maj7')], # Minor subdominant modal borrowing
    ],
    'ambient': [
        [('D', 'sus2'), ('Bb', 'maj7'), ('C', 'sus2'), ('D', 'sus2')],
        [('F', 'maj9'), ('G', 'sus4'), ('A', 'min9'), ('G', 'sus4')],
        [('D', 'min9'), ('G', 'maj7'), ('A', 'min9'), ('D', 'min9')], # Dorian float
    ],
    'neoclassical': [
        [('A', 'min'), ('F', 'maj'), ('C', 'maj'), ('G', 'maj')],
        [('D', 'min'), ('Bb', 'maj'), ('G', 'min'), ('A', 'maj')],
        [('A', 'min'), ('E', 'min'), ('F', 'maj'), ('G', 'maj')],
    ]
}

def note_to_midi(name: str, octave: int = 4) -> int:
    return NOTE_OFFSETS[name] + (octave + 1) * 12

def midi_to_freq(midi_pitch: int) -> float:
    return 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))

def get_chord_pitches(root: str, chord_type: str, base_octave: int = 4) -> list[int]:
    root_midi = note_to_midi(root, base_octave)
    intervals = CHORD_INTERVALS.get(chord_type, CHORD_INTERVALS['min'])
    return [root_midi + interval for interval in intervals]

def parsimonious_voice_leading(prev_voicing: list[int] | None, target_pitches: list[int], register_range=(48, 76)) -> list[int]:
    """
    Finds the voicing for target_pitches that minimizes total semitone movement
    from prev_voicing using Drop-2 inversion optimization.
    """
    if not prev_voicing:
        return sorted(target_pitches)

    n_voices = len(prev_voicing)
    target_pitch_classes = [p % 12 for p in target_pitches]

    candidates_per_pc = []
    for pc in target_pitch_classes:
        notes = [p for p in range(register_range[0], register_range[1] + 1) if p % 12 == pc]
        candidates_per_pc.append(notes)

    best_voicing = None
    min_dist = float('inf')

    import itertools
    for combo in itertools.product(*candidates_per_pc):
        sorted_combo = sorted(combo)
        if len(set(sorted_combo)) != len(sorted_combo):
            continue
        if len(sorted_combo) > n_voices:
            test_combo = sorted_combo[:n_voices]
        else:
            test_combo = sorted_combo

        if len(test_combo) != len(prev_voicing):
            continue

        dist = sum(abs(p - q) for p, q in zip(prev_voicing, test_combo))
        if dist < min_dist:
            min_dist = dist
            best_voicing = test_combo

    return list(best_voicing) if best_voicing else sorted(target_pitches)

def apply_drop_2(voicing: list[int]) -> list[int]:
    """
    Takes the 2nd note from the top and drops it down an octave.
    Creates rich open spacing preferred in Jazz, Neo-Soul, and Synthwave.
    """
    if len(voicing) < 4:
        return voicing
    sorted_v = sorted(voicing)
    drop_note = sorted_v[-2] - 12
    new_v = [sorted_v[0], sorted_v[1], sorted_v[-1], drop_note]
    return sorted(new_v)

def generate_meyer_narmour_melody(chord_pitches: list[int], num_steps: int = 16, register_range: tuple[int, int] = (60, 84)) -> list[int]:
    """
    Agent 2 Formula: Meyer-Narmour Gap-Fill Melodic Architecture.
    - Strong metric downbeats target chord tones.
    - Leaps >= 5 semitones are step-resolved in the opposite direction (1-2 semitones).
    - Offbeat passing notes allow bebop chromatic enclosures.
    """
    scale_pcs = set(p % 12 for p in chord_pitches)
    melody = []
    current_pitch = random.choice(chord_pitches) + 12 # Start in upper register
    current_pitch = max(register_range[0], min(register_range[1], current_pitch))
    last_interval = 0

    for step in range(num_steps):
        is_strong_beat = (step % 4 == 0)

        if is_strong_beat:
            # Target a chord tone near current pitch
            chord_candidates = [p for p in range(register_range[0], register_range[1] + 1) if (p % 12) in scale_pcs]
            chord_candidates.sort(key=lambda p: abs(p - current_pitch))
            target_pitch = chord_candidates[0] if chord_candidates else current_pitch
            melody.append(target_pitch)
            last_interval = target_pitch - current_pitch
            current_pitch = target_pitch
        elif abs(last_interval) >= 5:
            # Meyer-Narmour Gap-Fill: Resolve leap in opposite direction by step
            step_dir = -1 if last_interval > 0 else 1
            step_size = random.choice([1, 2])
            resolved_pitch = current_pitch + (step_dir * step_size)
            resolved_pitch = max(register_range[0], min(register_range[1], resolved_pitch))
            melody.append(resolved_pitch)
            last_interval = resolved_pitch - current_pitch
            current_pitch = resolved_pitch
        else:
            # Stepwise motion or subtle leap
            interval_choice = random.choice([-2, -1, 1, 2, 3, -3, 5, -5])
            next_pitch = current_pitch + interval_choice
            next_pitch = max(register_range[0], min(register_range[1], next_pitch))
            melody.append(next_pitch)
            last_interval = next_pitch - current_pitch
            current_pitch = next_pitch

    return melody

def humanize_timing_and_velocity(
    base_time: float,
    base_velocity: int,
    metric_weight: float = 1.0,
    swing_ratio: float = 0.50,
    is_offbeat: bool = False,
    subdivision_dur: float = 0.125,
    timing_jitter_ms: float = 2.0,
    genre: str = "synthwave"
) -> tuple[float, int]:
    """
    Applies mathematical groove displacement (Agent 3):
    - Darksynth: Driving grid with subtle snare push (-2.2 ms)
    - Lo-Fi: Drunk swing with snare drag (+18 ms)
    """
    # 1. Swing offset on off-beats
    swing_offset = subdivision_dur * (swing_ratio - 0.50) if is_offbeat else 0.0

    # 2. Skew-normal genre groove offset
    groove_offset_ms = 0.0
    if genre == "synthwave" and metric_weight == 1.1: # Snare backbeat
        groove_offset_ms = -2.2 # Slight forward push
    elif genre == "lofi" and metric_weight == 1.1:
        groove_offset_ms = 18.0 # Laid-back drag

    jitter_sec = (groove_offset_ms / 1000.0) + random.gauss(0.0, timing_jitter_ms / 1000.0)
    adjusted_time = max(0.0, base_time + swing_offset + jitter_sec)

    # 3. Sigmoidal velocity dynamics
    metric_multiplier = 1.18 if metric_weight >= 1.0 else (0.92 if metric_weight >= 0.7 else 0.75)
    adjusted_vel = int(base_velocity * metric_multiplier + random.gauss(0.0, 3.5))
    adjusted_vel = max(15, min(127, adjusted_vel))

    return adjusted_time, adjusted_vel

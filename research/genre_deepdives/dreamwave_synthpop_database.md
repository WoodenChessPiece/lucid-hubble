# Dreamwave & Synthpop Harmonic Database: A Deep Dive

## Overview: The Nostalgic Engine
The core of Dreamwave, Outrun, and modern Synthpop (e.g., The Midnight, FM-84, Timecop1983, Gunship) relies heavily on a juxtaposition of triumphant major keys and melancholic yearning. This emotional complexity is largely driven by specific harmonic extensions, borrowed chords, and smooth voice leading that evokes nostalgia—a "remembered future."

## 1. Core Harmonic Vocabulary
The genre eschews basic triads in favor of lush, expanded voicings.

*   **Major 7ths (maj7) and Major 9ths (maj9):** The quintessential "dreamy" sound. The major 7th interval provides a wistful, slightly unresolved tension within a stable major chord.
*   **Added 9ths (add9):** Used to add brightness and a cinematic quality to major chords without the dominant or major 7th function.
*   **Suspended 2nds (sus2):** Creates an open, atmospheric sound, often used for pulsing synth pads or arpeggiated basslines to delay resolution.
*   **Minor iv Borrowing:** The most powerful tool for injecting melancholy into a major progression. Borrowing the minor four chord from the parallel minor key (e.g., in C Major, playing F minor instead of F major) creates a bittersweet, nostalgic pull back to the tonic.

## 2. Voice Leading & Descending Basslines
A hallmark of this style is the use of smooth, stepwise bass motion against relatively static upper structures.

### The "Nostalgia Walkdown" (I - V/7 - vi - IV)
This classic progression is given the Synthpop treatment through inversion and extensions.
*   **Key of C:** Cmaj7 -> G/B -> Am7 -> Fmaj7
*   **Emotional Effect:** The descending bassline (C -> B -> A) creates an inevitable, sinking feeling, counteracted by the uplifting upper notes. The slash chord (V/7) is crucial; it smoothes the transition from I to vi, making the progression feel like a single, sweeping gesture rather than separate chords.

## 3. Structural Progressions & JSON Presets

Below are JSON-structured arrays designed for consumption by algorithmic generation engines. The `notes` arrays reflect standard MIDI note values (Middle C = 60), voicing the chords for optimal spacing (often drop-2 or spread voicings for synth pads).

```json
{
  "genre": "Dreamwave_Synthpop",
  "bpm_range": [85, 115],
  "chord_dictionary": {
    "Cmaj9": {"type": "maj9", "notes": [48, 55, 64, 71, 74], "role": "Tonic_Lush"},
    "Fmaj7": {"type": "maj7", "notes": [53, 60, 65, 69, 72], "role": "Subdominant_Dreamy"},
    "Am11": {"type": "min11", "notes": [45, 52, 60, 64, 67, 74], "role": "Relative_Minor_Deep"},
    "Fm6": {"type": "min6", "notes": [53, 60, 65, 68, 74], "role": "Borrowed_Melancholy"},
    "G/B": {"type": "slash", "notes": [47, 55, 62, 67], "role": "Passing_Tension"}
  },
  "progressions": {
    "verse_brooding": {
      "description": "Atmospheric, unresolved movement relying on common tones.",
      "chords": [
        {"chord": "Am9", "duration_beats": 8, "voicing": [45, 52, 60, 64, 71]},
        {"chord": "Fmaj7(sus2)", "duration_beats": 8, "voicing": [41, 53, 60, 65, 67]}
      ],
      "roman_numeral": "vi - IV"
    },
    "pre_chorus_buildup": {
      "description": "Increasing tension leading into the triumphant chorus. Features the minor iv.",
      "chords": [
        {"chord": "Dm7", "duration_beats": 4, "voicing": [50, 57, 60, 65, 69]},
        {"chord": "Em7", "duration_beats": 4, "voicing": [52, 59, 62, 67, 71]},
        {"chord": "Fmaj7", "duration_beats": 4, "voicing": [53, 60, 65, 69, 72]},
        {"chord": "Fm6", "duration_beats": 4, "voicing": [53, 60, 65, 68, 74]}
      ],
      "roman_numeral": "ii - iii - IV - iv"
    },
    "chorus_anthem": {
      "description": "The soaring, nostalgic payoff with a descending bassline.",
      "chords": [
        {"chord": "Cmaj9", "duration_beats": 4, "voicing": [48, 55, 64, 71, 74]},
        {"chord": "G/B", "duration_beats": 4, "voicing": [47, 55, 62, 67]},
        {"chord": "Am11", "duration_beats": 4, "voicing": [45, 52, 60, 64, 67, 74]},
        {"chord": "Fmaj9", "duration_beats": 4, "voicing": [41, 53, 60, 65, 69, 72]}
      ],
      "roman_numeral": "I - V/7 - vi - IV"
    }
  }
}
```

## 4. Voice Leading Guidelines for Algorithms
To accurately reproduce the Dreamwave sound programmatically:
1.  **Pad Voicings:** Spread voicings (where intervals in the lower register are wider, e.g., root-fifth) are mandatory to prevent muddiness, especially with analog-style waveforms (saw/square).
2.  **Common Tone Retention:** When moving between chords (e.g., Am9 to Fmaj7), keep shared notes (C, E) in the same octave and voice to create a smooth, synthetic "gluing" effect.
3.  **Velocity:** Keep pad velocities consistent and low (40-60) to maintain a soft attack, utilizing slow filter sweeps (cutoff modulation) rather than velocity for dynamics.

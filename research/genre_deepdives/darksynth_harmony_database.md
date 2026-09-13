# Darksynth & Cyberpunk Harmonic Database

## 1. Theoretical Overview
Darksynth and Cyberpunk music rely heavily on aggressive, tension-filled harmonic structures. Unlike traditional synthwave which leans heavily on 80s pop tropes (major pentatonic, bright diatonic chords), darksynth draws from metal, horror film scores (e.g., John Carpenter, Goblin), and industrial music.

### Key Modalities:
- **Aeolian (Natural Minor):** The default canvas.
- **Phrygian / Phrygian Dominant:** Used for the signature "crunch" bII chord. The minor 2nd interval provides instant sinister tension.
- **Harmonic Minor:** Provides the leading tone (major VII or augmented 5th tension) over minor tonic chords.
- **Chromaticism & Tritones:** Frequent use of the diminished 5th / augmented 4th for horror/sci-fi dissonance.

### Chord Qualities:
- **Power Chords (Root-5th-Octave):** Used extensively in basslines and rhythm synths to avoid muddiness in heavy distortion.
- **Minor Triads / Minor 9ths:** Used in pads and arpeggios.
- **Diminished 7ths & Augmented 5ths:** Used as passing chords to build extreme tension before a heavy drop or resolution.

## 2. Machine-Readable Database (JSON)

The following JSON block contains structured data of signature progressions, tension formulas, and modal interchanges designed to be parsed by algorithmic generation engines.

```json
{
  "darksynth_harmony": {
    "version": "1.0",
    "primary_scales": [
      {
        "name": "Aeolian",
        "intervals": [0, 2, 3, 5, 7, 8, 10],
        "usage": "Base canvas for riffs and arpeggios."
      },
      {
        "name": "Phrygian Dominant",
        "intervals": [0, 1, 4, 5, 7, 8, 10],
        "usage": "Exotic, aggressive leads; provides the bII crunch."
      },
      {
        "name": "Harmonic Minor",
        "intervals": [0, 2, 3, 5, 7, 8, 11],
        "usage": "Gothic horror tension; V major to i minor cadences."
      }
    ],
    "progressions": [
      {
        "id": "prog_phrygian_crunch",
        "name": "The Carpenter bII Crunch",
        "roman_numerals": ["i", "bVI", "bII", "i"],
        "root_offsets_semitones": [0, 8, 1, 0],
        "chord_qualities": ["min", "maj", "maj", "min"],
        "voicings": ["power_chord", "power_chord", "power_chord", "power_chord"],
        "tension_level": "high",
        "description": "Signature darksynth progression. The bII (Phrygian) crashing down into the tonic creates immense, heavy tension."
      },
      {
        "id": "prog_cyberpunk_drive",
        "name": "Cyber_Drive_Ascent",
        "roman_numerals": ["i", "bIII", "iv", "bVI"],
        "root_offsets_semitones": [0, 3, 5, 8],
        "chord_qualities": ["min", "maj", "min", "maj"],
        "voicings": ["min_triad", "maj_triad", "min_triad", "maj_triad"],
        "tension_level": "medium",
        "description": "A driving, relentless progression often used with 16th note basslines for high-speed chase sequences."
      },
      {
        "id": "prog_horror_descent",
        "name": "Goblin's Descent",
        "roman_numerals": ["i", "V", "bVI", "V"],
        "root_offsets_semitones": [0, 7, 8, 7],
        "chord_qualities": ["min", "maj", "maj", "maj"],
        "voicings": ["min_add9", "maj_triad", "maj_triad", "maj_triad"],
        "tension_level": "extreme",
        "description": "Harmonic minor descent emphasizing the leading tone and the semitone clash between V and bVI."
      },
      {
        "id": "prog_tritone_sub",
        "name": "Tritone Hell",
        "roman_numerals": ["i", "bV", "iv", "V"],
        "root_offsets_semitones": [0, 6, 5, 7],
        "chord_qualities": ["power_chord", "diminished", "power_chord", "power_chord"],
        "voicings": ["power_chord", "dim_triad", "power_chord", "power_chord"],
        "tension_level": "extreme",
        "description": "Heavy use of the tritone (bV) for dissonant, jarring rhythmic stabs."
      }
    ],
    "modal_interchange": [
      {
        "target_chord": "bII",
        "borrowed_from": "Phrygian",
        "typical_resolution": "i",
        "effect": "Abrupt, aggressive downward resolution."
      },
      {
        "target_chord": "V (Major)",
        "borrowed_from": "Harmonic Minor",
        "typical_resolution": "i",
        "effect": "Strong classical/horror resolution."
      }
    ],
    "bassline_formulas": [
      {
        "type": "gallop",
        "pattern_16ths": [1, 0, 1, 1],
        "note_selection": ["root", "octave", "root", "root"],
        "description": "Standard metal-influenced galloping bassline."
      },
      {
        "type": "octave_pedal_tension",
        "pattern_16ths": [1, 1, 1, 1, 1, 1, 1, 1],
        "note_selection": ["root", "root", "root", "root", "root", "root", "b2", "root"],
        "description": "Relentless pedal point with a quick Phrygian passing tone for disruption."
      }
    ]
  }
}
```

# Arpeggiator & Counterpoint Database

## 1. Arpeggiator Modes & Behaviors
Arpeggiators (arps) dissect block chords into rhythmic, sequential monophonic lines, creating a sense of momentum and hypnotic depth. The choice of mode dictates the contour of the resulting sequence:
*   **Up**: Ascends from the lowest to the highest note. Creates an uplifting, propulsive feel.
*   **Down**: Descends from highest to lowest. Often feels grounding or slightly melancholic.
*   **Up-Down (Alt)**: Ascends then descends (and vice-versa). Creates a continuous wave or pendulum effect.
*   **Converge**: Plays the highest and lowest notes, working inward to the center of the chord. Creates a focusing, tightening sensation.
*   **Diverge**: Starts from the center notes and radiates outward to the extremes. Creates an expansive, opening texture.
*   **Random**: Selects notes from the held chord non-sequentially. Great for generative, unpredictable textures.
*   **As-Played (Chord-order)**: Triggers notes in the exact chronological sequence they were struck. Allows for custom rhythmic groupings.

## 2. Note Density & Rhythmic Subdivisions
The subdivision of the arpeggiator sets the fundamental pulse and genre-feel of the track:
*   **16th Notes**: The standard for trance, synthwave, and driving techno. Provides a relentless motoric pulse. When heavily sidechained, creates a pumping "breathing" effect.
*   **8th-Note Triplets**: Offers a rolling, swinging shuffle. Often used in cinematic scores or mid-tempo electronica to introduce triplet groove against a straight 4/4 beat.
*   **Dotted 8ths (The U2/Darksynth Feel)**: When an 8th note arp is combined with a dotted 8th delay (or the arp itself is programmed to dotted 8ths), it creates a cascading, syncopated polyrhythm against a 4/4 grid. This yields a massive sense of width and galloping momentum without adding actual note density.

## 3. Sculpting Tone: Filter Modulation & Gate Envelopes
To prevent rapid arpeggios from cluttering the mix and clashing with leads:
*   **Gate Time (Envelope Decay)**: Shortening the VCA/VCF decay creates a "plucky" staccato transient. A short gate (e.g., 20-40%) ensures silence between notes, preserving mix clarity. 
*   **Filter Modulation (Cutoff)**: Automating the low-pass filter cutoff is essential. By keeping the cutoff low during verses, the arp acts as a subtle rhythmic rumble. Opening the cutoff introduces upper harmonics, transitioning the arp into a focal element during choruses.
*   **Velocity to Filter/Amp**: Mapping velocity to cutoff or volume ensures the sequence breathes and has dynamic contour, rather than sounding like static machine-gun fire.

## 4. Obbligato Counter-Melodies
An obbligato counter-melody is an essential supporting line that interacts with the primary lead.
*   **Call and Response**: Counter-melodies should fill the structural gaps. When the lead plays rapid notes, the counter-melody holds sustained tones. When the lead rests or sustains a long note, the counter-melody becomes rhythmically active.
*   **Register Separation**: The counter-melody should occupy a different frequency bracket (typically lower) than the lead to avoid masking.
*   **Contrary Motion**: If the lead melody ascends, having the counter-melody descend creates maximum independence and harmonic interest.

## 5. Algorithmic Patterns & JSON Schemas

Below are 10 algorithmic rules/patterns modeled as JSON for programmatic music generation engines.

```json
{
  "arpeggiator_patterns": [
    {
      "id": "ARP_001",
      "name": "Classic 16th Trance Gate",
      "mode": "Up-Down",
      "subdivision": "1/16",
      "gate_percentage": 25,
      "octave_range": 2,
      "velocity_curve": "Accent on downbeats (127, 90, 100, 90)"
    },
    {
      "id": "ARP_002",
      "name": "Darksynth Gallop",
      "mode": "As-Played",
      "subdivision": "1/8",
      "delay_sync": "3/16 (Dotted 8th)",
      "gate_percentage": 50,
      "octave_range": 1,
      "filter_movement": "Slow upward ramp over 8 bars"
    },
    {
      "id": "ARP_003",
      "name": "Cinematic Triplet Roll",
      "mode": "Random",
      "subdivision": "1/8T",
      "gate_percentage": 80,
      "octave_range": 3,
      "velocity_curve": "Randomized (60-110) for humanization"
    },
    {
      "id": "ARP_004",
      "name": "Converging Focus",
      "mode": "Converge",
      "subdivision": "1/16",
      "gate_percentage": 40,
      "octave_range": 4,
      "note_behavior": "Pinches inward to root note"
    },
    {
      "id": "ARP_005",
      "name": "Expansive Divergence",
      "mode": "Diverge",
      "subdivision": "1/8",
      "gate_percentage": 60,
      "octave_range": 2,
      "note_behavior": "Blossoms outward from the third"
    }
  ],
  "counterpoint_rules": [
    {
      "id": "CPT_001",
      "name": "Gap Filler (Obbligato)",
      "trigger_condition": "Lead rests > 1 beat",
      "action": "Generate melodic fill in counter-voice",
      "interval_preference": ["3rd", "6th"]
    },
    {
      "id": "CPT_002",
      "name": "Contrary Motion Engine",
      "trigger_condition": "Lead moves > a perfect 4th in one direction",
      "action": "Move counter-voice in opposite direction by step",
      "interval_preference": ["Stepwise", "3rd"]
    },
    {
      "id": "CPT_003",
      "name": "Sustained Anchor",
      "trigger_condition": "Lead plays 16th notes",
      "action": "Hold whole notes on chord tones (Root or 5th)",
      "register_offset": "-1 Octave"
    },
    {
      "id": "CPT_004",
      "name": "Rhythmic Hocket",
      "trigger_condition": "Lead plays syncopated 8ths",
      "action": "Play on the exact off-beats of the lead",
      "velocity_mapping": "Match lead accentuation"
    },
    {
      "id": "CPT_005",
      "name": "Climax Harmonization",
      "trigger_condition": "Track intensity > 80%",
      "action": "Shadow lead melody in parallel 6ths",
      "rhythmic_density": "Match lead perfectly"
    }
  ]
}
```

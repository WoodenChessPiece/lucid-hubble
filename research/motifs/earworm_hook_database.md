# Earworm Hook & Lead Motif Database

## Anatomy of Electronic Music Hooks

Electronic music hooks that become instant earworms—characteristic of artists like Avicii, deadmau5, The Midnight, and Swedish House Mafia—rely on a balance between predictability and surprise. They exploit psychological principles of tension and release.

### 1. Rhythmic Syncopation: Offbeat vs. Downbeat
Earworms frequently utilize syncopation to drive momentum. While starting a motif on the strong downbeat (beat 1) establishes clear grounding (common in Swedish House Mafia's anthemic leads), starting on an offbeat (e.g., the "and" of 1 or 2) creates forward pull. Avicii often employed a mix: planting a strong root note on the downbeat, followed by heavily syncopated trailing notes that anticipate the chord changes.

### 2. Stepwise Conjunct Motion with Dramatic Leaps
Memorable melodies are primarily singable. They move in stepwise, conjunct motion (seconds and thirds) within a specific scale (often minor or pentatonic). However, the "hook" factor usually relies on a sudden, dramatic leap—most commonly a perfect 5th or a full octave. This leap acts as the emotional peak of the motif, common in deadmau5’s progressive house plucks, providing a sudden burst of energy against the otherwise smooth contour.

### 3. Call-and-Response Phrasing (4-Bar Microstructures)
A single 4-bar phrase typically contains its own micro-narrative. Bars 1-2 act as the "Call" (a rising or unresolved question), and Bars 3-4 act as the "Response" (a falling or resolved answer). The Midnight uses this heavily in synthwave, where a lush lead synth plays a motif, leaves space, and answers it with a slight variation in rhythm.

### 4. Repetition with Pitch Mutation on Bar 4
The golden rule of an earworm loop is A-A-A-B or A-B-A-C structure. The motif repeats identically for 3 bars (or 3 iterations), building familiarity. In the 4th bar, a "pitch mutation" occurs—the rhythm stays exactly the same, but the final notes shift to outline a dominant or subdominant chord, leading seamlessly back into Bar 1. This mutation is what keeps a looping 4-bar phrase from becoming fatiguing over a 6-minute track.

## 10 Masterclass Melodic Motifs (JSON Database)

```json
{
  "motifs": [
    {
      "id": "motif_001",
      "style": "Anthemic House (Avicii)",
      "bpm_range": [126, 128],
      "key": "F# minor",
      "rhythm_type": "Syncopated Offbeats",
      "notes": [
        { "pitch": "F#4", "start_beat": 1.0, "duration_beats": 0.5, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "A4", "start_beat": 1.75, "duration_beats": 0.25, "velocity": 85, "pitch_bend": 0 },
        { "pitch": "C#5", "start_beat": 2.25, "duration_beats": 0.5, "velocity": 110, "pitch_bend": 0 },
        { "pitch": "B4", "start_beat": 3.0, "duration_beats": 0.75, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "A4", "start_beat": 4.5, "duration_beats": 0.5, "velocity": 95, "pitch_bend": 0 }
      ]
    },
    {
      "id": "motif_002",
      "style": "Progressive Pluck (deadmau5)",
      "bpm_range": [128, 130],
      "key": "B minor",
      "rhythm_type": "Polyrhythmic 16ths",
      "notes": [
        { "pitch": "B3", "start_beat": 1.0, "duration_beats": 0.25, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "D4", "start_beat": 1.75, "duration_beats": 0.25, "velocity": 75, "pitch_bend": 0 },
        { "pitch": "F#4", "start_beat": 2.5, "duration_beats": 0.25, "velocity": 85, "pitch_bend": 0 },
        { "pitch": "B4", "start_beat": 3.25, "duration_beats": 0.25, "velocity": 120, "pitch_bend": 0 }
      ]
    },
    {
      "id": "motif_003",
      "style": "Synthwave Lead (The Midnight)",
      "bpm_range": [90, 110],
      "key": "Eb major",
      "rhythm_type": "Legato with Glide",
      "notes": [
        { "pitch": "Eb4", "start_beat": 1.0, "duration_beats": 1.5, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "F4", "start_beat": 2.5, "duration_beats": 0.5, "velocity": 80, "pitch_bend": 0 },
        { "pitch": "G4", "start_beat": 3.0, "duration_beats": 1.0, "velocity": 110, "pitch_bend": 2000 },
        { "pitch": "Bb4", "start_beat": 4.0, "duration_beats": 2.0, "velocity": 95, "pitch_bend": -1000 }
      ]
    },
    {
      "id": "motif_004",
      "style": "Festival Big Room (Swedish House Mafia)",
      "bpm_range": [125, 128],
      "key": "G minor",
      "rhythm_type": "Staccato Downbeats",
      "notes": [
        { "pitch": "G4", "start_beat": 1.0, "duration_beats": 0.25, "velocity": 127, "pitch_bend": 0 },
        { "pitch": "G4", "start_beat": 1.5, "duration_beats": 0.25, "velocity": 110, "pitch_bend": 0 },
        { "pitch": "D5", "start_beat": 2.0, "duration_beats": 0.5, "velocity": 127, "pitch_bend": 0 },
        { "pitch": "C5", "start_beat": 3.0, "duration_beats": 0.5, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "Bb4", "start_beat": 4.0, "duration_beats": 0.5, "velocity": 115, "pitch_bend": 0 }
      ]
    },
    {
      "id": "motif_005",
      "style": "Melancholy Pop-Dance",
      "bpm_range": [115, 122],
      "key": "C minor",
      "rhythm_type": "Call and Response",
      "notes": [
        { "pitch": "C5", "start_beat": 1.0, "duration_beats": 0.5, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "Eb5", "start_beat": 1.5, "duration_beats": 0.5, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "G5", "start_beat": 2.5, "duration_beats": 1.0, "velocity": 110, "pitch_bend": 500 },
        { "pitch": "F5", "start_beat": 4.5, "duration_beats": 0.5, "velocity": 85, "pitch_bend": 0 }
      ]
    },
    {
      "id": "motif_006",
      "style": "Deep House Chord-Lead",
      "bpm_range": [120, 124],
      "key": "A minor",
      "rhythm_type": "Dotted 8ths",
      "notes": [
        { "pitch": "A4", "start_beat": 1.0, "duration_beats": 0.75, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "E5", "start_beat": 1.75, "duration_beats": 0.75, "velocity": 110, "pitch_bend": 0 },
        { "pitch": "D5", "start_beat": 2.5, "duration_beats": 0.5, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "C5", "start_beat": 4.0, "duration_beats": 1.0, "velocity": 95, "pitch_bend": -500 }
      ]
    },
    {
      "id": "motif_007",
      "style": "Trance Arp (Classic)",
      "bpm_range": [135, 140],
      "key": "E minor",
      "rhythm_type": "Straight 16ths",
      "notes": [
        { "pitch": "E4", "start_beat": 1.0, "duration_beats": 0.25, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "G4", "start_beat": 1.25, "duration_beats": 0.25, "velocity": 80, "pitch_bend": 0 },
        { "pitch": "B4", "start_beat": 1.5, "duration_beats": 0.25, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "E5", "start_beat": 1.75, "duration_beats": 0.25, "velocity": 120, "pitch_bend": 0 }
      ]
    },
    {
      "id": "motif_008",
      "style": "Modern Tech House",
      "bpm_range": [126, 128],
      "key": "D minor",
      "rhythm_type": "Minimal Syncopation",
      "notes": [
        { "pitch": "D3", "start_beat": 1.5, "duration_beats": 0.25, "velocity": 110, "pitch_bend": 0 },
        { "pitch": "F3", "start_beat": 2.5, "duration_beats": 0.25, "velocity": 90, "pitch_bend": 0 },
        { "pitch": "D4", "start_beat": 4.5, "duration_beats": 0.5, "velocity": 127, "pitch_bend": -8192 }
      ]
    },
    {
      "id": "motif_009",
      "style": "Future Bass Glide",
      "bpm_range": [140, 160],
      "key": "F major",
      "rhythm_type": "Triplets & Glides",
      "notes": [
        { "pitch": "F4", "start_beat": 1.0, "duration_beats": 1.0, "velocity": 100, "pitch_bend": 0 },
        { "pitch": "A4", "start_beat": 2.33, "duration_beats": 0.33, "velocity": 90, "pitch_bend": 4096 },
        { "pitch": "C5", "start_beat": 3.0, "duration_beats": 1.5, "velocity": 110, "pitch_bend": 8192 }
      ]
    },
    {
      "id": "motif_010",
      "style": "Euphoric Hardstyle",
      "bpm_range": [150, 155],
      "key": "G# minor",
      "rhythm_type": "Anthemic Quarters & 8ths",
      "notes": [
        { "pitch": "G#4", "start_beat": 1.0, "duration_beats": 1.0, "velocity": 127, "pitch_bend": 0 },
        { "pitch": "D#5", "start_beat": 2.0, "duration_beats": 0.5, "velocity": 115, "pitch_bend": 0 },
        { "pitch": "C#5", "start_beat": 2.5, "duration_beats": 0.5, "velocity": 115, "pitch_bend": 0 },
        { "pitch": "B4", "start_beat": 3.0, "duration_beats": 1.0, "velocity": 120, "pitch_bend": 0 }
      ]
    }
  ]
}
```

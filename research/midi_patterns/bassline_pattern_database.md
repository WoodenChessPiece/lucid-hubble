# French Electro & Cyberpunk Bassline Database
**Prepared by Agent 3: The French Electro & Cyberpunk Bassline Specialist**

## Introduction

The French Electro and Cyberpunk music scenes are legendary for their driving, overdriven, and deeply syncopated basslines. Ranging from the disco-infused grooves of Daft Punk to the aggressive, heavily compressed distorted textures of Justice and SebastiAn, to the minimalist, relentless industrial drives of Gesaffelstein and Danger, the bassline is often the melodic and rhythmic anchor of the track.

This database provides an exhaustive analysis of 10 iconic bassline paradigms. Each paradigm includes deep theoretical context regarding its syncopation, playing style (or sequencing style), and a 16-step MIDI grid represented in JSON. 

### Understanding the 16-Step JSON Model

Each pattern represents 1 bar in 4/4 time, quantized to 16th notes.
*   **step**: 1 to 16 (representing 16th note subdivisions).
*   **active**: boolean (`true` if a note triggers on this step, `false` for a rest).
*   **velocity**: 0-127 (MIDI velocity, affecting filter cutoff and volume).
*   **gate_percent**: 0-100 (percentage of a 16th note duration. >100 implies legato/overlapping notes).
*   **pitch_offset**: Semitones relative to the root note of the bassline.
*   **octave_jump**: +1, 0, or -1 (frequently used for disco octave leaps).
*   **pitch_bend**: -8192 to 8191 (standard MIDI pitch bend scale, used for slides/glides).

---

## 1. The Classic French Touch Bounce (Inspired by Daft Punk - "Da Funk")
**Theory:** This groove relies on heavily swung 16th notes (though represented here in straight 16ths for standard grids, apply 55-60% swing in the DAW). The magic is in the ghost notes—low velocity, short gate notes that create a "bouncing" feel before the main downbeats. It utilizes a resonant low-pass filter envelope where higher velocities open the filter more.

```json
{
  "name": "Classic French Touch Bounce",
  "tempo": 112,
  "root_note": "G1",
  "swing": 58,
  "pattern": [
    { "step": 1, "active": true, "velocity": 110, "gate_percent": 80, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 60, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": true, "velocity": 100, "gate_percent": 60, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 5, "active": true, "velocity": 115, "gate_percent": 75, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 70, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": true, "velocity": 105, "gate_percent": 90, "pitch_offset": 5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 9, "active": true, "velocity": 120, "gate_percent": 70, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 80, "gate_percent": 50, "pitch_offset": 0, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 90, "gate_percent": 50, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 13, "active": true, "velocity": 110, "gate_percent": 80, "pitch_offset": -5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": false },
    { "step": 15, "active": true, "velocity": 85, "gate_percent": 40, "pitch_offset": -5, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 16, "active": true, "velocity": 95, "gate_percent": 60, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 }
  ]
}
```

## 2. The Overdriven Slap (Inspired by Justice - "Genesis")
**Theory:** Emulating a heavily compressed, distorted slap bass guitar played through a synthesizer. The pattern relies heavily on octave jumps (popping) and root-fifth movements. The gates are incredibly short on the upbeats (pops) and longer on the downbeats (slaps). Extreme velocity dynamics are compressed flat, using velocity solely to drive a distortion saturation curve rather than volume.

```json
{
  "name": "Overdriven Slap",
  "tempo": 108,
  "root_note": "E1",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 60, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 110, "gate_percent": 25, "pitch_offset": 0, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 4, "active": false },
    { "step": 5, "active": true, "velocity": 120, "gate_percent": 50, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": true, "velocity": 115, "gate_percent": 25, "pitch_offset": 3, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 7, "active": true, "velocity": 90, "gate_percent": 20, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": true, "velocity": 127, "gate_percent": 40, "pitch_offset": 5, "octave_jump": 0, "pitch_bend": -2000 },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 75, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 120, "gate_percent": 30, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 100, "gate_percent": 25, "pitch_offset": 7, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 13, "active": true, "velocity": 115, "gate_percent": 50, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": true, "velocity": 105, "gate_percent": 30, "pitch_offset": -2, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 15, "active": true, "velocity": 127, "gate_percent": 60, "pitch_offset": 10, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": false }
  ]
}
```

## 3. The Industrial Rolling 16ths (Inspired by Gesaffelstein - "Pursuit")
**Theory:** Pure techno aggression. This pattern is a continuous stream of 16th notes. The "groove" is created entirely through micro-velocity changes, subtle filter modulation on every 4th step, and pitch slides. It feels relentless. It uses strict quantization (no swing) to sound mechanical.

```json
{
  "name": "Industrial Rolling 16ths",
  "tempo": 105,
  "root_note": "F1",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": true, "velocity": 90, "gate_percent": 80, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 3, "active": true, "velocity": 110, "gate_percent": 85, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": true, "velocity": 100, "gate_percent": 80, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 5, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": true, "velocity": 90, "gate_percent": 80, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 7, "active": true, "velocity": 110, "gate_percent": 110, "pitch_offset": -1, "octave_jump": 0, "pitch_bend": 2000 },
    { "step": 8, "active": true, "velocity": 95, "gate_percent": 80, "pitch_offset": -1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": true, "velocity": 90, "gate_percent": 80, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 11, "active": true, "velocity": 110, "gate_percent": 85, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 100, "gate_percent": 80, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 13, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": 1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": true, "velocity": 115, "gate_percent": 80, "pitch_offset": 1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 15, "active": true, "velocity": 120, "gate_percent": 95, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": -4000 },
    { "step": 16, "active": true, "velocity": 105, "gate_percent": 75, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 }
  ]
}
```

## 4. The Disco Syncopation (Inspired by Daft Punk - "Around The World")
**Theory:** Based heavily on classic Chic/Bernard Edwards basslines. The notes almost never hit on the '2' or '4' snare drums, heavily emphasizing the 'e' and 'a' 16th subdivisions (steps 2, 4, 6, 8, etc.). The gates are round, typically around 50-70% for standard notes, allowing the kick and snare to breathe in the gaps.

```json
{
  "name": "Disco Syncopation",
  "tempo": 121,
  "root_note": "E1",
  "swing": 54,
  "pattern": [
    { "step": 1, "active": true, "velocity": 120, "gate_percent": 70, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 95, "gate_percent": 50, "pitch_offset": 0, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 4, "active": true, "velocity": 110, "gate_percent": 60, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 5, "active": false },
    { "step": 6, "active": true, "velocity": 105, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 7, "active": true, "velocity": 127, "gate_percent": 75, "pitch_offset": 5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": true, "velocity": 100, "gate_percent": 50, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 9, "active": false },
    { "step": 10, "active": true, "velocity": 110, "gate_percent": 60, "pitch_offset": -5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 11, "active": true, "velocity": 105, "gate_percent": 60, "pitch_offset": -5, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 12, "active": false },
    { "step": 13, "active": true, "velocity": 115, "gate_percent": 50, "pitch_offset": -7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": true, "velocity": 120, "gate_percent": 70, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 15, "active": false },
    { "step": 16, "active": true, "velocity": 90, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 }
  ]
}
```

## 5. Micro-Chopped Funk (Inspired by SebastiAn - "Walkman")
**Theory:** This approach stems from chopping up funk samples. The MIDI pattern reflects an MPC-style trigger sequence where bass notes stutter rapidly, halt abruptly, and switch pitches in ways a live player couldn't physically manage. Very short gate times and high velocities to punch through heavy bitcrushing and distortion.

```json
{
  "name": "Micro-Chopped Funk",
  "tempo": 118,
  "root_note": "A1",
  "swing": 60,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 25, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": true, "velocity": 110, "gate_percent": 25, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 3, "active": true, "velocity": 127, "gate_percent": 50, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": false },
    { "step": 5, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 127, "gate_percent": 80, "pitch_offset": 5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": false },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 20, "pitch_offset": -7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": true, "velocity": 115, "gate_percent": 20, "pitch_offset": -5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 11, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": -4096 },
    { "step": 12, "active": false },
    { "step": 13, "active": true, "velocity": 127, "gate_percent": 40, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": true, "velocity": 100, "gate_percent": 30, "pitch_offset": 10, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 15, "active": true, "velocity": 127, "gate_percent": 40, "pitch_offset": 12, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": false }
  ]
}
```

## 6. Punk Distortion Square Wave (Inspired by Justice - "Waters of Nazareth")
**Theory:** This bassline is essentially a distorted, overdriven lead synth played in the bass register. The gates are almost 100% (legato) ensuring a wall of sound, overlapping slightly to trigger portamento slides on key intervals. It relies on minor scales and tritone dissonance.

```json
{
  "name": "Punk Distortion Square Wave",
  "tempo": 123,
  "root_note": "D1",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": false },
    { "step": 5, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 127, "gate_percent": 110, "pitch_offset": 6, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": false },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 127, "gate_percent": 50, "pitch_offset": -4, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 13, "active": false },
    { "step": 14, "active": true, "velocity": 127, "gate_percent": 50, "pitch_offset": -5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 15, "active": true, "velocity": 127, "gate_percent": 105, "pitch_offset": -7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": false }
  ]
}
```

## 7. Synthwave Pulsing 8ths (Inspired by Kavinsky - "Nightcall")
**Theory:** The backbone of synthwave. A repeating sequence of 8th notes, strictly on the grid. The dynamic movement comes entirely from sidechain compression (ducking on the 1, 5, 9, 13 steps for the kick drum) rather than MIDI velocity. Filter cutoff is modulated over 8 or 16 bars via a macro, while the pattern remains static.

```json
{
  "name": "Synthwave Pulsing 8ths",
  "tempo": 90,
  "root_note": "A0",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": false },
    { "step": 5, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": false },
    { "step": 9, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": false },
    { "step": 13, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": false },
    { "step": 15, "active": true, "velocity": 100, "gate_percent": 90, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": false }
  ]
}
```

## 8. Tension Drill 16ths (Inspired by Justice - "Stress")
**Theory:** Designed to induce anxiety. Stabbing, high-resonance, short-gate 16th notes that repeat relentlessly, ascending minor scales in a chromatic and dissonant fashion. High velocities trigger harsh FM or ring-modulation layers.

```json
{
  "name": "Tension Drill 16ths",
  "tempo": 115,
  "root_note": "F1",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 3, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 5, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 7, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 6, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": true, "velocity": 120, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 11, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 1, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 13, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": true, "velocity": 120, "gate_percent": 30, "pitch_offset": 6, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 15, "active": true, "velocity": 127, "gate_percent": 30, "pitch_offset": 8, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": true, "velocity": 110, "gate_percent": 30, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 }
  ]
}
```

## 9. Cyberpunk Off-Beat Drive (Inspired by Gesaffelstein - "Opr")
**Theory:** The backbone of dark electro. Heavily emphasizing the 'and' of the beat (steps 3, 7, 11, 15). The kick hits on the quarter notes, while the bass fills the space precisely between them with long, sustained 16th notes that crash into the next kick. Very stark, brutalist arrangement.

```json
{
  "name": "Cyberpunk Off-Beat Drive",
  "tempo": 100,
  "root_note": "F1",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 80, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": false },
    { "step": 3, "active": true, "velocity": 127, "gate_percent": 100, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": false },
    { "step": 5, "active": true, "velocity": 80, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 127, "gate_percent": 100, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": false },
    { "step": 9, "active": true, "velocity": 80, "gate_percent": 40, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 127, "gate_percent": 100, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 12, "active": false },
    { "step": 13, "active": true, "velocity": 80, "gate_percent": 40, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": false },
    { "step": 15, "active": true, "velocity": 127, "gate_percent": 100, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": false }
  ]
}
```

## 10. Chiptune-Infused Electro (Inspired by Danger - "11h30")
**Theory:** Blending video game aesthetic (fast arpeggios, tight pulses) with heavy electro beats. The pattern features rapid 32nd-note flourishes (represented here via pitch bend sweeps and octave jumps on 16ths to simulate the trill). Strict quantize, 50% pulse width, minimal filter envelope, heavy reliance on pitch jumps.

```json
{
  "name": "Chiptune-Infused Electro",
  "tempo": 107,
  "root_note": "C2",
  "swing": 50,
  "pattern": [
    { "step": 1, "active": true, "velocity": 127, "gate_percent": 75, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 2, "active": true, "velocity": 100, "gate_percent": 50, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 3, "active": true, "velocity": 127, "gate_percent": 80, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 4, "active": true, "velocity": 115, "gate_percent": 50, "pitch_offset": 0, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 5, "active": true, "velocity": 127, "gate_percent": 75, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 6, "active": false },
    { "step": 7, "active": true, "velocity": 110, "gate_percent": 50, "pitch_offset": -2, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 8, "active": true, "velocity": 120, "gate_percent": 50, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": -8192 },
    { "step": 9, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": -5, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 10, "active": false },
    { "step": 11, "active": true, "velocity": 127, "gate_percent": 40, "pitch_offset": -5, "octave_jump": 1, "pitch_bend": 0 },
    { "step": 12, "active": true, "velocity": 115, "gate_percent": 40, "pitch_offset": -5, "octave_jump": 2, "pitch_bend": 0 },
    { "step": 13, "active": true, "velocity": 127, "gate_percent": 90, "pitch_offset": 0, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 14, "active": false },
    { "step": 15, "active": true, "velocity": 100, "gate_percent": 50, "pitch_offset": 3, "octave_jump": 0, "pitch_bend": 0 },
    { "step": 16, "active": true, "velocity": 110, "gate_percent": 50, "pitch_offset": 7, "octave_jump": 0, "pitch_bend": 0 }
  ]
}
```

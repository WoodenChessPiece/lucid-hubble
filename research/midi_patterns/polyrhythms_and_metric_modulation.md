# Polyrhythms & Metric Modulation: Hypnotic Groove Mechanics

## Overview
In electronic dance music, a relentless 4/4 kick drum forms the anchor. Polyrhythms and metric modulations create hypnotic, evolving grooves by superimposing contrasting subdivisions—such as 3-against-4, dotted notes, and prime-number phases—over this anchor. Artists like deadmau5, Jon Hopkins, Bicep, and Bonobo utilize these techniques to generate tension, momentum, and complex polyphonic textures without losing the dancefloor pulse.

## 1. Dotted 8th-Note Lead Patterns Against 4/4 Kicks
A dotted 8th-note occupies three 16th-notes. When played over a 4/4 beat (where the kick hits every four 16th-notes), the pattern creates a 3/16 repeating cycle. Because 3 and 16 share no common divisors other than 1, the pattern will shift its relationship to the downbeat, finally resolving back to the "one" after exactly 3 bars (48 sixteenth notes). This creates an algorithmic, phasing effect typical in progressive house and techno.

## 2. Hemiolas and 3:2 Polyrhythms in Hi-Hat Patterns
A hemiola or a 3:2 polyrhythm occurs when three evenly spaced notes are played in the time of two. In electronic music, this is often manifested by grouping 16th notes into blocks of three against the steady duple meter. Hi-hat patterns exploiting 3:2 or 3:4 relationships inject a triplet feel into a straight 4/4 grid, producing a swinging, organic groove that feels constantly in motion.

## 3. Polyrhythmic Basslines
Polyrhythmic basslines use odd groupings (e.g., 5/16, 7/16, or 3/8) against standard drum grooves. A 5/16 bassline looping over a 4/4 drum pattern creates a phase shift where the bassline's starting note lands on a different 16th note each measure, resolving every 5 bars. This injects long-form generative evolution into short loop-based music.

---

## 8 Polyrhythmic Groove Blueprints

Below are 8 groove blueprints with JSON MIDI timing arrays (values denote 16th-note grid positions, 0-indexed, where a standard 4/4 bar is 0, 1, 2... 15).

### 1. Dotted 8th-Note Lead vs 4/4 Kick (3-Bar Cycle)
```json
{
  "name": "Dotted 8th Lead",
  "length_16ths": 48,
  "kick_pattern": [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44],
  "lead_pattern": [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45]
}
```

### 2. 3:2 Hi-Hat Hemiola (1-Bar Cycle)
```json
{
  "name": "3:2 Hi-Hat Hemiola",
  "length_16ths": 16,
  "kick_pattern": [0, 4, 8, 12],
  "hihat_pattern": [0, 3, 6, 8, 11, 14]
}
```

### 3. 5/16 Bassline Phase (5-Bar Cycle)
```json
{
  "name": "5/16 Bassline",
  "length_16ths": 80,
  "kick_pattern": [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76],
  "bass_pattern": [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
}
```

### 4. 7/16 Arpeggio vs 4/4 (7-Bar Cycle)
```json
{
  "name": "7/16 Arpeggio",
  "length_16ths": 112,
  "kick_pattern_interval": 4,
  "arp_pattern_interval": 7
}
```

### 5. 3-Against-4 Synth Chords (1-Bar Cycle)
```json
{
  "name": "3-against-4 Chords",
  "length_16ths": 16,
  "kick_pattern": [0, 4, 8, 12],
  "chord_pattern": [0, 5, 10]
}
```

### 6. Metric Modulation Transition (4/4 to 6/8 Feel)
```json
{
  "name": "Metric Mod Transition",
  "length_16ths": 32,
  "bar1_4_4_drums": [0, 4, 8, 12],
  "bar2_implied_6_8_kick": [16, 21, 26],
  "bar2_implied_6_8_snare": [21, 29]
}
```

### 7. 3/8 Bass vs 4/4 Drums (3-Bar Cycle)
```json
{
  "name": "3/8 Bass",
  "length_16ths": 48,
  "kick_pattern": [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44],
  "bass_pattern": [0, 6, 12, 18, 24, 30, 36, 42]
}
```

### 8. 5:4 Polyrhythmic Percussion (1-Bar Cycle)
```json
{
  "name": "5:4 Percussion",
  "length_16ths": 16,
  "kick_pattern": [0, 4, 8, 12],
  "percussion_pattern": [0, 3.2, 6.4, 9.6, 12.8]
}
```

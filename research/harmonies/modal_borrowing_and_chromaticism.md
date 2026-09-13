# Research Report: Modal Borrowing & Chromaticism in Electronic Music
**Author**: Agent 16, Melodic Voice Leading & Modal Borrowing Specialist

This document explores advanced modal interchange and chromatic passing chords, providing a structured knowledge base for programmatic music generation engines. The following structures demonstrate how to employ these concepts effectively in electronic music genres ranging from Synthwave to Cinematic Bass.

## 1. Minor iv in Major Cadences
The borrowing of the minor iv chord from the parallel minor is a staple of emotional resonance. Found in the works of The Beatles, The Midnight, and Porter Robinson, the iv chord contains the `b6` degree, which resolves downward by a half-step to the `5` of the I chord, creating profound yearning.

## 2. The Neapolitan Chord (bII Major Triad)
The Neapolitan chord functions predominantly as a pre-dominant in minor keys. Built on the lowered second degree, it offers a dramatic, heroic tension, often resolving to the V chord. This creates a striking cinematic transition before a heavy drop or climactic chorus.

## 3. The Andalusian Cadence (i - bVII - bVI - V)
Rooted in Flamenco music, this descending tetrachord progression brings an inevitable, fatalistic momentum. In Synthwave and Darkwave crossovers, driving this progression with a pulsing 16th-note bassline over four-on-the-floor drums transforms it into a powerful dancefloor sequence. 

## 4. Chromatic Mediant Modulations
Moving by a major or minor third where chords share at least one common tone but belong to different keys. Examples include C Major to Ab Major (sharing C) or D Minor to Bb Minor (sharing F). These modulations immediately shift the emotional landscape, ideal for contrasting verse and chorus sections.

## Programmatic Models: 10 Concrete Progressions

Below are JSON schemas defining 10 progressions utilizing these concepts, complete with Drop-2 and Drop-4 voicing coordinates to ensure optimal voice leading.

```json
[
  {
    "id": "PROG_01",
    "name": "Classic Minor iv Cadence",
    "concept": "Minor iv in Major",
    "key": "C Major",
    "progression": ["I", "IV", "iv", "I"],
    "chords": ["Cmaj7", "Fmaj7", "Fmin7", "Cmaj7"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [48, 55, 59, 64],
        [53, 60, 64, 69],
        [53, 60, 63, 68],
        [48, 55, 59, 64]
      ]
    }
  },
  {
    "id": "PROG_02",
    "name": "Porter's Plaintive iv",
    "concept": "Minor iv in Major",
    "key": "Db Major",
    "progression": ["vi", "IV", "iv", "I"],
    "chords": ["Bbmin7", "Gbmaj7", "Gbmin6", "Dbmaj7"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [46, 53, 56, 61],
        [42, 53, 58, 61],
        [42, 54, 57, 61],
        [49, 53, 56, 60]
      ]
    }
  },
  {
    "id": "PROG_03",
    "name": "Neapolitan Pre-Dominant Drop",
    "concept": "Neapolitan bII",
    "key": "A Minor",
    "progression": ["i", "VI", "bII", "V7"],
    "chords": ["Amin9", "Fmaj7", "Bbmaj", "E7(#9)"],
    "voicings": {
      "style": "Drop-4",
      "midi_intervals": [
        [33, 52, 57, 60, 64],
        [29, 53, 57, 60, 64],
        [34, 53, 58, 62],
        [28, 56, 59, 62, 67]
      ]
    }
  },
  {
    "id": "PROG_04",
    "name": "Heroic Minor Neapolitan Shift",
    "concept": "Neapolitan bII",
    "key": "D Minor",
    "progression": ["i", "bII/FirstInversion", "V", "i"],
    "chords": ["Dmin", "Eb/G", "A7", "Dmin"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [50, 57, 62, 65],
        [55, 63, 67, 70],
        [45, 57, 61, 64],
        [50, 57, 62, 65]
      ]
    }
  },
  {
    "id": "PROG_05",
    "name": "Darkwave Andalusian",
    "concept": "Andalusian Cadence",
    "key": "E Minor",
    "progression": ["i", "bVII", "bVI", "V"],
    "chords": ["Emin", "Dmaj", "Cmaj", "Bmaj"],
    "voicings": {
      "style": "Drop-4",
      "midi_intervals": [
        [40, 59, 64, 67],
        [38, 57, 62, 66],
        [36, 55, 60, 64],
        [35, 54, 59, 63]
      ]
    }
  },
  {
    "id": "PROG_06",
    "name": "Synthwave Extended Andalusian",
    "concept": "Andalusian Cadence",
    "key": "C Minor",
    "progression": ["i7", "bVII7", "bVImaj7", "Vsus4"],
    "chords": ["Cmin7", "Bb7", "Abmaj7", "Gsus4"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [48, 55, 58, 63],
        [46, 53, 58, 62],
        [44, 55, 58, 63],
        [43, 55, 57, 60]
      ]
    }
  },
  {
    "id": "PROG_07",
    "name": "Cinematic Major Mediant Shift",
    "concept": "Chromatic Mediant",
    "key": "C Major to Ab Major",
    "progression": ["I", "vi", "bVI", "bIImaj7"],
    "chords": ["Cmaj", "Amin", "Abmaj", "Dbmaj7"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [48, 55, 60, 64],
        [45, 52, 57, 60],
        [44, 51, 56, 60],
        [49, 53, 58, 63]
      ]
    }
  },
  {
    "id": "PROG_08",
    "name": "Epic Minor Mediant Drop",
    "concept": "Chromatic Mediant",
    "key": "D Minor to Bb Minor",
    "progression": ["i", "iv", "bvi", "bII"],
    "chords": ["Dmin", "Gmin", "Bbmin", "Ebmaj"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [50, 57, 62, 65],
        [55, 62, 67, 70],
        [58, 65, 70, 73],
        [63, 70, 75, 79]
      ]
    }
  },
  {
    "id": "PROG_09",
    "name": "Parallel Mediant Exploration",
    "concept": "Chromatic Mediant",
    "key": "E Major to C Major",
    "progression": ["I", "iii", "bVI", "V"],
    "chords": ["Emaj", "G#min", "Cmaj", "Bmaj"],
    "voicings": {
      "style": "Drop-4",
      "midi_intervals": [
        [40, 59, 64, 68],
        [44, 59, 63, 68],
        [36, 55, 60, 64],
        [35, 54, 59, 63]
      ]
    }
  },
  {
    "id": "PROG_10",
    "name": "Hybrid Modal Interlude",
    "concept": "Compound Borrowing",
    "key": "F Major",
    "progression": ["I", "iv", "bVI", "bII"],
    "chords": ["Fmaj7", "Bbmin7", "Dbmaj7", "Gbmaj7"],
    "voicings": {
      "style": "Drop-2",
      "midi_intervals": [
        [53, 60, 65, 69],
        [46, 53, 58, 61],
        [49, 56, 60, 65],
        [54, 61, 66, 70]
      ]
    }
  }
]
```

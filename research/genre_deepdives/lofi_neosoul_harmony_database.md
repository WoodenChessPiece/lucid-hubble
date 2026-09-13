# Lo-Fi Chill & Neo-Soul Harmony Database

## 1. Extended Jazz Chords in Lo-Fi and Neo-Soul
Lo-Fi and Neo-Soul extensively utilize extended harmony to create warmth, color, and emotional ambiguity.
- **min9 and maj9**: The foundation of the genre. Adding the 7th and 9th creates a rich, complex sonority that softens the triad.
- **11ths (min11, maj11, dom11)**: Provide a suspended, unresolved feeling, perfect for "chill" loops.
- **13ths (dom13, maj13)**: Often used in dominant functioning chords or lush major tonalities.
- **dim7 Passing Chords**: Used to smoothly connect diatonic chords, usually moving up or down by a half step (e.g., ii9 - #ii°7 - iii7).

## 2. Secondary Dominants and Tritone Substitutions
- **Secondary Dominants (V/ii, V/V)**: Adding a dominant 7th chord that resolves down a fifth to a diatonic chord. For instance, in C major, an A7 (V/ii) leading to Dmin9.
- **Tritone Substitutions (subV7)**: Replacing a dominant chord with another dominant chord a tritone away (e.g., Db7 replacing G7 to resolve to Cmaj9). This creates a descending chromatic bassline (e.g., Dmin9 - Db9 - Cmaj9).

## 3. The Minor Subdominant Cadence and Modal Borrowing
- **I - iv - I**: The "nostalgic" progression. Borrowing the minor iv from the parallel minor (e.g., Cmaj9 - Fmin9 - Cmaj9).
- **Modal Interchange**: Incorporating chords from other modes (like Dorian or Aeolian) while in a major key adds a bittersweet, melancholy flavor.

## 10 Lo-Fi / Neo-Soul Chord Progressions

### Progression 1: The Classic 2-5-1 (with extensions)
**Chords:** Dmin9 | G13 | Cmaj9 | A7(b13)
**Analysis:** ii - V - I - V/ii. The A7(b13) smoothly leads back to the Dmin9.
**JSON Preset:**
```json
{
  "name": "Classic 2-5-1 Lo-Fi",
  "bpm": 75,
  "chords": [
    { "name": "Dmin9", "voicing": [60, 65, 69, 72, 76] },
    { "name": "G13", "voicing": [55, 65, 71, 76, 77] },
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "A7(b13)", "voicing": [57, 61, 67, 70, 77] }
  ]
}
```

### Progression 2: The Minor Subdominant (Nostalgia)
**Chords:** Fmaj9 | Fmin9 | Cmaj9 | Cmaj9
**Analysis:** IV - iv - I. Classic bittersweet resolution.
**JSON Preset:**
```json
{
  "name": "Minor Subdominant Nostalgia",
  "bpm": 80,
  "chords": [
    { "name": "Fmaj9", "voicing": [53, 60, 65, 69, 72] },
    { "name": "Fmin9", "voicing": [53, 60, 63, 68, 72] },
    { "name": "Cmaj9", "voicing": [48, 55, 64, 67, 71] },
    { "name": "Cmaj9", "voicing": [48, 55, 64, 67, 71] }
  ]
}
```

### Progression 3: Tritone Sub Walkdown
**Chords:** Emin9 | Eb9 | Dmin9 | Db9
**Analysis:** iii - subV/ii - ii - subV/I. Chromatic descending bass.
**JSON Preset:**
```json
{
  "name": "Tritone Walkdown",
  "bpm": 78,
  "chords": [
    { "name": "Emin9", "voicing": [52, 59, 62, 67, 71] },
    { "name": "Eb9", "voicing": [51, 57, 61, 65, 68] },
    { "name": "Dmin9", "voicing": [50, 57, 60, 65, 69] },
    { "name": "Db9", "voicing": [49, 56, 59, 63, 68] }
  ]
}
```

### Progression 4: Neo-Soul Turnaround
**Chords:** Cmaj9 | Bmin11 E7(b9) | Amin11 | D13
**Analysis:** I - vii - V/vi - vi - V/V. Very smooth voice leading.
**JSON Preset:**
```json
{
  "name": "Neo-Soul Turnaround",
  "bpm": 72,
  "chords": [
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "Bmin11", "voicing": [59, 66, 69, 74, 76] },
    { "name": "E7(b9)", "voicing": [52, 64, 68, 74, 77] },
    { "name": "Amin11", "voicing": [57, 64, 67, 72, 74] },
    { "name": "D13", "voicing": [50, 60, 66, 71, 74] }
  ]
}
```

### Progression 5: Diminished Passing
**Chords:** Dmin9 | D#dim7 | Emin7 | A7(alt)
**Analysis:** ii - #ii°7 - iii - V/ii. The diminished chord acts as a bridge.
**JSON Preset:**
```json
{
  "name": "Diminished Passing",
  "bpm": 82,
  "chords": [
    { "name": "Dmin9", "voicing": [50, 65, 69, 72, 76] },
    { "name": "D#dim7", "voicing": [51, 63, 66, 69, 75] },
    { "name": "Emin7", "voicing": [52, 64, 67, 71, 74] },
    { "name": "A7(alt)", "voicing": [57, 61, 65, 70, 75] }
  ]
}
```

### Progression 6: Constant Structure (Parallelism)
**Chords:** Abmaj9 | Gmaj9 | Gbmaj9 | Fmaj9
**Analysis:** Sliding down in major 9ths. Very floaty and disconnected.
**JSON Preset:**
```json
{
  "name": "Parallel Float",
  "bpm": 70,
  "chords": [
    { "name": "Abmaj9", "voicing": [56, 63, 68, 72, 75] },
    { "name": "Gmaj9", "voicing": [55, 62, 67, 71, 74] },
    { "name": "Gbmaj9", "voicing": [54, 61, 66, 70, 73] },
    { "name": "Fmaj9", "voicing": [53, 60, 65, 69, 72] }
  ]
}
```

### Progression 7: Modal Borrowing (Aeolian)
**Chords:** Cmaj9 | Abmaj7 | Bbmaj7 | Cmaj9
**Analysis:** I - bVI - bVII - I. Epic, cinematic resolve used in Neo-Soul choruses.
**JSON Preset:**
```json
{
  "name": "Aeolian Borrowing",
  "bpm": 76,
  "chords": [
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "Abmaj7", "voicing": [56, 63, 68, 72, 75] },
    { "name": "Bbmaj7", "voicing": [58, 65, 70, 74, 77] },
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] }
  ]
}
```

### Progression 8: Phrygian Flavor
**Chords:** Cmaj9 | Dbmaj9 | Cmaj9 | Dbmaj9
**Analysis:** I - bII. Gives a slightly Spanish/Phrygian edge but keeps the major qualities.
**JSON Preset:**
```json
{
  "name": "Phrygian Major Float",
  "bpm": 85,
  "chords": [
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "Dbmaj9", "voicing": [49, 65, 68, 72, 75] },
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "Dbmaj9", "voicing": [49, 65, 68, 72, 75] }
  ]
}
```

### Progression 9: Sus Chord Ambiguity
**Chords:** Fmaj7 | Gsus4 | Esus4 | Asus4
**Analysis:** Creates a very open, unresolved atmosphere typical of ambient Lo-Fi.
**JSON Preset:**
```json
{
  "name": "Sus Ambiguity",
  "bpm": 74,
  "chords": [
    { "name": "Fmaj7", "voicing": [53, 65, 69, 72, 76] },
    { "name": "Gsus4", "voicing": [55, 65, 67, 72, 77] },
    { "name": "Esus4", "voicing": [52, 64, 69, 74, 76] },
    { "name": "Asus4", "voicing": [57, 69, 74, 76, 81] }
  ]
}
```

### Progression 10: The Dilla Offset (8-bar)
**Chords:** 
Bar 1-2: Dmin11 | G7(#9)
Bar 3-4: Cmaj9 | A7(b13)
Bar 5-6: Dmin11 | Db13
Bar 7-8: Cmaj9 | Bb13 A13
**Analysis:** Extended progression featuring tritone subs, altered dominants, and a very Dilla-esque turnaround at the end.
**JSON Preset:**
```json
{
  "name": "Dilla Offset",
  "bpm": 86,
  "chords": [
    { "name": "Dmin11", "voicing": [50, 65, 69, 72, 76] },
    { "name": "G7(#9)", "voicing": [55, 65, 71, 74, 75] },
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "A7(b13)", "voicing": [57, 61, 67, 70, 77] },
    { "name": "Dmin11", "voicing": [50, 65, 69, 72, 76] },
    { "name": "Db13", "voicing": [49, 63, 68, 73, 75] },
    { "name": "Cmaj9", "voicing": [48, 64, 67, 71, 74] },
    { "name": "Bb13", "voicing": [46, 62, 68, 72, 74] }
  ]
}
```

# Masterclass Harmonic Structures: Synthwave, Darksynth, and Cinematic Electronic

This document serves as an exhaustive reference for the harmonic language, chord formulas, and voice leading principles utilized in top-tier electronic music production (Synthwave, Darksynth, Cinematic).

## 1. Masterworks Harmonic Analysis

### Kavinsky
*   **Nightcall (F Aeolian / minor):**
    *   **Progression:** `i - VI - III - VII` (Fm - Db - Ab - Eb).
    *   **Analysis:** This is the quintessential "epic minor" progression. It cycles through the relative major (Ab) before returning via the V-substitute (Eb / VII) to the tonic, evoking a tragic but heroic narrative loop.
*   **Pacific Coast Highway (D Aeolian):**
    *   **Progression:** `i - v - VI - iv` (Dm - Am - Bb - Gm).
    *   **Analysis:** Emphasizes subdominant motion, creating a continuous, driving "highway" feel without a strong authentic cadence.

### The Midnight
*   **Sunset (C# minor / E Major):**
    *   **Progression:** `VImaj7 - VII - i - III` (Amaj7 - B - C#m - E) or functionally in Major: `IVmaj7 - V - vi - I`.
    *   **Analysis:** Masterful use of `add9` and `sus2` voicings to blur the major/minor third distinction, establishing a profound sense of nostalgic ambiguity.
*   **Days of Thunder (F Lydian / D Dorian):**
    *   **Progression:** Features constant rootless voicings and slash chords like `C/E - F - Am - G`.
    *   **Analysis:** The avoidance of root-position tonics provides a floating, unresolved cinematic texture.

### Carpenter Brut
*   **Turbo Killer (D Phrygian / Minor):**
    *   **Progression:** Intense reliance on `i - bII - i` (Dm - Eb - Dm).
    *   **Analysis:** The bII chord (Phrygian crunch) is the cornerstone of Darksynth tension. Combined with rapid 16th-note bass arpeggiations.
*   **Roller Mobster (F# Phrygian Dominant):**
    *   **Progression:** `i - bII - viio` utilizing harmonic minor alterations (raised 3rd, flat 2nd).
    *   **Analysis:** High dissonance and aggressive half-step resolutions create an apocalyptic soundscape.

### Gunship
*   **Tech Noir (C minor):**
    *   **Progression:** `i - VI - III - VII` (Cm - Ab - Eb - Bb).
    *   **Analysis:** A foundational 80s pop/synthwave progression, heavily utilizing rich analog brass pads to thicken the triads.
*   **Fly For Your Life (G minor):**
    *   **Progression:** Explores `i - iv - v` structures, utilizing tight, staccato bass sequencing against sustained, tension-filled string pads.

### Daft Punk
*   **Tron: Legacy Theme (C minor):**
    *   **Progression:** `i - VI` (Cm - Abmaj7) ostinato.
    *   **Analysis:** Cinematic minimalism. The harmony shifts underneath a static melodic motif (pedal point), generating massive forward momentum.
*   **End of Line (A Dorian):**
    *   **Progression:** `i - IV` (Am - D major).
    *   **Analysis:** The major IV chord contains the raised 6th of the Dorian mode (F#), injecting a bright, futuristic "heroic" energy into a minor key.

---

## 2. Sectional Harmony & Tension/Release

### Intro / Verse (Tension Building)
*   **Harmonic Ambiguity:** Verses thrive on lack of resolution. Use of `sus2`, `sus4`, and `min11` chords. 
*   **Pedal Points:** A static bass note (e.g., C pedal) while triads shift above: `C - F/C - G/C - C`.
*   **Slash Chords:** `IV/V` or `ii/V` to build anticipation without stating the dominant explicitly.

### Pre-Chorus (Escalation)
*   **Rising Action:** Harmonically moving away from the tonic. Use of secondary dominants (`V/vi` or `V/V`).
*   **Suspended Dominants:** `V7sus4` hanging for 2-4 bars before the drop.

### Chorus / Drop (Release)
*   **Functional Resolution:** Strong root movements (4ths and 5ths). `i - VI - III - VII` or `vi - IV - I - V`.
*   **Voicing:** Power chords (Root-Fifth-Octave) in the low mids to leave frequency space for aggressive sub-bass and high soaring lead arpeggios.

### Bridge
*   **Modulation:** The bridge is the prime location for Chromatic Mediants or parallel minor/major shifts to break the loop.

---

## 3. Modal Borrowing and Interchange

### The Minor Flavors
*   **Aeolian (Natural Minor):** The default setting. Dark, driving (`i - VI - v`).
*   **Dorian:** The "Outrun" mode. The major `IV` chord brings a neon-soaked, driving optimism. (`i - IV`).
*   **Phrygian:** The "Darksynth" mode. The `bII` chord creates immediate, evil tension. (`i - bII`).

### Essential Interchanges
*   **The Minor iv in Major:** The "nostalgic" cadence. Borrowing the minor subdominant in a major key: `I - IV - iv - I` (C - F - Fm - C). The voice leading (A -> Ab -> G) is devastatingly emotional.
*   **Andalusian Cadence:** Descending minor progression: `i - bVII - bVI - V` (Am - G - F - E).
*   **Chromatic Mediant Modulations:** Jumping to a key a third away. For cinematic shock: `D minor -> Bb minor` (down a major third) or `D minor -> F# minor` (up a major third). 

---

## 4. Voice Leading & MIDI Architecture

*   **Bass / Sub Layer (MIDI C0 - C2):** Avoid thirds. Stick to Roots and Fifths. Parallel fifths are *encouraged* in Darksynth to mimic power chords.
*   **Pad Layer (MIDI C3 - C5):** Require strict parsimonious voice leading. Move voices by half-step or whole-step and retain common tones. E.g., `C minor (C-Eb-G)` to `Ab Major (C-Eb-Ab)` – only the G moves to Ab. This creates a smooth, glassy texture that doesn't distract from the melody.
*   **Lead / Arp Layer (MIDI C4 - C6):** Emphasize extensions (9ths, 11ths, 13ths) of the underlying chords to add color without muddying the mid-range.

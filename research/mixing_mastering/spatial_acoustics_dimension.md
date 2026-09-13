# Spatial Acoustics & Dimension Architecture: A Blueprint for 3D Electronic Staging

## Introduction
Creating a compelling three-dimensional mix in electronic music requires intentional orchestration of width, depth, and height. By systematically manipulating early reflections, reverberation decay, stereo field placement, and spectral depth cues, producers can build an immersive sonic landscape. This report outlines the definitive framework for engineering 3D spatial staging.

## 1. Reverb Staging: Front-to-Back Layering
Reverb is the primary mechanism for establishing environmental context and distance. Effective staging relies on utilizing contrasting reverb algorithms for different elements to prevent frequency masking and dimensional flattening.

### Small Room / Early Reflections (Drums & Close Percussion)
- **Settings:** < 25ms Pre-delay, ~0.6s Decay.
- **Function:** Places percussive elements in a tangible, tight physical space without muddying the mix. Early reflections define the "size" of the space.
- **Application:** Claps, hi-hats, and rhythmic synths. A short decay prevents rhythmic smearing, while the minimal pre-delay bonds the space to the transient.

### Hall / Plate Reverb (Leads & Vocals)
- **Settings:** 40–60ms Pre-delay, 2.5s+ Decay.
- **Function:** Creates majestic, soaring sustain for melodic focal points.
- **Application:** Lead synths, vocals, and arpeggios. The longer pre-delay (often tempo-synced, e.g., 1/64 or 1/32 note) is critical here—it separates the dry transient from the onset of the reverb tail, preserving the upfront intelligibility of the lead while still immersing it in a vast space.

## 2. Stereo Imaging: The Width Spectrum
A wide mix is only effective when anchored by a powerful, focused center. The contrast between mono and ultra-wide elements dictates the perceived width.

### Mono Core & Phantom Center
- **Low-End Foundation:** All frequencies below ~130 Hz should be strictly mono. This ensures phase coherence, club system compatibility, and maximum punch.
- **Phantom Center:** The kick drum, snare body, main bass, and primary lead hook must be panned dead center. These elements drive the rhythm and melody; placing them centrally gives them power and focus.

### Ultra-Wide Sides
- **Techniques:** Haas effect delays (10-30ms difference between L/R), chorus, micro-pitch shifting, and Mid/Side EQ (boosting highs on the sides).
- **Elements:** Atmospheric pads, stereo delay taps, white noise sweeps, and auxiliary percussion (shakers, wide claps). Pushing these to the extreme edges leaves the center channel clear for the primary elements.

## 3. Depth Cues: Pushing Elements into the Background
Depth is not just about reverb; it's about mimicking how sound travels through air. High frequencies dissipate faster than low frequencies over distance.

- **Low-Pass Filtering (Spectral Dimming):** To push an element (e.g., a background pad) "behind" a lead, apply a low-pass filter (rolling off above 5-8 kHz).
- **Transient Softening:** Distant sounds lack sharp transients. Using transient shapers or fast-attack compression to reduce the initial "click" pushes sounds further back.
- **Volume Attenuation:** Naturally, distant sounds are quieter. Combining volume reduction with LPF creates a psychoacoustic illusion of true physical distance.

---

## Spatial Routing Blueprint
1. **Send A (Drum Room):** Room Reverb (0.6s decay, 10ms pre-delay). EQ: HPF @ 250Hz, LPF @ 7kHz.
2. **Send B (Vocal/Lead Plate):** Plate Reverb (2.5s decay, 45ms pre-delay). EQ: HPF @ 400Hz, High-shelf boost.
3. **Send C (Lush Hall):** Hall Reverb (4.0s decay, 60ms pre-delay). EQ: Abbey Road trick (HPF @ 600Hz, LPF @ 10kHz). Sidechain compressed to the dry lead.
4. **Master Bus:** Mid/Side EQ (HPF Side channel at 130Hz).

---

## JSON Spatial Acoustics Configuration

```json
{
  "spatial_architecture": {
    "reverb_staging": {
      "drums_percussion": {
        "type": "Small Room / Early Reflections",
        "pre_delay_ms": "<25",
        "decay_time_s": 0.6,
        "eq_filtering": "HPF @ 300Hz, LPF @ 7kHz"
      },
      "lead_elements": {
        "type": "Hall / Plate",
        "pre_delay_ms": "40-60",
        "decay_time_s": 2.5,
        "eq_filtering": "HPF @ 400Hz, Abbey Road EQ style"
      }
    },
    "stereo_imaging": {
      "mono_center": {
        "frequency_range": "< 130 Hz",
        "elements": [
          "Kick",
          "Sub Bass",
          "Snare (Main Body)",
          "Lead Vocal / Main Hook"
        ]
      },
      "stereo_sides": {
        "techniques": [
          "Haas Effect (10-30ms offset)",
          "Chorus/Ensemble",
          "Mid/Side EQ"
        ],
        "elements": [
          "Pads",
          "Stereo Delay Taps",
          "High Percussion",
          "Backing Vocals"
        ]
      }
    },
    "depth_cues": {
      "foreground": {
        "volume": "0 to -6 dB",
        "frequency_response": "Full Spectrum, Bright, Intact Transients",
        "elements": [
          "Leads",
          "Kick",
          "Snare"
        ]
      },
      "background": {
        "volume": "-12 to -24 dB",
        "frequency_response": "Low-pass filtered, rolled off highs, softened transients",
        "elements": [
          "Atmospheric Pads",
          "Distant FX",
          "Support Strings"
        ]
      }
    }
  }
}
```

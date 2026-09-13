# Lead Articulation & Humanization: Injecting Soul into Synthesized Leads

**Author**: Agent 17 - Vocal Chop & Lead Synth Articulation Specialist  
**Discipline**: Computational Musicology & Advanced Sound Design Synthesis  
**Scope**: Legato lead transitions, pitch bend scoops, delayed vibrato, and formant-shifted vocal chop arpeggios (in the style of Daft Punk, Madeon, Porter Robinson, Skrillex).

---

## 1. Portamento / Glide Dynamics
Human instrumentalists and vocalists rarely snap between notes instantaneously. Synthesized leads achieve "soul" by mimicking this glide through precise **Portamento** tuning.
* **Legato Transitions**: A glide time of **30ms to 85ms** is the sweet spot. 
  * `30ms-45ms`: Fast, punchy, "Complextro" style leads. Gives a slight whip-like articulation without losing rhythmic intent.
  * `60ms-85ms`: Expressive, euphoric "Nurture" style glides that emulate human breath transitions and dramatic vocal leaps.

## 2. Pitch Bend Articulations
To anchor a lead melody, synthesize a virtual "scoop" into downbeat target notes, mimicking a guitarist sliding into a fret or a vocalist finding pitch.
* **2-Semitone Scoops**: Map a pitch envelope to -2 semitones, curving upward into the root pitch over 70-120ms. Use a logarithmic curve to simulate the tension of vocal cords tightening.

## 3. Vibrato Delay
Synthetic, instant vibrato sounds cheap and robotic. Human vibrato builds gradually after a sustained note stabilizes.
* **Delay**: 300ms delay before vibrato engages.
* **Fade In**: 150ms fade-in time for the LFO depth.
* **Rate**: 4-6 Hz.
* **Depth**: 20-35 cents.

## 4. Formant-Shifted Vocal Chop Arpeggios
A hallmark of modern electronic composition (Porter Robinson, Skrillex) is using human voice samples chopped and mapped to MIDI, shifting formants independently of pitch.
* **Top-Line Layers**: Use vocal chops as staccato arpeggios layered over sustained saw/square leads.
* **Formant Rules**: Shift formants UP (+2 to +4) on lower velocity notes to emulate whispery/head-voice textures, and shift formants DOWN (-1 to -3) on high velocity notes to mimic guttural/chest-voice power.

---

## The 8 Articulation Models (JSON Performance Curves)

The following JSON schema defines 8 programmatic models for expressive synth leads and vocal chops, ready for parsing by algorithmic music generation engines.

```json
{
  "lead_articulation_models": [
    {
      "model_id": "M01_FRENCH_TOUCH_GLIDER",
      "style_reference": "Daft Punk",
      "synthesis_type": "square_saw_talkbox",
      "portamento": { "mode": "legato", "time_ms": 45, "curve": "exponential" },
      "pitch_bend": { "type": "scoop", "range_st": -2, "duration_ms": 80 },
      "vibrato": { "delay_ms": 300, "attack_ms": 150, "rate_hz": 4.5, "depth_cents": 20 }
    },
    {
      "model_id": "M02_COMPLEXTRO_LASER",
      "style_reference": "Skrillex",
      "synthesis_type": "fm_growl_lead",
      "portamento": { "mode": "always", "time_ms": 30, "curve": "linear" },
      "pitch_bend": { "type": "whip_down", "range_st": 12, "duration_ms": 40 },
      "vibrato": { "delay_ms": 0, "attack_ms": 0, "rate_hz": 0, "depth_cents": 0 }
    },
    {
      "model_id": "M03_NURTURE_BREATHY_CHOP",
      "style_reference": "Porter Robinson",
      "synthesis_type": "vocal_chop_sampler",
      "portamento": { "mode": "legato", "time_ms": 85, "curve": "logarithmic" },
      "pitch_bend": { "type": "scoop", "range_st": -2, "duration_ms": 120 },
      "vibrato": { "delay_ms": 350, "attack_ms": 200, "rate_hz": 5.0, "depth_cents": 30 },
      "formant_shift": { "velocity_mapped": true, "low_vel_shift": 3, "high_vel_shift": -1 }
    },
    {
      "model_id": "M04_ADVENTURE_STACCATO_ARP",
      "style_reference": "Madeon",
      "synthesis_type": "pulse_vocal_hybrid",
      "portamento": { "mode": "off", "time_ms": 0, "curve": "none" },
      "pitch_bend": { "type": "none", "range_st": 0, "duration_ms": 0 },
      "vibrato": { "delay_ms": 200, "attack_ms": 100, "rate_hz": 6.0, "depth_cents": 25 },
      "formant_shift": { "velocity_mapped": false, "static_shift": 2 }
    },
    {
      "model_id": "M05_EMOTIONAL_SWELL",
      "style_reference": "Porter Robinson",
      "synthesis_type": "supersaw_lead",
      "portamento": { "mode": "legato", "time_ms": 70, "curve": "exponential" },
      "pitch_bend": { "type": "scoop", "range_st": -2, "duration_ms": 150 },
      "vibrato": { "delay_ms": 400, "attack_ms": 300, "rate_hz": 4.0, "depth_cents": 35 }
    },
    {
      "model_id": "M06_DISCOVERY_SOLO",
      "style_reference": "Daft Punk",
      "synthesis_type": "moog_triangle",
      "portamento": { "mode": "legato", "time_ms": 60, "curve": "linear" },
      "pitch_bend": { "type": "up_down_flick", "range_st": 2, "duration_ms": 90 },
      "vibrato": { "delay_ms": 250, "attack_ms": 100, "rate_hz": 5.5, "depth_cents": 25 }
    },
    {
      "model_id": "M07_AGGRESSIVE_VOWEL_BASS",
      "style_reference": "Skrillex",
      "synthesis_type": "wavetable_vowel",
      "portamento": { "mode": "always", "time_ms": 40, "curve": "exponential" },
      "pitch_bend": { "type": "scoop", "range_st": -12, "duration_ms": 200 },
      "vibrato": { "delay_ms": 100, "attack_ms": 50, "rate_hz": 4.0, "depth_cents": 15 }
    },
    {
      "model_id": "M08_SHELTER_CHORD_LEAD",
      "style_reference": "Madeon / Porter Robinson",
      "synthesis_type": "layered_vocal_synth",
      "portamento": { "mode": "legato", "time_ms": 80, "curve": "logarithmic" },
      "pitch_bend": { "type": "scoop", "range_st": -1, "duration_ms": 100 },
      "vibrato": { "delay_ms": 300, "attack_ms": 150, "rate_hz": 4.5, "depth_cents": 20 },
      "formant_shift": { "velocity_mapped": true, "low_vel_shift": 4, "high_vel_shift": 0 }
    }
  ]
}
```

## Velocity and MIDI Interval Arrays
* **Velocity Mapping**: Assign `0-40` to low-pass filter (cutoff 800Hz), `41-100` to medium open (cutoff 3kHz), and `101-127` to wide open (cutoff 10kHz) + subtle white noise layer.
* **Interval Arrays**: For chop arpeggios, prioritize these intervals relative to root: `[0, 3, 7, 10]` (Minor 7th chord shapes) or `[0, 4, 7, 9]` (Major 6th chord shapes) for maximum emotional resonance without harmonic clutter.

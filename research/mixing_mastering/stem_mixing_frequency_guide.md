# The Mixing Engineer: Stem Balancing & Frequency Carving

## Overview
Achieving crystal clarity, punchy low-end, and zero mid-range mud in electronic music requires meticulous frequency management. Top mixing engineers like Serban Ghenea, Mick Guzauski, and Luca Pretolesi rely on precise EQ pocketing, dynamic processing, and surgical subtractive EQ to create separation and depth.

## 1. Low-End Management: Kick vs. Sub-Bass
The relationship between the kick drum and sub-bass is the foundation of electronic music. The goal is to avoid frequency masking and phase cancellation in the 30-120 Hz range.

**Techniques:**
*   **Fundamental Frequency Separation:** If the kick fundamental is at 50-60 Hz, the sub-bass should occupy either the sub-harmonic (30-45 Hz) or the upper bass region (80-120 Hz).
*   **Dynamic EQ / Sidechaining:** Use sidechain compression or dynamic EQ on the bass bus, triggered by the kick drum, to duck the overlapping frequencies (usually a narrow cut around 50-80 Hz, ducking 3-6 dB with a fast attack of <5ms and release timed to the groove, typically 30-80ms).
*   **High-Pass Filtering (HPF):** Aggressive HPF (12-24dB/octave) on all non-bass elements at 100-150 Hz to preserve low-end headroom.

**Exact EQ Curve (Kick vs Bass):**
*   **Kick:** Boost +2dB @ 55Hz (Q=1.5), Cut -3dB @ 250Hz (Q=2.0).
*   **Bass:** Cut -2dB @ 55Hz (Q=2.0) or Dynamic Cut triggered by Kick. Boost +1.5dB @ 90Hz (Q=1.0) for definition.

## 2. Low-Mid Cleanup: Eliminating Boxiness
The 250-400 Hz range is notorious for "mud" and "boxiness," especially when multiple synths, pads, and reverbs overlap.

**Techniques:**
*   **Surgical Cuts:** Cut -2 to -4 dB between 250-400 Hz on pads, dense chords, and reverb returns.
*   **Dynamic Suppression:** Use a multiband compressor on the synth bus to clamp down on the 300 Hz region only when it exceeds a threshold, maintaining warmth without buildup.
*   **Mid/Side Processing:** Cut low-mids more aggressively on the Side channel to keep the low-end focused in the center while preserving stereo width in the highs.

**Exact EQ Curve (Pads/Reverb):**
*   **Pads:** Cut -3dB @ 300Hz (Q=1.5), HPF @ 150Hz.
*   **Reverb Return:** Cut -4dB @ 350Hz (Q=2.0), HPF @ 200Hz.

## 3. High-Mid Presence: Intelligibility and Bite
The 2-5 kHz range is where human hearing is most sensitive. This is critical for vocals, lead synths, and transient snap.

**Techniques:**
*   **Saturation over EQ:** Instead of extreme EQ boosts, use tape or tube saturation to generate upper-harmonic excitement. This adds presence without the harsh phase shift of aggressive EQ.
*   **Carving Space:** To make a vocal or lead pop, cut 1-2 dB at 3 kHz on competing elements (rhythm synths, guitars, overheads).
*   **Dynamic EQ on Leads:** Use dynamic EQ to tame 4 kHz resonances that become harsh at high volumes, compressing only when the harshness peaks.

**Exact EQ Curve (Lead/Vocal vs Accompaniment):**
*   **Lead/Vocal:** Boost +1.5dB @ 3.5kHz (Q=1.0) or apply harmonic exciter.
*   **Accompaniment:** Cut -1.5dB @ 3.5kHz (Q=1.0).

## 4. Air Frequencies: High-End Polish
The 10-16 kHz range provides "air," "sheen," and "expensive" high-end polish.

**Techniques:**
*   **Pultec-Style Shelves:** Use a broad, musical high-shelf boost (e.g., Pultec EQP-1A emulation) at 10 kHz or 12 kHz. The gentle curve adds brightness without piercing harshness.
*   **Transient Shaping:** Boost the air frequencies on transient-heavy elements (hi-hats, shakers) rather than sustained sounds to enhance rhythmic energy.
*   **Low-Pass Filtering (LPF):** Conversely, use LPFs on elements that don't need high-frequency information (bass, low synths, kick) to prevent white noise buildup.

**Exact EQ Curve (Master Bus/Vocals):**
*   **Master Bus / Vocals:** High Shelf Boost +1.5dB @ 12kHz.

---

## JSON Mixing Template

```json
{
  "mixing_template": {
    "buses": [
      {
        "name": "Kick",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 25, "slope": "24dB/oct"},
              {"type": "Bell", "freq": 55, "gain": 2.0, "q": 1.5},
              {"type": "Bell", "freq": 250, "gain": -3.0, "q": 2.0},
              {"type": "HighShelf", "freq": 5000, "gain": 1.5, "q": 0.7}
            ]
          },
          {
            "type": "Compression",
            "attack_ms": 15,
            "release_ms": 50,
            "ratio": 4,
            "threshold_db": -12,
            "makeup_gain_db": 2
          }
        ]
      },
      {
        "name": "Sub_Bass",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 25, "slope": "24dB/oct"},
              {"type": "LPF", "freq": 150, "slope": "12dB/oct"}
            ]
          },
          {
            "type": "Sidechain_Dynamic_EQ",
            "trigger": "Kick",
            "band": {"type": "Bell", "freq": 55, "q": 2.0},
            "ducking_depth_db": -5,
            "attack_ms": 2,
            "release_ms": 40
          }
        ]
      },
      {
        "name": "Mid_Bass",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 100, "slope": "24dB/oct"},
              {"type": "Bell", "freq": 120, "gain": 1.5, "q": 1.0},
              {"type": "Bell", "freq": 350, "gain": -2.0, "q": 1.5}
            ]
          },
          {
            "type": "Saturation",
            "drive": "Moderate",
            "type": "Tape"
          }
        ]
      },
      {
        "name": "Synths_Pads",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 150, "slope": "18dB/oct"},
              {"type": "Bell", "freq": 300, "gain": -3.0, "q": 1.5},
              {"type": "Bell", "freq": 3500, "gain": -1.5, "q": 1.0}
            ]
          },
          {
            "type": "Multiband_Compression",
            "band_250_500Hz": {"threshold_db": -18, "ratio": 3, "attack_ms": 10, "release_ms": 100}
          }
        ]
      },
      {
        "name": "Leads_Vocals",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 120, "slope": "12dB/oct"},
              {"type": "Bell", "freq": 350, "gain": -1.5, "q": 1.5},
              {"type": "HighShelf", "freq": 10000, "gain": 2.0, "type": "Pultec"}
            ]
          },
          {
            "type": "Dynamic_EQ",
            "band": {"type": "Bell", "freq": 4000, "q": 2.5},
            "threshold_db": -15,
            "ducking_depth_db": -3
          }
        ]
      },
      {
        "name": "Reverb_Return",
        "processing": [
          {
            "type": "EQ",
            "bands": [
              {"type": "HPF", "freq": 200, "slope": "24dB/oct"},
              {"type": "Bell", "freq": 350, "gain": -4.0, "q": 2.0},
              {"type": "LPF", "freq": 8000, "slope": "12dB/oct"}
            ]
          }
        ]
      }
    ]
  }
}
```

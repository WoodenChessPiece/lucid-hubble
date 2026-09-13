# Dynamic Transition FX & Impact Designer: Research Report

## 1. Downlifters & White Noise Sweeps
Downlifters release energy from buildups, usually starting on the downbeat of a new section.
- **Sound Source**: White or pink noise.
- **Filtering**: Low-pass filter (LPF) sweeping downwards.
  - Start Frequency: ~10 kHz to 20 kHz.
  - End Frequency: ~100 Hz to 500 Hz.
  - Curve: Logarithmic.
- **Dynamics & Routing**: Heavy reverb (decay 3-5s) ducked via sidechain compression triggered by the kick drum to prevent low-end mud.
- **Modulation**: Optional slow LFO (sine or triangle) modulating stereo panning or filter resonance for movement.

## 2. Sub-Boom / Bass Drops
Used to add immense weight and gravity to a transition, particularly into a sparse section or a heavy drop.
- **Sound Source**: Pure sine wave oscillator.
- **Pitch Envelope**: Fast initial pitch drop, followed by a slower glide.
  - Start Pitch: ~90 Hz.
  - End Pitch: ~25 Hz.
  - Decay Time: 1 to 3 seconds depending on the tempo.
- **Amplitude Envelope**: Hard attack, slow decay.
- **Saturation**: Light tape or tube saturation to add higher harmonics so it's audible on smaller speakers.

## 3. Reverse Crashes and Gated Reverb Snare Claps
These elements build tension precisely before the downbeat (often the last 1 or 2 beats of a bar).
- **Reverse Crash**: 
  - Standard cymbal crash sample reversed.
  - Adjusted so the peak amplitude hits exactly on the grid (usually beat 1 of the new section).
- **Gated Reverb Snare**: 
  - Massive digital reverb (large hall or plate, decay > 3s) abruptly cut off by a noise gate.
  - The gate threshold is high, and the release is extremely fast (~5-10ms) to create a sudden vacuum of silence immediately before the downbeat.

## 4. Impact Hits and Cinematic Braams
Planted directly on the downbeat to signal massive structural changes.
- **Impacts**: Layered acoustic drums (toms, kicks) with metallic hits, pitched down and run through transient shapers and hard clippers.
- **Braams**: Layered brass and low-end synth (sawtooth + sub).
  - Heavy distortion/fuzz.
  - Aggressive low-pass filter with an envelope opening up (attack ~50ms) and closing slowly.

## DSP Parameters and JSON Transition Event Definitions

```json
{
  "transitions": [
    {
      "name": "Classic_Downlifter",
      "type": "noise_sweep",
      "trigger_beat": 1.0,
      "duration_beats": 16.0,
      "dsp": {
        "oscillator": "white_noise",
        "filter": {
          "type": "lowpass_24db",
          "start_freq_hz": 15000,
          "end_freq_hz": 200,
          "sweep_curve": "logarithmic"
        },
        "fx": {
          "reverb": {
            "decay_s": 4.0,
            "mix": 0.6
          },
          "sidechain": {
            "source": "kick",
            "ratio": 4.0,
            "threshold_db": -12.0
          }
        }
      }
    },
    {
      "name": "Heavy_Sub_Drop",
      "type": "bass_drop",
      "trigger_beat": 1.0,
      "duration_beats": 8.0,
      "dsp": {
        "oscillator": "sine",
        "pitch_envelope": {
          "start_hz": 90.0,
          "end_hz": 25.0,
          "time_s": 2.5,
          "curve": "exponential"
        },
        "amp_envelope": {
          "attack_ms": 5,
          "decay_ms": 2500,
          "sustain_level": 0.0,
          "release_ms": 10
        },
        "saturation": {
          "type": "tape",
          "drive_db": 3.0
        }
      }
    },
    {
      "name": "Pre_Drop_Reverse_Crash",
      "type": "reverse_cymbal",
      "trigger_beat": -2.0, 
      "duration_beats": 2.0,
      "dsp": {
        "sample": "cymbal_crash_909",
        "reverse": true,
        "alignment": "peak_at_downbeat",
        "fade_in_curve": "exponential"
      }
    },
    {
      "name": "Cinematic_Drop_Impact",
      "type": "impact",
      "trigger_beat": 1.0,
      "duration_beats": 4.0,
      "dsp": {
        "layers": ["sub_kick", "metallic_anvil", "distorted_brass_braam"],
        "transient_shaper": {
          "attack": 5.0,
          "sustain": -2.0
        },
        "clipper": {
          "threshold_db": -3.0
        },
        "reverb": {
          "type": "plate",
          "size": 100,
          "decay_s": 3.0
        }
      }
    }
  ]
}
```

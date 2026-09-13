# Build-Up Tension & Riser Engineering Database

## 1. Snare Roll Acceleration Curves
The classic electronic music build-up relies on exponential rhythmic density and velocity ramping to generate tension.

### Acceleration Model
The subdivision length $L$ of the snare notes at time $t$ (where $t$ is the normalized time from 0 to 1 over the duration of the build-up) follows an exponential decay:
$L(t) = L_{start} \cdot 2^{- \lfloor k \cdot t \rfloor}$
Where $k$ determines the number of subdivision doublings.
For an 8-bar build-up, typically transitioning from 1/4 notes to 1/64 notes:
- Bars 1-4: 1/4 notes
- Bars 5-6: 1/8 notes
- Bar 7: 1/16 notes
- Bar 8 (beats 1-2): 1/32 notes
- Bar 8 (beat 3): 1/64 notes
- Bar 8 (beat 4): Silence (Zero Drop)

### Velocity Curve Ramping
Velocity $V(t)$ is often modeled using a quadratic or exponential growth function to simulate increasing intensity:
$V(t) = V_{min} + (V_{max} - V_{min}) \cdot t^p$
Where $p \approx 2$ to $3$ for an exponential feel.

### JSON Representation
```json
{
  "snare_roll": {
    "duration_bars": 8,
    "acceleration_phases": [
      { "start_bar": 1, "end_bar": 5, "subdivision": "1/4", "velocity_range": [60, 80] },
      { "start_bar": 5, "end_bar": 7, "subdivision": "1/8", "velocity_range": [80, 100] },
      { "start_bar": 7, "end_bar": 8, "subdivision": "1/16", "velocity_range": [100, 115] },
      { "start_bar": 8, "end_bar": 8.5, "subdivision": "1/32", "velocity_range": [115, 127] },
      { "start_bar": 8.5, "end_bar": 8.75, "subdivision": "1/64", "velocity_range": [127, 127] },
      { "start_bar": 8.75, "end_bar": 9, "subdivision": "none", "description": "Zero Drop Silence" }
    ],
    "velocity_curve": "exponential",
    "velocity_exponent_p": 2.5
  }
}
```

## 2. Pitch Risers
Pitch risers use continuous chromatic glissando or discrete chromatic steps to elevate harmonic tension.

### Pitch Trajectory
For a synth riser climbing 2 octaves (+24 semitones) over 8 bars, the pitch bend $P(t)$ in semitones can be linear or convex:
Linear: $P(t) = 24 \cdot t$
Convex (tension peaks late): $P(t) = 24 \cdot t^{1.5}$

### JSON Synthesis Recipe
```json
{
  "pitch_riser": {
    "waveform": "sawtooth",
    "voices": 5,
    "detune": 0.15,
    "duration_bars": 8,
    "start_pitch": "C3",
    "end_pitch": "C5",
    "pitch_envelope": {
      "type": "convex",
      "formula": "24 * (t ^ 1.5)",
      "target_semitones_offset": 24
    },
    "effects": {
      "reverb": { "mix": "increases from 10% to 50%", "decay_time": "3.5s" },
      "chorus": { "rate": "0.5Hz", "depth": "40%" }
    }
  }
}
```

## 3. High-Pass Filter (HPF) Sweeps
To maximize the impact of the drop, the low-end of the mix is progressively removed during the build-up. This creates a psychoacoustic "vacuum" that makes the reintroduction of the sub-bass at the drop feel significantly heavier.

### Filter Cutoff Formula
The HPF cutoff frequency $F(t)$ typically follows a logarithmic scale to sound linear to human hearing:
$F(t) = F_{min} \cdot \left( \frac{F_{max}}{F_{min}} \right)^t$
- $F_{min} \approx 20 \text{ Hz}$ (inactive)
- $F_{max} \approx 400 \text{ Hz}$

### JSON Automation Rules
```json
{
  "hpf_sweep": {
    "target": "master_bus_or_drum_group",
    "filter_type": "high_pass",
    "slope": "24dB/oct",
    "duration_bars": 8,
    "frequency_curve": {
      "type": "logarithmic",
      "f_min_hz": 20,
      "f_max_hz": 400,
      "formula": "20 * (20 ^ t)"
    },
    "resonance_q": {
      "start": 0.707,
      "end": 1.5,
      "description": "Slight resonance boost at cutoff to accentuate the sweep."
    }
  }
}
```

## 4. The 'Zero-Drop' Moment of Silence
The 'Zero-Drop' is a micro-arrangement technique where a vacuum of silence (usually 1 beat to 1 bar) is inserted immediately before the drop. This reset maximizes dynamic contrast.

### Techniques
1. **Total Vacuum:** Absolute silence (muting all tracks including reverb/delay tails).
2. **Vocal Glitch/Pre-shift:** A dry, isolated vocal phrase or a reversed reverb swell leading into the downbeat.
3. **Reverse Tape Stop:** A quick pitch-down and amplitude fade simulating a turntable stopping.

### JSON Arrangement Instructions
```json
{
  "zero_drop": {
    "placement": "End of build-up (e.g., Bar 8, Beat 4)",
    "duration_beats": 1,
    "actions": [
      {
        "track_group": "drums",
        "action": "mute"
      },
      {
        "track_group": "synths_and_bass",
        "action": "mute"
      },
      {
        "track_group": "fx_returns",
        "action": "mute_or_tape_stop",
        "tape_stop_time_ms": 250
      },
      {
        "track_group": "vocals",
        "action": "play_pre_drop_sample",
        "sample": "dry_vocal_shout.wav",
        "timing": "Beat 4"
      }
    ],
    "dynamic_range_delta_db": 18
  }
}
```

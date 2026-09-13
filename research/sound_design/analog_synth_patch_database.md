# Analog Synth Patch Database

## 1. Iconic Rolling Cyberpunk Bass (Moog / Sub-37 style)
*Oscillators:* Osc 1 (Sawtooth), Osc 2 (Square, 1 octave below). Sync: Off.
*Sub-oscillator:* Triangle wave mixed at 50%.
*Pulse Width Modulation:* N/A (Saw/Square base)
*Filter:* 24dB/oct Ladder Filter, Cutoff 40Hz, Resonance 30%. Envelope amount +60%.
*Envelopes:* Filter Env (A: 0ms, D: 300ms, S: 10%, R: 100ms). Amp Env (A: 0ms, D: 400ms, S: 80%, R: 100ms).
*Modulation:* LFO to Filter Cutoff (Rate: 1/8T or 1/16 depending on tempo).
*Portamento:* Glide time 15ms.

```json
{
  "patch_name": "Rolling Cyberpunk Bass",
  "synth_type": "Subtractive Analog Monosynth",
  "oscillators": [
    {"id": "Osc1", "waveform": "sawtooth", "octave": 0},
    {"id": "Osc2", "waveform": "square", "octave": -1},
    {"id": "Sub", "waveform": "triangle", "mix": 0.5}
  ],
  "filter": {
    "type": "ladder_24db",
    "cutoff_hz": 40,
    "resonance_pct": 30,
    "env_amount_pct": 60
  },
  "envelopes": {
    "filter": {"a": 0, "d": 300, "s": 10, "r": 100},
    "amp": {"a": 0, "d": 400, "s": 80, "r": 100}
  },
  "portamento_ms": 15
}
```

## 2. Warm Vintage Juno-106 80s Pad
*Oscillators:* DCO (Sawtooth + Square). Sub-oscillator level 30%.
*Pulse Width Modulation:* LFO driven PWM, Rate 0.4 Hz, Amount 40%.
*Filter:* 24dB/oct Low Pass, Cutoff 600Hz, Resonance 0%, HPF 1.
*Envelopes:* Amp Env (A: 1200ms, D: 0ms, S: 100%, R: 2500ms). Filter Env (A: 800ms, D: 1000ms, S: 50%, R: 2500ms).
*Chorus:* Chorus Mode II (Wide & lush).

```json
{
  "patch_name": "Warm Vintage 80s Pad",
  "synth_type": "Roland Juno-106",
  "oscillators": [
    {"waveform": "sawtooth", "mix": 1.0},
    {"waveform": "square", "mix": 1.0, "pwm_lfo_rate_hz": 0.4, "pwm_amount_pct": 40},
    {"waveform": "sub_square", "mix": 0.3}
  ],
  "filter": {
    "type": "lowpass_24db",
    "cutoff_hz": 600,
    "resonance_pct": 0,
    "hpf_freq": 1
  },
  "envelopes": {
    "filter": {"a": 800, "d": 1000, "s": 50, "r": 2500},
    "amp": {"a": 1200, "d": 0, "s": 100, "r": 2500}
  },
  "effects": {
    "chorus": "Mode II"
  }
}
```

## 3. Soaring Resonant Mono-Lead (Jupiter-8 style)
*Oscillators:* Osc 1 (Sync Master, Sawtooth), Osc 2 (Sync Slave, Square, +7 semitones).
*Filter:* 12dB/oct Low Pass, Cutoff 1200Hz, Resonance 70%.
*Envelopes:* Filter Env (A: 50ms, D: 400ms, S: 30%, R: 300ms). Amp Env (A: 10ms, D: 500ms, S: 100%, R: 200ms).
*Modulation:* Pitch Env on Osc 2 (+12 semitones attack transient). LFO to Pitch (Vibrato) delayed by 500ms, Rate 5Hz.
*Portamento:* Glide time 60ms.

```json
{
  "patch_name": "Soaring Resonant Mono-Lead",
  "synth_type": "Roland Jupiter-8",
  "oscillators": [
    {"id": "Osc1", "waveform": "sawtooth", "sync": "master"},
    {"id": "Osc2", "waveform": "square", "tuning": "+7st", "sync": "slave"}
  ],
  "filter": {
    "type": "lowpass_12db",
    "cutoff_hz": 1200,
    "resonance_pct": 70
  },
  "envelopes": {
    "filter": {"a": 50, "d": 400, "s": 30, "r": 300},
    "amp": {"a": 10, "d": 500, "s": 100, "r": 200}
  },
  "modulation": {
    "vibrato_delay_ms": 500,
    "vibrato_rate_hz": 5.0
  },
  "portamento_ms": 60
}
```

## 4. Nostalgic FM Electric Piano (Yamaha DX7 style)
*Algorithm:* Algorithm 5 (3 Carriers, 3 Modulators).
*Operators:* Op 1 (Carrier, Ratio 1.0), Op 2 (Modulator, Ratio 14.0, High output level for metallic attack), Op 3 (Carrier, Ratio 1.0, detuned +3), Op 4 (Modulator, Ratio 2.0).
*Envelopes:* Percussive decaying envelopes on Modulators (simulate tines). Sustain on Carriers.
*Velocity Sensitivity:* Modulator output levels mapped aggressively to velocity for dynamic brightness.
*Chorus/FX:* Subtle chorus to thicken the FM tone.

```json
{
  "patch_name": "Nostalgic FM Electric Piano",
  "synth_type": "Yamaha DX7",
  "algorithm": 5,
  "operators": [
    {"id": 1, "type": "carrier", "ratio": 1.0, "detune": 0},
    {"id": 2, "type": "modulator", "ratio": 14.0, "env": {"a": 0, "d": 200, "s": 0, "r": 100}, "velocity_sens": 99},
    {"id": 3, "type": "carrier", "ratio": 1.0, "detune": 3},
    {"id": 4, "type": "modulator", "ratio": 2.0, "env": {"a": 0, "d": 800, "s": 0, "r": 300}, "velocity_sens": 70}
  ]
}
```

## 5. Plucked Neon Arpeggio
*Oscillators:* Osc 1 (Square), Osc 2 (Pulse 25%). Detune: +5 cents.
*Pulse Width Modulation:* Manual, 25% pulse width on Osc 2.
*Filter:* 24dB/oct Low Pass, Cutoff 150Hz, Resonance 40%. Envelope Amount +80%.
*Envelopes:* Filter Env (A: 0ms, D: 150ms, S: 0%, R: 50ms). Amp Env (A: 0ms, D: 250ms, S: 0%, R: 100ms).
*Delay:* Ping-pong delay, 3/16th note sync, 30% feedback.

```json
{
  "patch_name": "Plucked Neon Arpeggio",
  "synth_type": "Subtractive Analog Poly",
  "oscillators": [
    {"id": "Osc1", "waveform": "square"},
    {"id": "Osc2", "waveform": "pulse_25", "detune_cents": 5}
  ],
  "filter": {
    "type": "lowpass_24db",
    "cutoff_hz": 150,
    "resonance_pct": 40,
    "env_amount_pct": 80
  },
  "envelopes": {
    "filter": {"a": 0, "d": 150, "s": 0, "r": 50},
    "amp": {"a": 0, "d": 250, "s": 0, "r": 100}
  },
  "effects": {
    "delay": {"type": "ping_pong", "sync": "3/16", "feedback_pct": 30}
  }
}
```

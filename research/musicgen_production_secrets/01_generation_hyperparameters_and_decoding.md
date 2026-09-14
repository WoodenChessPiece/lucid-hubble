# MusicGen 3.3B Production Engineering Secrets: Hyperparameters, Codec Bottlenecks, and Melodic Conditioning

## Executive Summary: The Autopsy of "What That Was"
When our pipeline ran `facebook/musicgen-stereo-large` with default settings:
- `temperature = 1.0`
- `guidance_scale (cfg_coef) = 3.5`
- Unconstrained sampling
- Monolithic end-to-end full-track generation in one pass
- Direct 32 kHz EnCodec waveform decode with no post-processing

The resulting output exhibited the classic **"MusicGen Sludge Syndrome"**:
1. **Muffled / Telephone-like Treble:** Loss of air above 15 kHz, dull transients, and muddy high-hats.
2. **Phase Mush & Comb Filtering:** An unconstrained stereo field that cancels out when played on mono sound systems.
3. **Severe CFG Overdrive Distortion:** High-frequency digital clipping and metallic ringing from CFG scale 3.5 over-saturating codebook logits.
4. **Polyphonic Hallucination & Rhythmic Smear:** Drums wandering off the grid, kick transients blurred across multiple 20ms frames, and bass clashing with lead melodies.

---

## 1. Optimal Hyperparameters
- **CFG Guidance (`cfg_coef`):** Drop from `3.5` to **`2.1`** (eliminates phase tear and metallic sizzle).
- **Temperature:** Drop from `1.0` to **`0.85`** (eliminates detuned pitch drift and noise floor).
- **Nucleus Sampling:** Set **`top_p = 0.90`** and **`top_k = 200`** (cuts low-probability RVQ garbage tokens).
- **Repetition Penalty:** Strictly **`1.0`** (values >1.0 destroy rhythmic periodicity like 4-on-the-floor kicks).

---

## 2. The Architectural Shift: Stem-Level Generation & Hybrid Routing
Commercial-grade AI music never generates an entire track in a single prompt. Top workflows use:
1. **Deterministic Rhythm & Sub-Bass (Local DSP):** Sample-accurate, punchy 50 Hz kick drum, crisp 200 Hz snare, mono-locked 808/sub-bass.
2. **Neural Lead / Hook (`facebook/musicgen-melody` or `musicgen-stereo-large`):** Conditioned on the exact melody and chords.
3. **Post-Codec DSP Chain:** Spectral excitation (Chebyshev harmonics >10.5 kHz), Mid/Side 140 Hz mono-lock, and transient recovery.

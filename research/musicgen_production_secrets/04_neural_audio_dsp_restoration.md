# Forensic DSP & Acoustic Engineering: Neural Audio Post-Processing & Restoration

## Executive Summary & Forensic Verdict

When a producer listens to raw MusicGen audio, four psychoacoustic alarm bells trigger simultaneously:
1. **The "Underwater / Flanging" Phenomenon:** EnCodec's Residual Vector Quantization (RVQ) combined with transposed-convolution vocoder decoding generates catastrophic phase dispersion and comb-filtering above 4 kHz, creating a "swirling, watery" artifact reminiscent of a low-bitrate MP3.
2. **The 10 kHz "Dark Blanket" & Ghost Shimmer:** Codebook bit starvation causes severe high-frequency roll-off above 10–11 kHz. The air band (12–20 kHz) lacks genuine harmonic sizzle, replaced instead by sporadic granular vocoder noise.
3. **Transient Collapse & Soft Attacks:** Autoregressive token sampling smears micro-second attack impulses. Kick drums, snare snaps, and pluck attacks lose their Dirac-like transient spikes, mushing into 15–30 ms blobs.
4. **The Flat "Wall of Mud" (Zero Dynamic Crest Factor):** Cross-entropy training penalizes silence, causing the model to emit a continuous low-level neural hash between musical events. This shrinks the dynamic range to an exhausting 6–8 dB crest factor with hyper-resonances in the 2.5–4.0 kHz Fletcher-Munson sensitivity sweet spot.

---

## The Industrial Restoration Chain
1. **Harmonic Bandwidth Synthesis:** Non-linear Chebyshev polynomial exciter to synthesize true harmonic air (>10.5 kHz).
2. **Differential Transient Recovery:** SPL Transient Designer modeling to restore instantaneous attack punch (+4 dB) and duck background neural hash (-3 dB).
3. **Dynamic Spectral Resonance Suppression:** Fast-tracking STFT spectral notch filtering (Soothe2/DSEQ paradigm) to surgically carve out 2 kHz–4.5 kHz harsh vocoder resonances.
4. **Mid-Side Sub-Bass Phase Alignment:** Elliptical mono-making below 130 Hz and spatial stereo air expansion.
5. **Oversampled True-Peak Mastering:** Broadcast-compliant limiting to achieve punchy -14 LUFS / -1.0 dBTP.

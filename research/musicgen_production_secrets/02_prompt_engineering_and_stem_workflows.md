# State-of-the-Art MusicGen 3.3B Prompt Engineering & Stem Conditioning Architecture

## Executive Summary
When users listen to raw outputs from `facebook/musicgen-stereo-large` (3.3B) and remark that it sounds muddy or muffled, the issue is architectural:

1. **Vocabulary Mismatch**: MusicGen was trained on licensed stock catalogs (Pond5, Shutterstock) with scrubbed artist names. Using artist names like *"Martin Garrix"* feeds out-of-distribution noise into the T5 text encoder. The model falls back to a diffuse average of stock music.
2. **The "Full Mix in One Neural Prompt" Fallacy**: Generating drums, sub-bass, chord pads, leads, and vocals simultaneously through a single prompt forces the model to compress all polyphonic elements into only 4 to 8 RVQ codebooks at 50Hz (20ms frames). This causes frequency masking, transient smearing, and muddy reverb soup.
3. **Absence of Negative Prompting**: Without negative Classifier-Free Guidance (CFG) to penalize muddiness, boxy sub-rumble, and phase cancellation, the unguided autoregressive distribution naturally regresses to low-fidelity stock music.
4. **The 30-Second Wall**: Attempting to generate a multi-section arrangement in a single 30-second context window leads to chaotic motif collisions rather than coherent structural progression.

---

## 1. High-Fidelity Vocabulary Activation
- **Translate Artists into Physical & Timbral Tags:**
  - *Martin Garrix* -> `progressive house, 128 bpm, key of D minor, bright detuned supersaw synth lead, punchy sidechained four-on-the-floor, uplifting stadium anthemic melody, clean mix, wide stereo`
  - *Deadmau5* -> `minimal progressive house, 128 bpm, analog Moog bassline, hypnotic plucks, dry crisp percussion, tight kick, clean stereo field`
- **Isolation Tokens (Mandatory for Stems):**
  - `isolated solo synthesizer lead, bright detuned supersaw, dry recording, clean high-end, wide stereo field, no drums, no bass`
  - `isolated synthesizer pad chords, warm analog polyphonic sustained harmony, rich chorus, no drums, no bass, no lead`

---

## 2. Negative CFG Prompting
```python
UNIVERSAL_NEGATIVE_PROMPT = (
    "muddy, muffled, boomy low-end, distorted, clipping, excessive reverb wash, "
    "phase cancellation, out of tune, mono mush, background noise, low bit-rate artifacts"
)
```

---

## 3. The 3-Tier Hybrid Architecture
Top AI music producers **never rely on MusicGen for drums and sub-bass**:
1. **Layer 1: Deterministic Engine / High-Res Samples**:
   - Kick Drum: Sample-accurate 0.2ms click + clean 50Hz sine sweep (Phase locked).
   - Hi-Hats & Percussion: Uncompressed 44.1kHz crisp 909/808 transients (>16kHz air).
   - Sub-Bass: Pure 45-60Hz mono sine wave, zero pitch drift.
2. **Layer 2: Neural MusicGen 3.3B (Isolated Stems)**:
   - Conditioned exclusively for **leads, pads, and vocal chops**.
3. **Layer 3: Python DAW / DSP Master Bus**:
   - 120Hz Highpass on Neural Stems (cuts all neural low-end mud).
   - Fast Optical Sidechain Ducking against deterministic kick (-12dB duck, 220ms release).
   - Mid/Side Spatializer (Mono center for bass/kick, wide side-channels for neural leads).
   - Console8 Saturation & EBU R128 Master Limiter (-14 LUFS / -1.0 dBTP).

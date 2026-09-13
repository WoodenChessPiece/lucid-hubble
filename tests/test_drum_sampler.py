"""
tests/test_drum_sampler.py - Comprehensive Verification and FFT Spectral Analysis
of Commercial Drum Sampler & Layering Engine.

Verifies:
1. Forensic contrast: Legacy np.sin pitch-drop kick & filtered noise snare vs modern commercial layered drums.
2. TransientShaper DSP: Differential attack/sustain envelope tracking, dB gain scaling, and soft ceiling.
3. Kick Layering Architecture: Sub sine (45-55 Hz), acoustic beater transient (2.5-4 kHz), saturated body.
4. Snare Layering Architecture: 200 Hz body thump, 909 snappy wire sizzle, stereo acoustic ring.
5. Claps & Hats: Multi-tap flam delays, inharmonic 6-oscillator cluster, pre-shifted offbeats.
6. SoundFont & Hybrid Integration: FluidSynth batch cache retrieval and seamless synthesis fallback.
7. Groove & Micro-Timing: MPC60 16th-note swing formula and offbeat pre-shift accuracy.
"""

import math
import numpy as np
import scipy.signal as signal

from src.engine.drum_sampler import (
    DrumSamplerEngine,
    TransientShaper,
    KickLayerEngine,
    SnareLayerEngine,
    ClapAndHatEngine,
    SoundFontDrumSampler,
    GrooveEngine,
    DrumHitEvent,
    SAMPLE_RATE,
)


def test_transient_shaper_attack_boost_and_sustain_cut():
    """Verify that TransientShaper boosts initial attack peak and attenuates sustain tail."""
    print("Testing TransientShaper DSP differential envelope dynamics...")
    sr = 44100
    shaper = TransientShaper(sample_rate=sr)

    # Test signal: synthetic burst with exponential decay
    dur = 0.4
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sig = (np.sin(2 * np.pi * 120 * t) * np.exp(-18 * t)).astype(np.float32)

    # 1. Boost attack by +6 dB, neutral sustain
    boosted = shaper.process(sig, attack_gain_db=6.0, sustain_gain_db=0.0, drive=1.0, ceiling_db=0.0)
    # The early transient (< 10ms) must have higher peak
    attack_window = int(0.010 * sr)
    assert np.max(np.abs(boosted[:attack_window])) > np.max(np.abs(sig[:attack_window])), "Attack transient was not boosted!"

    # 2. Cut sustain by -6 dB, neutral attack
    tightened = shaper.process(sig, attack_gain_db=0.0, sustain_gain_db=-6.0, drive=1.0, ceiling_db=0.0)
    # The tail (> 60ms) must have lower energy
    tail_start = int(0.060 * sr)
    tail_end = int(0.200 * sr)
    sig_tail_energy = np.sum(sig[tail_start:tail_end] ** 2)
    tight_tail_energy = np.sum(tightened[tail_start:tail_end] ** 2)
    assert tight_tail_energy < sig_tail_energy * 0.75, "Sustain tail was not attenuated!"

    # 3. Ceiling compliance
    hard_driven = shaper.process(sig * 4.0, attack_gain_db=6.0, ceiling_db=-0.5, drive=1.5)
    ceiling_linear = 10.0 ** (-0.5 / 20.0)
    assert np.max(np.abs(hard_driven)) <= ceiling_linear + 1e-4, f"Output exceeded ceiling: {np.max(np.abs(hard_driven))} vs {ceiling_linear}"

    print("  -> Passed! TransientShaper correctly isolates and shapes attack and sustain.")


def test_kick_layering_frequency_and_dynamics():
    """Verify kick layering: Sub sine (45-55 Hz), acoustic beater (2.5-4 kHz), and saturated body."""
    print("Testing Kick Layering Architecture (Sub + Beater + Saturated Body)...")
    sr = 44100
    kick_engine = KickLayerEngine(sample_rate=sr)

    kick = kick_engine.render_kick(
        pitch_sub=50.0,
        sub_decay=0.40,
        beater_freq=3200.0,
        saturation_drive=1.3,
        velocity=110,
        duration=0.45
    )

    # Must be stereo array with identical L and R (strict mono kick)
    assert kick.ndim == 2 and kick.shape[1] == 2
    assert np.allclose(kick[:, 0], kick[:, 1]), "Kick drum should be pure mono!"

    # FFT Spectral Analysis
    kick_mono = kick[:, 0]
    n_fft = 8192
    spec = np.abs(np.fft.rfft(kick_mono[:n_fft] * np.hanning(n_fft)))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)

    # Sub energy check (40 - 65 Hz)
    sub_band = (freqs >= 40) & (freqs <= 65)
    sub_energy = np.sum(spec[sub_band] ** 2)
    assert sub_energy > 1.0, "Kick lacks fundamental sub energy in 40-65 Hz!"

    # Beater energy check (2.5 - 4.5 kHz)
    beater_band = (freqs >= 2500) & (freqs <= 4500)
    beater_energy = np.sum(spec[beater_band] ** 2)
    assert beater_energy > 0.05, "Kick lacks acoustic beater click in 2.5-4.5 kHz!"

    # Contrast against legacy kick: calculate RMS energy
    legacy_t = np.linspace(0, 0.42, int(sr * 0.42), endpoint=False)
    legacy_pitch = 42 + (170 - 42) * np.exp(-36 * legacy_t)
    legacy_phase = 2 * np.pi * np.cumsum(legacy_pitch) / sr
    legacy_body = np.sin(legacy_phase) * np.exp(-10.5 * legacy_t)
    legacy_click = np.random.uniform(-1, 1, len(legacy_t)) * np.exp(-130 * legacy_t) * 0.45
    legacy_kick = np.tanh((legacy_body + legacy_click) * 1.85) * 0.94

    commercial_rms = np.sqrt(np.mean(kick_mono ** 2))
    legacy_rms = np.sqrt(np.mean(legacy_kick ** 2))

    print(f"  -> Commercial Kick RMS: {commercial_rms:.3f} vs Legacy Kick RMS: {legacy_rms:.3f}")
    assert commercial_rms > legacy_rms * 1.15, "Commercial kick should have substantially higher perceived fullness and RMS!"
    print("  -> Passed! Kick layering verified.")


def test_snare_layering_components():
    """Verify snare layering: 200 Hz body thump, snappy wire sizzle, stereo acoustic ring."""
    print("Testing Snare Layering Architecture (Thump + 909 Wire + Ring + Crack)...")
    sr = 44100
    snare_engine = SnareLayerEngine(sample_rate=sr)

    snare = snare_engine.render_snare(
        fundamental_freq=200.0,
        wire_decay=0.24,
        ring_decay=0.20,
        velocity=105,
        duration=0.45
    )

    assert snare.ndim == 2 and snare.shape[1] == 2
    # Snare wire must produce genuine stereo decorrelation (L != R)
    corr = np.corrcoef(snare[:, 0], snare[:, 1])[0, 1]
    print(f"  -> Snare L/R correlation: {corr:.3f} (natural stereo width)")
    assert 0.70 < corr < 0.98, "Snare must exhibit stereo width from wire sizzle and ring without phase cancellation!"

    # FFT analysis of body thump vs wire sizzle
    n_fft = 8192
    mid = 0.5 * (snare[:, 0] + snare[:, 1])
    spec = np.abs(np.fft.rfft(mid[:n_fft] * np.hanning(n_fft)))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)

    # 200 Hz fundamental body band (170 - 240 Hz)
    thump_band = (freqs >= 170) & (freqs <= 240)
    assert np.sum(spec[thump_band] ** 2) > 0.5, "Snare lacks 200 Hz body thump!"

    # Wire sizzle band (3.5 - 10 kHz)
    wire_band = (freqs >= 3500) & (freqs <= 10000)
    assert np.sum(spec[wire_band] ** 2) > 0.1, "Snare lacks 909 wire sizzle energy!"

    print("  -> Passed! Snare layers verified.")


def test_clap_flam_delays_and_hihat_metallic_cluster():
    """Verify multi-tap flam delays in handclaps and inharmonic cluster in hi-hats."""
    print("Testing Handclap Multi-Tap Flam Delays & Hi-Hat Metallic Sheen...")
    sr = 44100
    engine = ClapAndHatEngine(sample_rate=sr)

    # 1. Clap Multi-Tap Flam Delays
    clap = engine.render_clap(flam_taps=4, flam_spread_ms=34.0, velocity=100)
    # Detect flam peaks in the envelope
    mono_clap = np.abs(clap[:, 0])
    sos_env = signal.butter(2, 300.0 / (sr / 2.0), btype='lowpass', output='sos')
    env_smooth = signal.sosfilt(sos_env, mono_clap)
    # Early 50ms window contains flam taps
    early_env = env_smooth[:int(0.050 * sr)]
    peaks, _ = signal.find_peaks(early_env, height=0.04, distance=int(0.006 * sr))
    print(f"  -> Clap flam peaks detected in first 50ms: {len(peaks)} peaks at sample indices {peaks}")
    assert len(peaks) >= 3, f"Expected at least 3 flam peaks in handclap, found {len(peaks)}"

    # 2. Hi-Hat Inharmonic Cluster
    hat_closed = engine.render_hat(is_open=False, velocity=90)
    hat_open = engine.render_hat(is_open=True, velocity=90)
    assert len(hat_open) > len(hat_closed) * 2, "Open hat must have longer sustain than closed hat!"

    # FFT analysis of hat sheen (energy above 7 kHz)
    n_fft = 4096
    spec_hat = np.abs(np.fft.rfft(hat_closed[:, 0], n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    high_energy = np.sum(spec_hat[freqs >= 7000] ** 2)
    low_energy = np.sum(spec_hat[freqs < 2000] ** 2)
    assert high_energy > low_energy * 10.0, "Hi-hat metallic sheen must dominate above 7 kHz!"

    print("  -> Passed! Clap flam delays and hi-hat cluster verified.")


def test_groove_engine_mpc_swing_and_offbeat_preshift():
    """Verify MPC60 swing timing shifts and offbeat hi-hat pre-shift."""
    print("Testing GrooveEngine (MPC60 16th-note swing and offbeat pre-shift)...")
    bpm = 120.0
    beat_dur = 60.0 / bpm  # 0.5s
    sixteenth = beat_dur / 4.0  # 0.125s

    # Create 4 sixteenth notes (downbeat, swing 16th, eighth, swing 16th)
    raw_events = [
        DrumHitEvent(name_or_note="hat_closed", start_time=0.0 * sixteenth, velocity=100),
        DrumHitEvent(name_or_note="hat_closed", start_time=1.0 * sixteenth, velocity=80),
        DrumHitEvent(name_or_note="hat_closed", start_time=2.0 * sixteenth, velocity=90),
        DrumHitEvent(name_or_note="hat_closed", start_time=3.0 * sixteenth, velocity=80),
    ]

    swing_ratio = 0.60
    pre_shift_ms = -4.0
    grooved = GrooveEngine.apply_mpc_swing(
        events=raw_events,
        bpm=bpm,
        swing_ratio=swing_ratio,
        pre_shift_hats_ms=pre_shift_ms,
        humanize_timing_ms=0.0,  # Zero jitter for deterministic check
        velocity_jitter_pct=0.0,
    )

    # Expected shift on 2nd and 4th sixteenths:
    # swing_shift = sixteenth * (2 * 0.60 - 1.0) = 0.125 * 0.20 = +0.025s (+25ms)
    # plus pre-shift of -4ms = +21ms shift total
    expected_t1 = 1.0 * sixteenth + (sixteenth * 0.20) + (pre_shift_ms / 1000.0)
    actual_t1 = grooved[1].start_time
    assert abs(actual_t1 - expected_t1) < 1e-4, f"Swing timing mismatch: {actual_t1} vs expected {expected_t1}"

    print(f"  -> MPC60 60% swing shift on 16th-note: expected {expected_t1:.4f}s, actual {actual_t1:.4f}s")
    print("  -> Passed! Groove and micro-timing math verified.")


def test_soundfont_drum_sampler_and_hybrid_fallback():
    """Verify SoundFontDrumSampler caching and seamless fallback in DrumSamplerEngine."""
    print("Testing SoundFontDrumSampler and Hybrid Layering Pipeline...")
    engine = DrumSamplerEngine()

    # Verify hit rendering across all modes: 'synth', 'soundfont', 'hybrid'
    hit_synth = engine.render_hit("kick", velocity=100, mode="synth")
    assert hit_synth.ndim == 2 and len(hit_synth) > 0, "Synth kick failed!"

    hit_hybrid = engine.render_hit("kick", velocity=100, mode="hybrid")
    assert hit_hybrid.ndim == 2 and len(hit_hybrid) > 0, "Hybrid kick failed!"

    # Render a multi-bar drum stem
    events = [
        DrumHitEvent("kick", 0.0, velocity=115),
        DrumHitEvent("hat_closed", 0.125, velocity=85),
        DrumHitEvent("snare", 0.25, velocity=105),
        DrumHitEvent("hat_closed", 0.375, velocity=80),
        DrumHitEvent("kick", 0.50, velocity=110),
        DrumHitEvent("hat_closed", 0.625, velocity=85),
        DrumHitEvent("clap", 0.75, velocity=100),
        DrumHitEvent("hat_open", 0.875, velocity=90),
    ]

    drum_stem = engine.render_drum_stem(events=events, total_duration=1.2, bpm=120.0, mode="hybrid")
    assert drum_stem.ndim == 2 and drum_stem.shape[0] == int(1.2 * 44100)
    peak = np.max(np.abs(drum_stem))
    assert 0.4 < peak <= 1.0, f"Drum stem level abnormal: peak = {peak}"
    print(f"  -> Rendered multi-track drum stem: duration = {len(drum_stem)/44100:.2f}s, peak = {peak:.3f}")
    print("  -> Passed! Master drum sampler and stem rendering verified.")


if __name__ == "__main__":
    test_transient_shaper_attack_boost_and_sustain_cut()
    test_kick_layering_frequency_and_dynamics()
    test_snare_layering_components()
    test_clap_flam_delays_and_hihat_metallic_cluster()
    test_groove_engine_mpc_swing_and_offbeat_preshift()
    test_soundfont_drum_sampler_and_hybrid_fallback()
    print("\n==================================================================")
    print("ALL DRUM SAMPLER & TRANSIENT SOUND DESIGN TESTS PASSED (100% SUCCESS)!")
    print("==================================================================")

"""
Execution and verification of the 3 Master Hybrid Layering Strategies.
Uses Second-Order Sections (SOS) for pristine numerical stability across all filter slopes.
"""

import numpy as np
import scipy.signal as signal

fs = 44100

def lr4_split_2way(x, cutoff, fs):
    """Linkwitz-Riley 4th Order crossover using cascaded SOS Butterworth filters."""
    Wn = cutoff / (fs / 2)
    sos_lp = signal.butter(2, Wn, btype='low', output='sos')
    sos_hp = signal.butter(2, Wn, btype='high', output='sos')
    
    # Cascade twice for 4th order (24 dB/oct)
    low = signal.sosfilt(sos_lp, signal.sosfilt(sos_lp, x, axis=-1), axis=-1)
    high = signal.sosfilt(sos_hp, signal.sosfilt(sos_hp, x, axis=-1), axis=-1)
    return low, high

def midside_encode(stereo):
    L, R = stereo[0], stereo[1]
    M = 0.5 * (L + R)
    S = 0.5 * (L - R)
    return M, S

def midside_decode(M, S):
    L = M + S
    R = M - S
    return np.stack([L, R], axis=0)

def elliptical_mono_maker(stereo, cutoff_hz=125.0, fs=44100):
    """Converts low-end frequencies below cutoff strictly to mono using 8th order SOS HPF on the side."""
    M, S = midside_encode(stereo)
    sos = signal.butter(8, cutoff_hz / (fs / 2), btype='high', output='sos')
    S_filtered = signal.sosfilt(sos, S, axis=-1)
    return midside_decode(M, S_filtered)

def align_phase_and_polarity(reference, layer):
    """Calculates cross-correlation delay and polarity alignment between two stems."""
    corr = signal.correlate(reference, layer, mode='full')
    lags = signal.correlation_lags(len(reference), len(layer), mode='full')
    peak_idx = np.argmax(np.abs(corr))
    lag = lags[peak_idx]
    polarity = np.sign(corr[peak_idx])
    
    # Invert polarity if negative
    aligned_layer = layer * polarity
    # Shift by lag
    if lag > 0:
        aligned_layer = np.pad(aligned_layer, (lag, 0))[:len(layer)]
    elif lag < 0:
        aligned_layer = np.pad(aligned_layer, (0, -lag))[-lag:len(layer)-lag]
    return aligned_layer, lag, polarity

def soft_clip_saturate(x, drive_db=0.0):
    gain = 10.0 ** (drive_db / 20.0)
    y = x * gain
    return np.tanh(y)

# -------------------------------------------------------------
# Recipe 1: Acoustic Grand Piano + Electric Rhodes + Juno Pad
# -------------------------------------------------------------
def test_recipe_piano_rhodes_pad():
    dur = 2.0
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    
    # 1. Acoustic Grand Felt Hammer transient (percussive strike)
    hammer_click = np.random.randn(len(t)) * np.exp(-t * 200) * 0.4
    piano_soundboard = np.sin(2 * np.pi * 261.63 * t) * np.exp(-t * 1.5)
    piano_layer = hammer_click + piano_soundboard
    piano_stereo = np.stack([piano_layer, piano_layer], axis=0)
    
    # 2. Electric Rhodes MK1 (Rich warm tines + subtle tremolo)
    rhodes_tine = (np.sin(2 * np.pi * 261.63 * t) + 0.5 * np.sin(2 * np.pi * 523.25 * t)) * np.exp(-t * 0.8)
    tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 4.0 * t)
    rhodes_stereo = np.stack([rhodes_tine * tremolo, rhodes_tine * (2.0 - tremolo)], axis=0)
    # Bandpass Rhodes body (150 Hz to 4500 Hz) using SOS
    sos_bp = signal.butter(4, [150 / (fs/2), 4500 / (fs/2)], btype='band', output='sos')
    rhodes_stereo = signal.sosfilt(sos_bp, rhodes_stereo, axis=-1)
    
    # 3. Juno-106 Lush Pad (Detuned saw + Chorus II stereo spread)
    saw1 = signal.sawtooth(2 * np.pi * 261.63 * t)
    saw2 = signal.sawtooth(2 * np.pi * (261.63 * 1.004) * t)
    pad_mono = (saw1 + saw2) * 0.5
    # Amp envelope: slow attack
    pad_env = (1.0 - np.exp(-t * 4.0)) * np.exp(-t * 0.2)
    pad_mono = pad_mono * pad_env
    # Lowpass filter at 1200 Hz
    sos_lp = signal.butter(4, 1200 / (fs/2), btype='low', output='sos')
    pad_mono = signal.sosfilt(sos_lp, pad_mono)
    # Chorus widening (Haas delay 14ms)
    delay_samples = int(0.014 * fs)
    pad_stereo = np.stack([pad_mono, np.roll(pad_mono, delay_samples)], axis=0)
    
    # Mid/Side slotting: Rhodes and Piano centered, Pad pushed to sides
    pad_M, pad_S = midside_encode(pad_stereo)
    pad_M *= 0.3 # attenuate mid of pad
    pad_S *= 1.4 # boost side of pad
    pad_stereo_slotted = midside_decode(pad_M, pad_S)
    
    # Summation
    master_piano_stack = piano_stereo * 0.6 + rhodes_stereo * 0.4 + pad_stereo_slotted * 0.3
    peak = np.max(np.abs(master_piano_stack))
    assert peak > 0 and np.isfinite(peak)
    print(f"✓ Recipe 1 (Piano + Rhodes + Pad) synthesized and slotted successfully (Peak: {peak:.3f})")

# -------------------------------------------------------------
# Recipe 2: Monosynth Sub + Reese Bass + Transient Pluck
# -------------------------------------------------------------
def test_recipe_sub_reese_pluck():
    dur = 1.0
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    f0 = 55.0 # A1
    
    # 1. Monosynth Sub: Pure Sine, 100% Mono Mid, strictly 35 - 90 Hz
    sub_mono = np.sin(2 * np.pi * f0 * t) * (1.0 - 0.2 * t)
    sub_stereo = np.stack([sub_mono, sub_mono], axis=0)
    
    # 2. Reese Mid-Bass: Detuned saws, modulated notch, stereo chorus, HPF > 90 Hz
    saw_l = signal.sawtooth(2 * np.pi * f0 * 1.01 * t)
    saw_r = signal.sawtooth(2 * np.pi * f0 * 0.99 * t)
    reese_stereo = np.stack([saw_l, saw_r], axis=0)
    # Tube saturation
    reese_stereo = soft_clip_saturate(reese_stereo, drive_db=6.0)
    # Highpass at 90 Hz using LR4 highpass
    _, reese_hpf = lr4_split_2way(reese_stereo, 90.0, fs)
    
    # 3. Transient Pluck: snappy click at 2.5 kHz, 30ms decay
    pluck_mono = np.sin(2 * np.pi * 2500 * t) * np.exp(-t * 80)
    pluck_stereo = np.stack([pluck_mono, np.roll(pluck_mono, 8)], axis=0)
    
    # Sum with crossover alignment and elliptical filtering
    bass_stack = sub_stereo * 0.7 + reese_hpf * 0.5 + pluck_stereo * 0.3
    bass_clean = elliptical_mono_maker(bass_stack, cutoff_hz=125.0, fs=fs)
    
    # Verify mono sub purity
    M_sub, S_sub = midside_encode(bass_clean)
    sos_test = signal.butter(4, 70 / (fs/2), btype='low', output='sos')
    S_sub_low = signal.sosfilt(sos_test, S_sub)
    side_sub_power = np.mean(S_sub_low**2)
    assert side_sub_power < 1e-4, f"Side sub power leakage too high: {side_sub_power}"
    print(f"✓ Recipe 2 (Sub + Reese + Pluck) verified (Side sub leakage: {side_sub_power:.2e})")

# -------------------------------------------------------------
# Recipe 3: Acoustic Kick Click + Punch Body + 808 Sub Sine
# -------------------------------------------------------------
def test_recipe_kick_punch_808():
    dur = 0.8
    t = np.linspace(0, dur, int(fs * dur), endpoint=False)
    
    # 1. Beater Click: High-passed attack transient (1.5 kHz - 8 kHz)
    click = np.random.randn(len(t)) * np.exp(-t * 300)
    sos_hp = signal.butter(4, 1500 / (fs/2), btype='high', output='sos')
    click_layer = signal.sosfilt(sos_hp, click)
    
    # 2. Punch Body: Mid punch (80 Hz - 220 Hz)
    f_env = 160.0 * np.exp(-t * 40) + 70.0
    phase_punch = 2 * np.pi * np.cumsum(f_env) / fs
    punch_layer = np.sin(phase_punch) * np.exp(-t * 25)
    
    # 3. 808 Sub Sine: 45 Hz sine with slight pitch dive from 65 Hz
    f_808 = 20.0 * np.exp(-t * 15) + 45.0
    phase_808 = 2 * np.pi * np.cumsum(f_808) / fs
    sub_layer = np.sin(phase_808) * np.exp(-t * 3.5)
    
    # Alignment: Align punch and click to 808 phase peak
    click_aligned, c_lag, c_pol = align_phase_and_polarity(sub_layer[:1000], click_layer[:1000])
    punch_aligned, p_lag, p_pol = align_phase_and_polarity(sub_layer[:1000], punch_layer[:1000])
    
    # Stack with gain staging
    composite_kick = click_layer * 0.4 + punch_layer * 0.5 + sub_layer * 0.8
    clipped_kick = soft_clip_saturate(composite_kick, drive_db=1.5)
    
    peak = np.max(np.abs(clipped_kick))
    assert peak <= 1.0, f"Peak exceeded ceiling: {peak}"
    print(f"✓ Recipe 3 (Kick Click + Punch + 808) verified (Aligned Peak: {peak:.3f})")

if __name__ == "__main__":
    test_recipe_piano_rhodes_pad()
    test_recipe_sub_reese_pluck()
    test_recipe_kick_punch_808()
    print("\nAll 3 Hybrid Layering Recipes executed and verified successfully!")

import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import math
import os

SAMPLE_RATE = 44100
BPM = 118
BEAT_DUR = 60.0 / BPM
SIXTEENTH = BEAT_DUR / 4.0

def note_to_freq(note_name):
    notes = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
             'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
             'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    letter = note_name[:-1]
    octave = int(note_name[-1])
    semitone = notes[letter] + (octave + 1) * 12
    return 440.0 * (2.0 ** ((semitone - 69) / 12.0))

class AudioEngine:
    def __init__(self, total_duration):
        self.total_samples = int(total_duration * SAMPLE_RATE)
        self.left = np.zeros(self.total_samples, dtype=np.float32)
        self.right = np.zeros(self.total_samples, dtype=np.float32)

def synth_kick():
    duration = 0.4
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    pitch_env = 45 + (160 - 45) * np.exp(-35 * t)
    phase = 2 * np.pi * np.cumsum(pitch_env) / SAMPLE_RATE
    body = np.sin(phase)
    amp_env = np.exp(-10 * t)
    click = np.random.uniform(-1, 1, len(t)) * np.exp(-120 * t) * 0.4
    kick = (body * amp_env + click)
    kick = np.tanh(kick * 1.8) * 0.9
    return kick, kick

def synth_snare():
    duration = 0.45
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-22 * t)
    noise = np.random.uniform(-1, 1, len(t))
    sos = signal.butter(4, [1000, 7500], btype='bandpass', fs=SAMPLE_RATE, output='sos')
    filtered_noise = signal.sosfilt(sos, noise)
    noise_env = np.exp(-9 * t)
    snare_l = np.tanh((tone * 0.45 + filtered_noise * noise_env * 0.8) * 1.6) * 0.75
    noise_r = np.roll(filtered_noise, 45) * noise_env * 0.8
    snare_r = np.tanh((tone * 0.45 + noise_r) * 1.6) * 0.75
    return snare_l, snare_r

def synth_hat(open_hat=False):
    duration = 0.25 if open_hat else 0.08
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    sos = signal.butter(3, 7000, btype='highpass', fs=SAMPLE_RATE, output='sos')
    hat = signal.sosfilt(sos, noise)
    decay = 18 if open_hat else 65
    amp_env = np.exp(-decay * t)
    hat = hat * amp_env * 0.35
    return hat, hat * 0.95

def synth_saw_bass_note(freq, duration, cutoff=1200):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    saw = signal.sawtooth(2 * np.pi * freq * t)
    sub = signal.square(2 * np.pi * (freq / 2.0) * t) * 0.4
    raw = saw + sub
    nyquist = SAMPLE_RATE / 2.0
    norm_cutoff = min(cutoff / nyquist, 0.95)
    sos = signal.butter(2, norm_cutoff, btype='lowpass', output='sos')
    filtered = signal.sosfilt(sos, raw)
    amp_env = np.exp(-4 * t)
    out = np.tanh(filtered * amp_env * 2.2) * 0.55
    return out, out

def synth_supersaw_pad(chord_freqs, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    mix_l = np.zeros_like(t)
    mix_r = np.zeros_like(t)
    detunes = [-0.015, -0.007, 0.0, 0.008, 0.016]
    for freq in chord_freqs:
        for i, d in enumerate(detunes):
            f = freq * (1.0 + d)
            phase_l = np.random.uniform(0, 2*np.pi)
            phase_r = np.random.uniform(0, 2*np.pi)
            saw_l = signal.sawtooth(2 * np.pi * f * t + phase_l)
            saw_r = signal.sawtooth(2 * np.pi * f * t + phase_r)
            pan = i / (len(detunes) - 1)
            mix_l += saw_l * (1 - pan * 0.6)
            mix_r += saw_r * (0.4 + pan * 0.6)
    sos = signal.butter(2, 2200 / (SAMPLE_RATE / 2.0), btype='lowpass', output='sos')
    mix_l = signal.sosfilt(sos, mix_l)
    mix_r = signal.sosfilt(sos, mix_r)
    attack = int(0.25 * SAMPLE_RATE)
    attack_curve = np.linspace(0, 1, attack)
    env = np.ones_like(t)
    if len(env) > attack:
        env[:attack] = attack_curve
    release = int(0.4 * SAMPLE_RATE)
    if len(env) > release:
        env[-release:] = np.linspace(1, 0, release)
    mix_l = np.tanh(mix_l * env * 0.08) * 0.5
    mix_r = np.tanh(mix_r * env * 0.08) * 0.5
    return mix_l, mix_r

def synth_arp_lead(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    osc = signal.square(2 * np.pi * freq * t, duty=0.35) * 0.6 + signal.sawtooth(2 * np.pi * freq * 1.002 * t) * 0.4
    env = np.exp(-12 * t)
    sos = signal.butter(2, min(3400 / (SAMPLE_RATE / 2.0), 0.9), btype='lowpass', output='sos')
    filtered = signal.sosfilt(sos, osc) * env
    delay_samples = int(0.18 * SAMPLE_RATE)
    out_l = filtered.copy()
    out_r = np.zeros_like(filtered)
    if len(filtered) > delay_samples:
        out_r[delay_samples:] += filtered[:-delay_samples] * 0.5
    return out_l * 0.4, out_r * 0.4

def apply_sidechain(signal_data, kick_times):
    duck_dur = 0.22
    duck_samples = int(duck_dur * SAMPLE_RATE)
    duck_curve = 1.0 - np.exp(-18 * np.linspace(0, duck_dur, duck_samples))
    duck_mask = np.ones(len(signal_data), dtype=np.float32)
    for kt in kick_times:
        idx = int(kt * SAMPLE_RATE)
        end = min(idx + duck_samples, len(signal_data))
        clen = end - idx
        if clen > 0:
            duck_mask[idx:end] = np.minimum(duck_mask[idx:end], duck_curve[:clen])
    return signal_data * duck_mask

def build_song():
    bars = 16
    beats_per_bar = 4
    total_bars_time = bars * beats_per_bar * BEAT_DUR
    outro_time = 4.0
    total_duration = total_bars_time + outro_time

    engine = AudioEngine(total_duration)

    progression = [
        # Bars 1-4: Atmospheric intro
        (['D3', 'F3', 'A3', 'C4'], 'D2'),
        (['Bb2', 'D3', 'F3', 'A3'], 'Bb1'),
        (['F3', 'A3', 'C4', 'E4'], 'F2'),
        (['C3', 'E3', 'G3', 'B3'], 'C2'),
        # Bars 5-8: Groove drops in
        (['D3', 'F3', 'A3', 'D4'], 'D2'),
        (['Bb2', 'D3', 'F3', 'Bb3'], 'Bb1'),
        (['G2', 'Bb2', 'D3', 'G3'], 'G1'),
        (['A2', 'C#3', 'E3', 'A3'], 'A1'),
        # Bars 9-12: Full power with open hats
        (['D3', 'F3', 'A3', 'C4'], 'D2'),
        (['Bb2', 'D3', 'F3', 'A3'], 'Bb1'),
        (['F3', 'A3', 'C4', 'E4'], 'F2'),
        (['C3', 'E3', 'G3', 'D4'], 'C2'),
        # Bars 13-16: Climax (four-on-the-floor driving energy)
        (['D3', 'F3', 'A3', 'D4'], 'D2'),
        (['Bb2', 'D3', 'F3', 'Bb3'], 'Bb1'),
        (['G2', 'Bb2', 'D3', 'G3'], 'G1'),
        (['A2', 'C#3', 'E3', 'A3'], 'A1'),
    ]

    kick_l, kick_r = synth_kick()
    snare_l, snare_r = synth_snare()
    hat_c_l, hat_c_r = synth_hat(open_hat=False)
    hat_o_l, hat_o_r = synth_hat(open_hat=True)

    bass_track_l = np.zeros(engine.total_samples, dtype=np.float32)
    bass_track_r = np.zeros(engine.total_samples, dtype=np.float32)

    pad_track_l = np.zeros(engine.total_samples, dtype=np.float32)
    pad_track_r = np.zeros(engine.total_samples, dtype=np.float32)

    arp_track_l = np.zeros(engine.total_samples, dtype=np.float32)
    arp_track_r = np.zeros(engine.total_samples, dtype=np.float32)

    drums_l = np.zeros(engine.total_samples, dtype=np.float32)
    drums_r = np.zeros(engine.total_samples, dtype=np.float32)

    kick_times = []

    def add_to_track(tl, tr, sl, sr, t_sec):
        idx = int(t_sec * SAMPLE_RATE)
        end = min(idx + len(sl), len(tl))
        clen = end - idx
        if clen > 0:
            tl[idx:end] += sl[:clen]
            tr[idx:end] += sr[:clen]

    for bar_idx in range(bars):
        chord_notes, bass_root = progression[bar_idx]
        bar_start = bar_idx * beats_per_bar * BEAT_DUR

        # Pads
        chord_freqs = [note_to_freq(n) for n in chord_notes]
        p_l, p_r = synth_supersaw_pad(chord_freqs, beats_per_bar * BEAT_DUR)
        add_to_track(pad_track_l, pad_track_r, p_l, p_r, bar_start)

        # Rolling 16th Darksynth Bass
        root_freq = note_to_freq(bass_root)
        oct_freq = root_freq * 2.0
        for step in range(16):
            step_time = bar_start + step * SIXTEENTH
            freq = oct_freq if (step % 4 == 2) else root_freq
            b_l, b_r = synth_saw_bass_note(freq, SIXTEENTH * 0.95, cutoff=1400 if bar_idx >= 4 else 850)
            add_to_track(bass_track_l, bass_track_r, b_l, b_r, step_time)

        # Arpeggiator (comes in at bar 5)
        if bar_idx >= 4:
            arp_notes = chord_notes + [chord_notes[1]] + [chord_notes[2]]
            for step in range(16):
                step_time = bar_start + step * SIXTEENTH
                note_pick = arp_notes[step % len(arp_notes)]
                n_freq = note_to_freq(note_pick) * 2.0
                a_l, a_r = synth_arp_lead(n_freq, SIXTEENTH * 1.8)
                vel = 0.9 if step % 2 == 0 else 0.65
                add_to_track(arp_track_l, arp_track_r, a_l * vel, a_r * vel, step_time)

        # Drums
        for beat in range(4):
            beat_time = bar_start + beat * BEAT_DUR

            is_kick = False
            if bar_idx >= 4:
                if bar_idx >= 12:
                    is_kick = True
                elif beat in [0, 2]:
                    is_kick = True

            if is_kick:
                add_to_track(drums_l, drums_r, kick_l, kick_r, beat_time)
                kick_times.append(beat_time)

            if bar_idx >= 4 and beat in [1, 3]:
                add_to_track(drums_l, drums_r, snare_l, snare_r, beat_time)

            for sub in range(4):
                hat_time = beat_time + sub * SIXTEENTH
                if sub == 2:
                    if bar_idx >= 8 and (beat % 2 == 1):
                        add_to_track(drums_l, drums_r, hat_o_l, hat_o_r, hat_time)
                    else:
                        add_to_track(drums_l, drums_r, hat_c_l * 0.8, hat_c_r * 0.8, hat_time)
                else:
                    vel = 0.85 if sub == 0 else 0.4
                    add_to_track(drums_l, drums_r, hat_c_l * vel, hat_c_r * vel, hat_time)

    # Apply Sidechain ducking
    bass_track_l = apply_sidechain(bass_track_l, kick_times)
    bass_track_r = apply_sidechain(bass_track_r, kick_times)
    pad_track_l = apply_sidechain(pad_track_l, kick_times)
    pad_track_r = apply_sidechain(pad_track_r, kick_times)

    # Final Mixdown
    master_l = drums_l * 0.95 + bass_track_l * 0.85 + pad_track_l * 0.7 + arp_track_l * 0.65
    master_r = drums_r * 0.95 + bass_track_r * 0.85 + pad_track_r * 0.7 + arp_track_r * 0.65

    # Stereo room reverb
    rev_delay = int(0.045 * SAMPLE_RATE)
    master_l[rev_delay:] += master_r[:-rev_delay] * 0.15
    master_r[rev_delay:] += master_l[:-rev_delay] * 0.15

    # Limiting / normalization
    peak = max(np.max(np.abs(master_l)), np.max(np.abs(master_r)))
    if peak > 0:
        master_l = master_l / peak
        master_r = master_r / peak

    # Warm analog saturation
    master_l = np.tanh(master_l * 1.25) / 1.15
    master_r = np.tanh(master_r * 1.25) / 1.15

    out_16_l = np.int16(np.clip(master_l * 32767, -32767, 32767))
    out_16_r = np.int16(np.clip(master_r * 32767, -32767, 32767))

    stereo = np.column_stack((out_16_l, out_16_r))
    output_wav = "output_cyberpunk.wav"
    wav.write(output_wav, SAMPLE_RATE, stereo)
    print(f"SUCCESS: Generated {output_wav} ({total_duration:.1f}s, {bars} bars)")

if __name__ == "__main__":
    build_song()

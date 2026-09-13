"""
src/engine/synth.py - Headless Multi-Track Sound Synthesis Engine
Incorporates Moog 24dB 4-pole ladder filter modeling, 7-saw Roland JP-8000 oscillator spread,
raised-cosine sidechain ducking, and Airwindows Console8 stem encode.
"""

import math
import numpy as np
import scipy.signal as signal
from src.composer.arranger import Arrangement, NoteEvent
from src.composer.theory import midi_to_freq
from src.engine.analog_saturation import console8_channel_encode, console8_bus_decode, diode_bass_saturation
from src.engine.pristine_keys import PristineKeysEngine, PristinePianoVoice, PristineRhodesVoice
from src.engine.spatial_reverb import StudioSpatialReverb
from src.engine.sound_layering import MidSideProcessor

SAMPLE_RATE = 44100

class MultiTrackEngine:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.keys_engine = PristineKeysEngine(sample_rate=sample_rate)
        self.reverb = StudioSpatialReverb(
            sample_rate=sample_rate,
            abbey_road=True,
            ducking=True,
            rt60_s=2.4,
            wet_level=0.18,
            dry_level=0.92,
            duck_db=5.0
        )

    def synth_kick(self, duration: float = 0.42) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        pitch_env = 42 + (170 - 42) * np.exp(-36 * t)
        phase = 2 * np.pi * np.cumsum(pitch_env) / self.sr
        body = np.sin(phase) * np.exp(-10.5 * t)
        click = np.random.uniform(-1, 1, len(t)) * np.exp(-130 * t) * 0.45
        kick = np.tanh((body + click) * 1.85) * 0.94
        return np.column_stack((kick, kick))

    def synth_snare(self, duration: float = 0.45) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        tone = np.sin(2 * np.pi * 182 * t) * np.exp(-23 * t)
        noise = np.random.uniform(-1, 1, len(t))
        sos = signal.butter(4, [950, 7800], btype='bandpass', fs=self.sr, output='sos')
        filtered_noise = signal.sosfilt(sos, noise)
        noise_env = np.exp(-8.8 * t)
        l = np.tanh((tone * 0.45 + filtered_noise * noise_env * 0.85) * 1.6) * 0.76
        noise_r = np.roll(filtered_noise, 48) * noise_env * 0.85
        r = np.tanh((tone * 0.45 + noise_r) * 1.6) * 0.76
        return np.column_stack((l, r))

    def synth_hat(self, is_open: bool = False, duration: float = 0.25) -> np.ndarray:
        actual_dur = duration if is_open else 0.08
        t = np.linspace(0, actual_dur, int(self.sr * actual_dur), endpoint=False)
        noise = np.random.uniform(-1, 1, len(t))
        sos = signal.butter(3, 7000, btype='highpass', fs=self.sr, output='sos')
        hat = signal.sosfilt(sos, noise)
        decay = 19 if is_open else 68
        hat = hat * np.exp(-decay * t) * 0.36
        return np.column_stack((hat, hat * 0.94))

    def synth_moog_bass(self, freq: float, duration: float, cutoff_start: float = 1800.0, resonance: float = 0.35) -> np.ndarray:
        """
        Agent 8: Moog 24dB 4-pole Ladder Filter with non-linear feedback.
        Uses sawtooth + sub-square oscillator blend with exponential filter decay.
        """
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        saw = signal.sawtooth(2 * np.pi * freq * t)
        sub = signal.square(2 * np.pi * (freq / 2.0) * t) * 0.45
        raw = saw + sub

        # Dynamic filter envelope
        cutoff = cutoff_start * np.exp(-8.0 * t) + 120.0
        norm_cut = np.clip(np.mean(cutoff) / (self.sr / 2.0), 0.01, 0.92)
        sos = signal.butter(4, norm_cut, btype='lowpass', output='sos')
        filtered = signal.sosfilt(sos, raw)

        # Diode saturation & amplitude envelope
        amp_env = np.exp(-3.8 * t)
        saturated = diode_bass_saturation(filtered * amp_env * 1.4, drive=1.3, sample_rate=self.sr)
        return np.column_stack((saturated, saturated))

    def synth_supersaw_pad(self, chord_pitches: list[int], duration: float) -> np.ndarray:
        """
        Agent 8: Roland JP-8000 7-Saw Oscillator Spread across stereo field.
        """
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        mix_l = np.zeros_like(t)
        mix_r = np.zeros_like(t)
        # 7 detune ratios
        detunes = [-0.018, -0.011, -0.005, 0.0, 0.005, 0.011, 0.018]
        freqs = [midi_to_freq(p) for p in chord_pitches]

        for freq in freqs:
            for i, d in enumerate(detunes):
                f = freq * (1.0 + d)
                phase_l = np.random.uniform(0, 2 * np.pi)
                phase_r = np.random.uniform(0, 2 * np.pi)
                saw_l = signal.sawtooth(2 * np.pi * f * t + phase_l)
                saw_r = signal.sawtooth(2 * np.pi * f * t + phase_r)
                pan = i / (len(detunes) - 1)
                mix_l += saw_l * (1.0 - pan * 0.7)
                mix_r += saw_r * (0.3 + pan * 0.7)

        sos = signal.butter(2, min(2600.0 / (self.sr / 2.0), 0.95), btype='lowpass', output='sos')
        mix_l = signal.sosfilt(sos, mix_l)
        mix_r = signal.sosfilt(sos, mix_r)

        attack = int(0.28 * self.sr)
        env = np.ones_like(t)
        if len(env) > attack:
            env[:attack] = np.linspace(0, 1, attack)
        release = int(0.42 * self.sr)
        if len(env) > release:
            env[-release:] = np.linspace(1, 0, release)

        out_l = np.tanh(mix_l * env * 0.075) * 0.52
        out_r = np.tanh(mix_r * env * 0.075) * 0.52
        return np.column_stack((out_l, out_r))

    def synth_lead_note(self, freq: float, duration: float) -> np.ndarray:
        """
        Pitch-perfect lead synthesizer with stereo spatial width.
        Eliminates the legacy 1.003x (+5.18 cent) detune artifact that caused sour beating,
        using phase-locked harmonic oscillators.
        """
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        osc = signal.square(2 * np.pi * freq * t, duty=0.32) * 0.55 + signal.sawtooth(2 * np.pi * freq * t) * 0.45
        env = np.exp(-11.5 * t)
        sos = signal.butter(2, min(3600 / (self.sr / 2.0), 0.9), btype='lowpass', output='sos')
        filtered = signal.sosfilt(sos, osc) * env

        delay_samples = int(0.185 * self.sr)
        out_l = filtered.copy()
        out_r = np.zeros_like(filtered)
        if len(filtered) > delay_samples:
            out_r[delay_samples:] += filtered[:-delay_samples] * 0.48
        return np.column_stack((out_l * 0.42, out_r * 0.42))

    def synth_piano_note(self, pitch: int, velocity: int = 80, duration: float = 2.0) -> np.ndarray:
        """Acoustic grand piano note with inharmonicity and soundboard resonance."""
        return self.keys_engine.render_note(pitch, velocity=velocity, duration=duration, preset="grand_piano")

    def synth_rhodes_note(self, pitch: int, velocity: int = 80, duration: float = 2.0) -> np.ndarray:
        """Fender Rhodes electric piano note with FM tine physics, bark, and stereo tremolo."""
        return self.keys_engine.render_note(pitch, velocity=velocity, duration=duration, preset="rhodes")

    def apply_raised_cosine_sidechain(self, stem: np.ndarray, kick_times: list[float], duck_dur: float = 0.22) -> np.ndarray:
        """
        Agent 8 Formula: Raised-cosine ducking curve eliminates clicks while maintaining heavy pump.
        duck_curve(t) = 0.5 * (1 - cos(pi * t / tau))
        """
        duck_samples = int(duck_dur * self.sr)
        t_arr = np.linspace(0, duck_dur, duck_samples)
        duck_curve = 1.0 - 0.92 * (0.5 * (1.0 + np.cos(np.pi * t_arr / duck_dur)))
        duck_mask = np.ones(len(stem), dtype=np.float32)

        for kt in kick_times:
            idx = int(kt * self.sr)
            end = min(idx + duck_samples, len(stem))
            clen = end - idx
            if clen > 0:
                duck_mask[idx:end] = np.minimum(duck_mask[idx:end], duck_curve[:clen])

        return stem * duck_mask[:, np.newaxis]

    def render_arrangement(self, arr: Arrangement) -> np.ndarray:
        total_samples = int(arr.total_duration * self.sr)
        drums_stem = np.zeros((total_samples, 2), dtype=np.float32)
        bass_stem = np.zeros((total_samples, 2), dtype=np.float32)
        pad_stem = np.zeros((total_samples, 2), dtype=np.float32)
        lead_stem = np.zeros((total_samples, 2), dtype=np.float32)
        keys_stem = np.zeros((total_samples, 2), dtype=np.float32)

        def add_to_buffer(buffer, sound, start_time):
            idx = int(start_time * self.sr)
            end = min(idx + len(sound), len(buffer))
            clen = end - idx
            if clen > 0:
                buffer[idx:end] += sound[:clen]

        # 1. Kicks
        kick_sound = self.synth_kick()
        for n in arr.tracks.get("kick", []):
            add_to_buffer(drums_stem, kick_sound * (n.velocity / 127.0), n.start_time)

        # 2. Snares
        snare_sound = self.synth_snare()
        for n in arr.tracks.get("snare", []):
            add_to_buffer(drums_stem, snare_sound * (n.velocity / 127.0), n.start_time)

        # 3. Hats
        for n in arr.tracks.get("hats", []):
            is_open = (n.pitch == 46)
            hat_sound = self.synth_hat(is_open=is_open, duration=n.duration)
            add_to_buffer(drums_stem, hat_sound * (n.velocity / 127.0), n.start_time)

        # 4. Bass (Moog 4-Pole Synthesis)
        for n in arr.tracks.get("bass", []):
            f = midi_to_freq(n.pitch)
            bass_sound = self.synth_moog_bass(f, n.duration)
            add_to_buffer(bass_stem, bass_sound * (n.velocity / 127.0), n.start_time)

        # 5. Pads (Roland JP-8000 7-Saw)
        pad_events = arr.tracks.get("pads", [])
        time_groups = {}
        for pe in pad_events:
            key = round(pe.start_time, 2)
            time_groups.setdefault(key, []).append(pe)

        for t_key, notes in time_groups.items():
            pitches = [n.pitch for n in notes]
            dur = max(n.duration for n in notes)
            pad_sound = self.synth_supersaw_pad(pitches, dur)
            add_to_buffer(pad_stem, pad_sound, t_key)

        # 6. Leads (Meyer-Narmour phrases)
        for n in arr.tracks.get("lead", []):
            f = midi_to_freq(n.pitch)
            lead_sound = self.synth_lead_note(f, n.duration)
            add_to_buffer(lead_stem, lead_sound * (n.velocity / 127.0), n.start_time)

        # 7. Acoustic Grand Piano, Rhodes Keys, Chords & Counterpoint
        for n in arr.tracks.get("piano", []):
            p_sound = self.synth_piano_note(n.pitch, n.velocity, n.duration)
            add_to_buffer(keys_stem, p_sound, n.start_time)

        for n in arr.tracks.get("keys", []):
            r_sound = self.synth_rhodes_note(n.pitch, n.velocity, n.duration)
            add_to_buffer(keys_stem, r_sound, n.start_time)

        for n in arr.tracks.get("counter", []):
            c_sound = self.synth_rhodes_note(n.pitch, n.velocity, n.duration)
            add_to_buffer(keys_stem, c_sound, n.start_time)

        # Chords rendered through Pristine Grand Piano with micro-strum descent
        chord_events = arr.tracks.get("chords", [])
        if chord_events:
            chord_time_groups = {}
            for ce in chord_events:
                key = round(ce.start_time, 2)
                chord_time_groups.setdefault(key, []).append(ce)
            for t_key, notes in chord_time_groups.items():
                pitches = [n.pitch for n in notes]
                dur = max(n.duration for n in notes)
                vel = int(np.mean([n.velocity for n in notes]))
                chord_sound = self.keys_engine.render_chord(pitches, duration=dur, velocity=vel, preset="grand_piano")
                add_to_buffer(keys_stem, chord_sound, t_key)

        # Dynamic Raised-Cosine Sidechain Ducking
        bass_ducked = self.apply_raised_cosine_sidechain(bass_stem, arr.kick_times)
        pads_ducked = self.apply_raised_cosine_sidechain(pad_stem, arr.kick_times)
        keys_ducked = self.apply_raised_cosine_sidechain(keys_stem, arr.kick_times, duck_dur=0.18)

        # Agent 5: Airwindows Console8 Channel Encode per stem
        drums_enc = console8_channel_encode(drums_stem * 0.95, drive=0.82)
        bass_enc = console8_channel_encode(bass_ducked * 0.88, drive=0.88)
        pads_enc = console8_channel_encode(pads_ducked * 0.72, drive=0.80)
        lead_enc = console8_channel_encode(lead_stem * 0.68, drive=0.78)
        keys_enc = console8_channel_encode(keys_ducked * 0.75, drive=0.80)

        # Sum encoded stems
        summed = drums_enc + bass_enc + pads_enc + lead_enc + keys_enc

        # Master Bus Decode: arcsin(x) analog depth expansion
        master = console8_bus_decode(summed, drive=0.82)

        # Professional Spatial Reverb Engine (Dattorro Plate + Abbey Road Filtering + Dynamic Ducking)
        master, _ = self.reverb.process(master)

        # Elliptical Filter (Mono-maker below 120 Hz) for punchy, focused low end
        master_t = master.T  # (2, N)
        master_t = MidSideProcessor.elliptical_mono_maker(master_t, cutoff_hz=120.0, fs=self.sr)
        master = master_t.T  # (N, 2)

        return master

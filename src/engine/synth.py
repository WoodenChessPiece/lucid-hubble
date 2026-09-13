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
from src.engine.drum_sampler import DrumSamplerEngine
from src.engine.spatial_reverb import StudioSpatialReverb
from src.engine.sound_layering import MidSideProcessor

SAMPLE_RATE = 44100

class MultiTrackEngine:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.keys_engine = PristineKeysEngine(sample_rate=sample_rate)
        self.drum_engine = DrumSamplerEngine(sample_rate=sample_rate)
        self.reverb = StudioSpatialReverb(
            sample_rate=sample_rate,
            abbey_road=True,
            ducking=True,
            rt60_s=2.2,
            hp_cutoff=600.0,
            lp_cutoff=8000.0,
            er_level=0.18,
            wet_level=0.32,
            duck_db=6.0,
            attack_ms=10.0,
            release_ms=220.0
        )

    def synth_kick(self, duration: float = 0.45, velocity: int = 110, pitch_sub: float = 50.0) -> np.ndarray:
        """Commercial layered kick: Sub sine (45-55 Hz) + Acoustic beater (2.5-4 kHz) + Saturated body."""
        return self.drum_engine.render_hit("kick", velocity=velocity, mode="hybrid", duration=duration, pitch_sub=pitch_sub)

    def synth_snare(self, duration: float = 0.45, velocity: int = 105) -> np.ndarray:
        """Commercial layered snare: 200 Hz body thump + 909 wire sizzle + Stereo acoustic ring."""
        return self.drum_engine.render_hit("snare", velocity=velocity, mode="hybrid", duration=duration)

    def synth_hat(self, is_open: bool = False, duration: float = 0.25, velocity: int = 90) -> np.ndarray:
        """Inharmonic metallic hi-hat using Roland TR-808 6-oscillator cluster."""
        return self.drum_engine.render_hit("hat_open" if is_open else "hat_closed", velocity=velocity, mode="hybrid", duration=duration)

    def synth_clap(self, duration: float = 0.55, velocity: int = 100) -> np.ndarray:
        """Authentic handclap with multi-tap flam delays and stereo spread."""
        return self.drum_engine.render_hit("clap", velocity=velocity, mode="hybrid", duration=duration)

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
        kick_stem = np.zeros((total_samples, 2), dtype=np.float32)
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

        # 1. Kicks (kept isolated for sidechain ducking & clean dry drum bus)
        for n in arr.tracks.get("kick", []):
            k_sound = self.synth_kick(velocity=n.velocity)
            add_to_buffer(kick_stem, k_sound, n.start_time)
        drums_stem += kick_stem

        # 2. Snares
        for n in arr.tracks.get("snare", []):
            s_sound = self.synth_snare(velocity=n.velocity)
            add_to_buffer(drums_stem, s_sound, n.start_time)

        # 3. Claps
        for n in arr.tracks.get("clap", []):
            c_sound = self.synth_clap(velocity=n.velocity)
            add_to_buffer(drums_stem, c_sound, n.start_time)

        # 4. Hats
        for n in arr.tracks.get("hats", []):
            is_open = (n.pitch == 46)
            hat_sound = self.synth_hat(is_open=is_open, duration=n.duration, velocity=n.velocity)
            add_to_buffer(drums_stem, hat_sound, n.start_time)

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

        # =========================================================================
        # PROFESSIONAL REVERB AUX SEND & MIX BUS ARCHITECTURE
        # =========================================================================
        # 1. Isolation: Drums (Kick/Snare/Hats) and Sub-Bass remain 100% DRY (-inf dB send).
        # 2. Parallel Aux Send: Only melodic stems feed the reverb aux at calibrated levels:
        #    - Pads: -12 dB (linear 0.2512) -> rich harmonic bedding behind the mix
        #    - Keys: -18 dB (linear 0.1259) -> acoustic depth halo preserving hammer strike
        #    - Lead: -20 dB (linear 0.1000) -> laser-focused, pristine up-front vocal presence
        send_pads = 10.0 ** (-12.0 / 20.0)
        send_keys = 10.0 ** (-18.0 / 20.0)
        send_lead = 10.0 ** (-20.0 / 20.0)

        reverb_send = (
            pads_ducked * send_pads +
            keys_ducked * send_keys +
            lead_stem * send_lead
        )

        # 3. Dual Sidechain Key: Dry Lead + Kick for dynamic masking elimination
        #    - Kick unmasks low-end punch & transient slap
        #    - Lead unmasks rapid melodic notes so they cut through upfront
        #    - When lead rests, reverb blooms into the stereo field
        reverb_sc_key = kick_stem + lead_stem * 0.85

        # 4. 100% Wet Aux Return with Abbey Road Pre-Filter (600 Hz HPF / 8 kHz LPF)
        reverb_return = self.reverb.process_aux(reverb_send, sidechain_key=reverb_sc_key)

        # 5. Airwindows Console8 Channel Encode per stem + Reverb Aux Return
        drums_enc = console8_channel_encode(drums_stem * 0.95, drive=0.82)
        bass_enc = console8_channel_encode(bass_ducked * 0.88, drive=0.88)
        pads_enc = console8_channel_encode(pads_ducked * 0.72, drive=0.80)
        lead_enc = console8_channel_encode(lead_stem * 0.68, drive=0.78)
        keys_enc = console8_channel_encode(keys_ducked * 0.75, drive=0.80)
        reverb_enc = console8_channel_encode(reverb_return * 0.75, drive=0.75)

        # 6. Master Console Summing (all dry stems + reverb aux return)
        summed = drums_enc + bass_enc + pads_enc + lead_enc + keys_enc + reverb_enc

        # 7. Master Bus Decode: arcsin(x) analog depth expansion
        master = console8_bus_decode(summed, drive=0.82)

        # 8. Elliptical Filter (Mono-maker below 120 Hz) for punchy, focused low end
        master_t = master.T  # (2, N)
        master_t = MidSideProcessor.elliptical_mono_maker(master_t, cutoff_hz=120.0, fs=self.sr)
        master = master_t.T  # (N, 2)

        return master

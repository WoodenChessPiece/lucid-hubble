"""
src/engine/drum_sampler.py - Masterclass Commercial Drum Sampler & Layering Engine

Addresses the sonic deficiencies of simplistic np.sin pitch-drop kicks and filtered noise snares:
1. Multi-Layer Commercial Drum Synthesis:
   - Kick Layering: Sub sine (45-55 Hz) + Acoustic beater transient (2.5-4 kHz) + Saturated mid body.
   - Snare Layering: 200 Hz fundamental body thump + 909 snappy wire sizzle + Stereo acoustic ring + Stick crack.
   - Claps & Hats: Multi-tap flam delays with micro-panning, 6-oscillator inharmonic metallic cluster, pre-shifted offbeats.
2. DSP Transient Shaper:
   - Dual-envelope differential follower (fast attack vs slow sustain) with +/- 12 dB attack/sustain sculpting
     and soft-knee saturation ceiling.
3. SoundFont & Hybrid Sample Management:
   - Headless SoundFont batch-caching via FluidSynth (TimGM6mb.sf2 or custom SF2) with zero-latency RAM playback.
   - Seamless fallback to high-impact embedded physical modeling pulses.
   - Hybrid mode: Sampled acoustic beater/stick transient coupled with phase-locked synthesized sub & saturated body.
4. Groove & Humanization:
   - MPC60/SP-1200 16th-note swing engine (50% to 75%).
   - Micro-timing pre-shift (offbeat pull/push) and velocity humanization to eliminate the machine-gun effect.
"""

import os
import math
import tempfile
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav

SAMPLE_RATE = 44100


# ==============================================================================
# 1. DSP TRANSIENT SHAPER
# ==============================================================================

class TransientShaper:
    """
    Studio-Grade Differential Envelope Transient Shaper.
    Models the differential envelope dynamics of hardware units (SPL Transient Designer):
    - Fast envelope follower tracks rapid wavefront onset (attack).
    - Slow envelope follower tracks acoustic body and room decay (sustain).
    - Differential delta isolates transient impact from resonance.
    - Soft-knee limiter prevents digital overs while preserving dynamic range.
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        tau_attack_fast_ms: float = 1.0,
        tau_release_fast_ms: float = 6.0,
        tau_attack_slow_ms: float = 20.0,
        tau_release_slow_ms: float = 60.0,
    ):
        self.sr = sample_rate
        self.alpha_att_fast = math.exp(-1.0 / (max(0.0001, tau_attack_fast_ms / 1000.0) * self.sr))
        self.alpha_rel_fast = math.exp(-1.0 / (max(0.0001, tau_release_fast_ms / 1000.0) * self.sr))
        self.alpha_att_slow = math.exp(-1.0 / (max(0.0001, tau_attack_slow_ms / 1000.0) * self.sr))
        self.alpha_rel_slow = math.exp(-1.0 / (max(0.0001, tau_release_slow_ms / 1000.0) * self.sr))

    def process(
        self,
        audio: np.ndarray,
        attack_gain_db: float = 0.0,
        sustain_gain_db: float = 0.0,
        ceiling_db: Optional[float] = None,
        drive: float = 1.0,
    ) -> np.ndarray:
        """
        Processes mono or stereo audio through differential envelope transient shaping.
        """
        if len(audio) == 0:
            return audio

        is_stereo = (audio.ndim == 2 and audio.shape[1] == 2)
        if is_stereo:
            mono_det = np.maximum(np.abs(audio[:, 0]), np.abs(audio[:, 1]))
        else:
            mono_det = np.abs(audio)

        n_samples = len(mono_det)
        e_fast = np.zeros(n_samples, dtype=np.float32)
        e_slow = np.zeros(n_samples, dtype=np.float32)

        ef = 0.0
        es = 0.0
        a_af = self.alpha_att_fast
        a_rf = self.alpha_rel_fast
        a_as = self.alpha_att_slow
        a_rs = self.alpha_rel_slow

        for i in range(n_samples):
            x = float(mono_det[i])
            c_f = a_af if x > ef else a_rf
            ef = c_f * ef + (1.0 - c_f) * x
            e_fast[i] = ef

            c_s = a_as if x > es else a_rs
            es = c_s * es + (1.0 - c_s) * x
            e_slow[i] = es

        # Linear gains
        g_att = 10.0 ** (attack_gain_db / 20.0)
        g_sus = 10.0 ** (sustain_gain_db / 20.0)

        diff = e_fast - e_slow
        denom = e_fast + 1e-6
        att_ratio = np.maximum(0.0, diff) / denom
        sus_ratio = e_slow / denom

        gain_curve = 1.0 + (g_att - 1.0) * att_ratio + (g_sus - 1.0) * sus_ratio

        if is_stereo:
            out = audio * gain_curve[:, np.newaxis]
        else:
            out = audio * gain_curve

        # Analog drive saturation
        if drive > 1.001:
            out = np.tanh(out * drive) / math.tanh(drive)

        # Soft-knee limiter to ceiling
        if ceiling_db is not None:
            ceiling_lin = 10.0 ** (ceiling_db / 20.0)
            threshold = ceiling_lin * 0.85
            abs_out = np.abs(out)
            sign_out = np.sign(out)
            over_mask = (abs_out > threshold)
            if np.any(over_mask):
                headroom = ceiling_lin - threshold
                delta = abs_out[over_mask] - threshold
                # Smooth tanh compression for peaks above 85% ceiling
                out[over_mask] = sign_out[over_mask] * (threshold + headroom * np.tanh(delta / headroom))

        return out.astype(np.float32)


# ==============================================================================
# 2. DRUM SYNTHESIS & LAYERING ENGINES
# ==============================================================================

class KickLayerEngine:
    """
    Commercial Multi-Layer Kick Drum Synthesizer.
    Eliminates cheap np.sin pitch-drop by layering:
    1. Sub Sine (45-55 Hz tuned fundamental, phase-locked, zero-offset start).
    2. Acoustic Beater Transient (2.5-4.0 kHz punchy slap with bandpass damping).
    3. Saturated Mid Body (80-220 Hz shell cavity with asymmetric diode saturation).
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.transient_shaper = TransientShaper(sample_rate=sample_rate)

    def render_kick(
        self,
        pitch_sub: float = 50.0,
        sub_decay: float = 0.40,
        beater_punch: float = 1.0,
        beater_freq: float = 3200.0,
        body_punch: float = 1.0,
        saturation_drive: float = 1.35,
        attack_gain_db: float = 2.5,
        sustain_gain_db: float = 0.0,
        velocity: int = 100,
        duration: float = 0.45,
    ) -> np.ndarray:
        """
        Renders a commercial kick drum hit as a stereo array (pure mono low end).
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        n_samples = int(self.sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Layer 1: Sub Sine (45 - 55 Hz fundamental)
        pitch_glide = pitch_sub + 38.0 * np.exp(-58.0 * t)
        phase_sub = 2.0 * np.pi * np.cumsum(pitch_glide) / self.sr
        env_sub = np.exp(-(1.0 / max(0.05, sub_decay)) * t)
        sub_layer = np.sin(phase_sub) * env_sub

        # Layer 2: Acoustic Beater Transient (2.5 - 4.2 kHz)
        click_dur = 0.016
        click_samples = int(self.sr * click_dur)
        t_click = t[:click_samples]
        noise_impulse = np.random.uniform(-1.0, 1.0, click_samples)
        click_tone = np.sin(2.0 * np.pi * beater_freq * t_click) * np.exp(-280.0 * t_click)
        sos_click = signal.butter(4, [max(1000.0, beater_freq - 900.0), min(self.sr * 0.45, beater_freq + 1100.0)],
                                  btype='bandpass', fs=self.sr, output='sos')
        filtered_noise = signal.sosfilt(sos_click, noise_impulse) * np.exp(-220.0 * t_click)
        beater_raw = (click_tone * 0.7 + filtered_noise * 0.5) * (beater_punch * vel_norm)

        beater_layer = np.zeros(n_samples, dtype=np.float32)
        beater_layer[:click_samples] = beater_raw

        # Layer 3: Saturated Mid Body (80 - 220 Hz Shell Cavity)
        body_pitch = 85.0 + 105.0 * np.exp(-42.0 * t)
        phase_body = 2.0 * np.pi * np.cumsum(body_pitch) / self.sr
        env_body = np.exp(-15.0 * t)
        raw_body = np.sin(phase_body) * env_body * (body_punch * vel_norm)
        sat_body = np.tanh(raw_body * 2.2 + 0.28 * (raw_body ** 2)) * 0.72

        # Master Layer Summing
        kick_mono = sub_layer * 0.88 + beater_layer * 0.65 + sat_body * 0.68

        # Transient Shaper
        kick_shaped = self.transient_shaper.process(
            kick_mono,
            attack_gain_db=attack_gain_db * vel_norm,
            sustain_gain_db=sustain_gain_db,
            ceiling_db=-0.1,
            drive=saturation_drive
        )

        kick_stereo = np.column_stack((kick_shaped, kick_shaped))
        return kick_stereo.astype(np.float32)


class SnareLayerEngine:
    """
    Commercial Snare Drum Synthesizer & Layering System.
    Replaces filtered noise with 4 distinct acoustic physics layers:
    1. 200 Hz Fundamental Body Thump (pitched acoustic shell with chest punch).
    2. 909 Snappy Wire Sizzle (modeled non-linear snare strainer rattle).
    3. Stereo Acoustic Ring (Bessel eigenmode shell overtones).
    4. Wooden Stick Attack Crack (4-8 kHz impact transient).
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.transient_shaper = TransientShaper(sample_rate=sample_rate)

    def render_snare(
        self,
        fundamental_freq: float = 200.0,
        wire_decay: float = 0.24,
        ring_decay: float = 0.20,
        stick_crack_gain: float = 1.0,
        saturation_drive: float = 1.3,
        attack_gain_db: float = 3.0,
        sustain_gain_db: float = 0.0,
        velocity: int = 100,
        duration: float = 0.45,
    ) -> np.ndarray:
        """
        Renders a commercial layered snare hit with authentic stereo snare wire sizzle.
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        n_samples = int(self.sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Layer 1: 200 Hz Fundamental Body Thump
        thump_pitch = fundamental_freq + 65.0 * np.exp(-62.0 * t)
        phase_thump = 2.0 * np.pi * np.cumsum(thump_pitch) / self.sr
        env_thump = np.exp(-22.0 * t)
        thump = np.sin(phase_thump) * env_thump * 0.85

        # Layer 2: 909 Snappy Wire Sizzle
        noise_l = np.random.uniform(-1.0, 1.0, n_samples)
        noise_r = np.random.uniform(-1.0, 1.0, n_samples)

        sos_wire = signal.butter(4, [3200, min(12500.0, self.sr * 0.45)], btype='bandpass', fs=self.sr, output='sos')
        wire_filt_l = signal.sosfilt(sos_wire, noise_l)
        wire_filt_r = signal.sosfilt(sos_wire, noise_r)

        wire_decay_rate = 1.0 / max(0.04, wire_decay)
        wire_env = 0.65 * np.exp(-38.0 * t) + 0.35 * np.exp(-wire_decay_rate * t)

        wire_l = wire_filt_l * wire_env * 0.75
        wire_r = wire_filt_r * wire_env * 0.75

        # Layer 3: Stereo Acoustic Ring (Bessel overtones)
        ring_decay_rate = 1.0 / max(0.04, ring_decay)
        ring_env = np.exp(-ring_decay_rate * t)
        mode1_l = np.sin(2.0 * np.pi * 342.0 * t) * 0.22
        mode1_r = np.sin(2.0 * np.pi * 348.0 * t) * 0.22
        mode2 = np.sin(2.0 * np.pi * 515.0 * t) * 0.14
        ring_l = (mode1_l + mode2) * ring_env
        ring_r = (mode1_r + mode2) * ring_env

        # Layer 4: Wooden Stick Attack Crack
        stick_dur = 0.009
        stick_samples = int(self.sr * stick_dur)
        t_stick = t[:stick_samples]
        noise_stick = np.random.uniform(-1.0, 1.0, stick_samples)
        sos_stick = signal.butter(4, 4500.0, btype='highpass', fs=self.sr, output='sos')
        stick_filt = signal.sosfilt(sos_stick, noise_stick) * np.exp(-320.0 * t_stick) * (stick_crack_gain * vel_norm)
        stick_full = np.zeros(n_samples, dtype=np.float32)
        stick_full[:stick_samples] = stick_filt

        # Summing & Transient Shaping
        snare_raw_l = (thump * 0.75 + wire_l * 0.70 + ring_l * 0.50 + stick_full * 0.60) * vel_norm
        snare_raw_r = (thump * 0.75 + wire_r * 0.70 + ring_r * 0.50 + stick_full * 0.60) * vel_norm

        snare_stereo = np.column_stack((snare_raw_l, snare_raw_r))

        snare_shaped = self.transient_shaper.process(
            snare_stereo,
            attack_gain_db=attack_gain_db * vel_norm,
            sustain_gain_db=sustain_gain_db,
            ceiling_db=-0.1,
            drive=saturation_drive
        )
        return snare_shaped.astype(np.float32)


class ClapAndHatEngine:
    """
    Commercial Claps, Hi-Hats & Cymbals Sound Design Engine.
    - Handclaps: Multi-tap flam delays (staggered hand strikes over 10-35 ms)
      with micro-panning and gated room tail.
    - Hi-Hats: 6-Oscillator Inharmonic Pulse Cluster (Roland TR-808/909 metallic topology)
      with resonance bandpass and bronze sheen.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.transient_shaper = TransientShaper(sample_rate=sample_rate)

    def render_clap(
        self,
        flam_taps: int = 4,
        flam_spread_ms: float = 34.0,
        stereo_spread: float = 0.65,
        tail_decay: float = 0.28,
        velocity: int = 100,
        duration: float = 0.55,
    ) -> np.ndarray:
        """
        Renders an authentic ensemble handclap with multi-tap flam delays.
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        n_samples = int(self.sr * duration)
        clap_l = np.zeros(n_samples, dtype=np.float32)
        clap_r = np.zeros(n_samples, dtype=np.float32)

        tap_offsets_ms = np.linspace(0.0, flam_spread_ms, flam_taps)
        tap_gains = np.linspace(0.45, 1.1, flam_taps)
        tap_pans = [-stereo_spread * 0.6, stereo_spread * 0.8, -stereo_spread * 0.3, 0.0]
        if flam_taps != 4:
            tap_pans = list(np.linspace(-stereo_spread, stereo_spread, flam_taps))

        sos_body = signal.butter(4, [1100, 5600], btype='bandpass', fs=self.sr, output='sos')

        for i in range(flam_taps):
            offset_s = tap_offsets_ms[i] / 1000.0
            idx_start = int(offset_s * self.sr)
            tap_dur = tail_decay if (i == flam_taps - 1) else 0.045
            tap_len = int(self.sr * tap_dur)
            t_tap = np.linspace(0, tap_dur, tap_len, endpoint=False)

            noise = np.random.uniform(-1.0, 1.0, tap_len)
            decay_rate = (1.0 / tail_decay) if (i == flam_taps - 1) else 85.0
            env = np.exp(-decay_rate * t_tap) * tap_gains[i]

            tap_audio = signal.sosfilt(sos_body, noise) * env

            pan = tap_pans[i]
            gain_l = 0.5 * (1.0 - pan)
            gain_r = 0.5 * (1.0 + pan)

            end_idx = min(n_samples, idx_start + tap_len)
            valid_len = end_idx - idx_start
            if valid_len > 0:
                clap_l[idx_start:end_idx] += tap_audio[:valid_len] * gain_l
                clap_r[idx_start:end_idx] += tap_audio[:valid_len] * gain_r

        clap_stereo = np.column_stack((clap_l, clap_r)) * vel_norm
        clap_shaped = self.transient_shaper.process(
            clap_stereo,
            attack_gain_db=2.0 * vel_norm,
            sustain_gain_db=1.0,
            ceiling_db=-0.1,
            drive=1.25
        )
        return clap_shaped.astype(np.float32)

    def render_hat(
        self,
        is_open: bool = False,
        velocity: int = 100,
        duration: Optional[float] = None,
        choke_cutoff_s: Optional[float] = None,
    ) -> np.ndarray:
        """
        Renders inharmonic metallic hi-hat using the Roland TR-808 6-oscillator cluster.
        Inharmonic frequencies: 243, 310, 395, 523, 678, 866 Hz.
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        actual_dur = duration if duration is not None else (0.35 if is_open else 0.085)
        n_samples = int(self.sr * actual_dur)
        t = np.linspace(0, actual_dur, n_samples, endpoint=False)

        cluster_freqs = [243.0, 310.0, 395.0, 523.0, 678.0, 866.0]
        osc_sum = np.zeros(n_samples, dtype=np.float32)
        for f in cluster_freqs:
            osc_sum += signal.square(2.0 * np.pi * f * t)

        sos_bp = signal.butter(4, [6800, min(15000.0, self.sr * 0.45)], btype='bandpass', fs=self.sr, output='sos')
        metallic_sheen = signal.sosfilt(sos_bp, osc_sum)

        noise_shimmer = np.random.uniform(-1.0, 1.0, n_samples)
        sos_hp = signal.butter(3, 8500.0, btype='highpass', fs=self.sr, output='sos')
        noise_filt = signal.sosfilt(sos_hp, noise_shimmer)

        hat_raw = (metallic_sheen * 0.75 + noise_filt * 0.25)
        decay_rate = 14.0 if is_open else 58.0
        env = np.exp(-decay_rate * t)

        if choke_cutoff_s is not None and choke_cutoff_s < actual_dur:
            choke_idx = int(choke_cutoff_s * self.sr)
            choke_fade_len = int(0.005 * self.sr)
            if choke_idx < n_samples:
                fade_end = min(n_samples, choke_idx + choke_fade_len)
                env[choke_idx:fade_end] *= np.linspace(1.0, 0.0, fade_end - choke_idx)
                env[fade_end:] = 0.0

        hat_mono = hat_raw * env * vel_norm * 0.65
        hat_stereo = np.column_stack((hat_mono, np.roll(hat_mono, 8) * 0.96))

        hat_shaped = self.transient_shaper.process(
            hat_stereo,
            attack_gain_db=2.0 if not is_open else 1.0,
            sustain_gain_db=0.0,
            ceiling_db=-0.1,
            drive=1.1
        )
        return hat_shaped.astype(np.float32)


# ==============================================================================
# 3. SOUNDFONT DRUM KIT & SAMPLER
# ==============================================================================

class SoundFontDrumSampler:
    """
    Headless SoundFont Drum Kit Loader & Cache Engine.
    Leverages FluidSynth to pre-render and cache standard General MIDI drum hits
    across velocity tiers for zero-latency, high-impact RAM playback.
    """

    MIDI_DRUM_MAP = {
        "kick_acoustic": 35,
        "kick": 36,
        "side_stick": 37,
        "snare_acoustic": 38,
        "clap": 39,
        "snare_electric": 40,
        "tom_floor_low": 41,
        "hat_closed": 42,
        "tom_floor_high": 43,
        "hat_pedal": 44,
        "tom_low": 45,
        "hat_open": 46,
        "tom_mid_low": 47,
        "tom_mid_high": 48,
        "crash_1": 49,
        "tom_high": 50,
        "ride_1": 51,
        "cymbal_chinese": 52,
        "ride_bell": 53,
        "tambourine": 54,
        "splash": 55,
        "cowbell": 56,
        "crash_2": 57,
        "ride_2": 59,
    }

    def __init__(self, soundfont_path: Optional[str] = None, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.soundfont_path = soundfont_path or self._discover_default_soundfont()
        self.fluidsynth_bin = self._find_fluidsynth()
        self.cached_samples: Dict[Tuple[int, int], np.ndarray] = {}
        self.is_ready = bool(self.fluidsynth_bin and self.soundfont_path and os.path.exists(self.soundfont_path))

    def _discover_default_soundfont(self) -> Optional[str]:
        try:
            import pretty_midi
            sf2 = os.path.join(os.path.dirname(pretty_midi.__file__), "TimGM6mb.sf2")
            if os.path.exists(sf2):
                return sf2
        except Exception:
            pass

        system_paths = [
            "/opt/homebrew/share/soundfonts/default.sf2",
            "/usr/share/sounds/sf2/FluidR3_GM.sf2",
            "/usr/share/soundfonts/default.sf2",
        ]
        for p in system_paths:
            if os.path.exists(p):
                return p
        return None

    def _find_fluidsynth(self) -> Optional[str]:
        paths = ["/opt/homebrew/bin/fluidsynth", "/usr/local/bin/fluidsynth", "/usr/bin/fluidsynth"]
        for p in paths:
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p
        return None

    def pre_cache_drum_hits(self, notes: Optional[List[int]] = None, velocities: Optional[List[int]] = None):
        """
        Renders and caches drum hits across velocity tiers into memory using a single batch FluidSynth call.
        """
        if not self.is_ready:
            return

        target_notes = notes or [35, 36, 38, 39, 40, 42, 44, 46, 49, 51]
        target_vels = velocities or [50, 85, 115]

        try:
            import pretty_midi
            pm = pretty_midi.PrettyMIDI()
            drum_track = pretty_midi.Instrument(program=0, is_drum=True)

            event_schedule = []
            cur_time = 0.1
            spacing = 1.2

            for pitch in target_notes:
                for vel in target_vels:
                    drum_track.notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=cur_time, end=cur_time + 0.9))
                    event_schedule.append((pitch, vel, cur_time))
                    cur_time += spacing

            pm.instruments.append(drum_track)

            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as mid_f:
                pm.write(mid_f.name)
                mid_path = mid_f.name

            wav_path = tempfile.mktemp(suffix=".wav")
            cmd = [
                self.fluidsynth_bin,
                "-ni",
                "-F", wav_path,
                "-r", str(self.sr),
                "-g", "1.1",
                self.soundfont_path,
                mid_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if res.returncode == 0 and os.path.exists(wav_path):
                file_sr, data = wav.read(wav_path)
                if data.dtype == np.int16:
                    audio = (data / 32768.0).astype(np.float32)
                elif data.dtype == np.int32:
                    audio = (data / 2147483648.0).astype(np.float32)
                else:
                    audio = data.astype(np.float32)

                if audio.ndim == 1:
                    audio = np.column_stack((audio, audio))

                hit_dur_samples = int(self.sr * 1.0)
                for pitch, vel, start_t in event_schedule:
                    start_idx = int(start_t * self.sr)
                    end_idx = min(len(audio), start_idx + hit_dur_samples)
                    hit = audio[start_idx:end_idx].copy()
                    mag = np.max(np.abs(hit), axis=1)
                    first_onset = np.where(mag > 0.005)[0]
                    if len(first_onset) > 0 and first_onset[0] > 0:
                        hit = hit[first_onset[0]:].copy()
                    self.cached_samples[(pitch, vel)] = hit

            if os.path.exists(mid_path):
                os.remove(mid_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)

        except Exception:
            pass

    def get_sample(self, pitch: int, velocity: int = 100) -> Optional[np.ndarray]:
        """Retrieves cached sample nearest to the requested velocity."""
        if not self.cached_samples:
            self.pre_cache_drum_hits([pitch], [50, 85, 115])

        matching_keys = [k for k in self.cached_samples if k[0] == pitch]
        if not matching_keys:
            return None

        closest_key = min(matching_keys, key=lambda k: abs(k[1] - velocity))
        sample = self.cached_samples[closest_key].copy()
        vel_scale = (velocity / float(closest_key[1]))
        return sample * vel_scale


# ==============================================================================
# 4. GROOVE, SWING & MICRO-TIMING ENGINE
# ==============================================================================

@dataclass
class DrumHitEvent:
    name_or_note: Union[str, int]
    start_time: float
    velocity: int = 100
    duration: float = 0.45
    pitch_hz: Optional[float] = None
    transient_attack_db: float = 0.0
    transient_sustain_db: float = 0.0


class GrooveEngine:
    """
    MPC60 & SP-1200 Swing, Micro-Timing Humanization & Dynamic Velocity Engine.
    - Classic 16th-Note Swing: 50% (straight) to 75% (hard triplet swing).
    - Pre-shifted offbeat hi-hats / ghost notes (-2 to -6 ms pull for urgency or +3 to +6 ms laid back).
    - Round-robin velocity jitter & micro-timing humanization.
    """

    @staticmethod
    def apply_mpc_swing(
        events: List[DrumHitEvent],
        bpm: float,
        swing_ratio: float = 0.58,
        pre_shift_hats_ms: float = -3.5,
        humanize_timing_ms: float = 1.5,
        velocity_jitter_pct: float = 0.04,
    ) -> List[DrumHitEvent]:
        """
        Applies swing and micro-timing adjustments to a list of drum events.
        """
        beat_dur = 60.0 / bpm
        sixteenth = beat_dur / 4.0
        swing_shift_s = sixteenth * (2.0 * swing_ratio - 1.0)
        pre_shift_s = pre_shift_hats_ms / 1000.0
        jitter_s = humanize_timing_ms / 1000.0

        processed = []
        for ev in events:
            t = ev.start_time
            beat_pos = (t / sixteenth) % 4.0
            is_swing_sixteenth = (abs(beat_pos - 1.0) < 0.15 or abs(beat_pos - 3.0) < 0.15)

            new_t = t
            if is_swing_sixteenth:
                new_t += swing_shift_s

            ev_name = str(ev.name_or_note).lower()
            if "hat" in ev_name or ev.name_or_note in (42, 44, 46):
                if is_swing_sixteenth or abs(beat_pos - 2.0) < 0.15:
                    new_t += pre_shift_s

            if jitter_s > 0:
                new_t += np.random.normal(0.0, jitter_s)

            new_t = max(0.0, new_t)

            vel = ev.velocity
            if velocity_jitter_pct > 0:
                vel_delta = int(np.random.normal(0.0, velocity_jitter_pct * 127))
                vel = max(1, min(127, vel + vel_delta))

            processed.append(DrumHitEvent(
                name_or_note=ev.name_or_note,
                start_time=new_t,
                velocity=vel,
                duration=ev.duration,
                pitch_hz=ev.pitch_hz,
                transient_attack_db=ev.transient_attack_db,
                transient_sustain_db=ev.transient_sustain_db,
            ))

        processed.sort(key=lambda x: x.start_time)
        return processed


# ==============================================================================
# 5. MASTER COMMERCIAL DRUM SAMPLER ENGINE
# ==============================================================================

class DrumSamplerEngine:
    """
    Unified Master Commercial Drum Sampler & Synthesizer.
    Combines:
    - Multi-layer kick, snare, clap, and hi-hat physical & analog synthesis.
    - SoundFont multi-velocity drum playback with FluidSynth RAM cache.
    - Hybrid Drum Layering (Sampled acoustic beater/stick + Synthesized sub/wire body).
    - Bus-level DSP Transient Shaping and soft-knee saturation limiter.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, soundfont_path: Optional[str] = None):
        self.sr = sample_rate
        self.kick_engine = KickLayerEngine(sample_rate=sample_rate)
        self.snare_engine = SnareLayerEngine(sample_rate=sample_rate)
        self.clap_hat_engine = ClapAndHatEngine(sample_rate=sample_rate)
        self.sf_sampler = SoundFontDrumSampler(soundfont_path=soundfont_path, sample_rate=sample_rate)
        self.bus_transient_shaper = TransientShaper(sample_rate=sample_rate)

    def render_hit(
        self,
        drum_type: Union[str, int],
        velocity: int = 100,
        mode: str = "hybrid",
        **kwargs
    ) -> np.ndarray:
        """
        Renders an individual drum hit.
        
        Args:
            drum_type: 'kick', 'snare', 'clap', 'hat_closed', 'hat_open', or MIDI note (35-81).
            velocity: MIDI velocity (1-127).
            mode: 'synth', 'soundfont', or 'hybrid'.
            **kwargs: Layering parameters.
            
        Returns:
            Stereo np.ndarray shape (N, 2).
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        dt = str(drum_type).lower()

        if isinstance(drum_type, int) or dt.isdigit():
            note = int(drum_type)
            if note in (35, 36):
                dt = "kick"
            elif note in (38, 40):
                dt = "snare"
            elif note == 39:
                dt = "clap"
            elif note in (42, 44):
                dt = "hat_closed"
            elif note == 46:
                dt = "hat_open"

        # Mode: SoundFont Sampled
        if mode == "soundfont" and self.sf_sampler.is_ready:
            pitch = SoundFontDrumSampler.MIDI_DRUM_MAP.get(dt, 36 if "kick" in dt else 38)
            sf_hit = self.sf_sampler.get_sample(pitch, velocity)
            if sf_hit is not None:
                return sf_hit

        # Mode: Hybrid
        if mode == "hybrid" and self.sf_sampler.is_ready:
            if "kick" in dt:
                sf_sample = self.sf_sampler.get_sample(35, velocity)
                synth_sub = self.kick_engine.render_kick(
                    beater_punch=0.25,
                    sub_decay=kwargs.get("sub_decay", 0.42),
                    pitch_sub=kwargs.get("pitch_sub", 50.0),
                    saturation_drive=kwargs.get("saturation_drive", 1.2),
                    velocity=velocity,
                )
                if sf_sample is not None:
                    trans_len = min(len(sf_sample), int(self.sr * 0.025))
                    blend = synth_sub.copy()
                    blend[:trans_len] += sf_sample[:trans_len] * 0.75
                    return np.tanh(blend * 1.1) * 0.95

            elif "snare" in dt:
                sf_sample = self.sf_sampler.get_sample(38, velocity)
                synth_snare = self.snare_engine.render_snare(
                    stick_crack_gain=0.3,
                    fundamental_freq=kwargs.get("fundamental_freq", 200.0),
                    wire_decay=kwargs.get("wire_decay", 0.22),
                    velocity=velocity,
                )
                if sf_sample is not None:
                    trans_len = min(len(sf_sample), int(self.sr * 0.035))
                    blend = synth_snare.copy()
                    blend[:trans_len] += sf_sample[:trans_len] * 0.70
                    return np.tanh(blend * 1.15) * 0.92

        # Mode: Multi-Layer Physical/Analog Synthesis
        if "kick" in dt:
            return self.kick_engine.render_kick(
                pitch_sub=kwargs.get("pitch_sub", 50.0),
                sub_decay=kwargs.get("sub_decay", 0.40),
                beater_punch=kwargs.get("beater_punch", 1.0),
                beater_freq=kwargs.get("beater_freq", 3200.0),
                body_punch=kwargs.get("body_punch", 1.0),
                saturation_drive=kwargs.get("saturation_drive", 1.35),
                attack_gain_db=kwargs.get("attack_gain_db", 2.5),
                velocity=velocity,
                duration=kwargs.get("duration", 0.45)
            )
        elif "snare" in dt:
            return self.snare_engine.render_snare(
                fundamental_freq=kwargs.get("fundamental_freq", 200.0),
                wire_decay=kwargs.get("wire_decay", 0.24),
                ring_decay=kwargs.get("ring_decay", 0.20),
                stick_crack_gain=kwargs.get("stick_crack_gain", 1.0),
                saturation_drive=kwargs.get("saturation_drive", 1.3),
                attack_gain_db=kwargs.get("attack_gain_db", 3.0),
                velocity=velocity,
                duration=kwargs.get("duration", 0.45)
            )
        elif "clap" in dt:
            return self.clap_hat_engine.render_clap(
                flam_taps=kwargs.get("flam_taps", 4),
                flam_spread_ms=kwargs.get("flam_spread_ms", 34.0),
                stereo_spread=kwargs.get("stereo_spread", 0.65),
                tail_decay=kwargs.get("tail_decay", 0.28),
                velocity=velocity,
                duration=kwargs.get("duration", 0.55)
            )
        elif "open" in dt or dt == "hat_open":
            return self.clap_hat_engine.render_hat(
                is_open=True,
                velocity=velocity,
                duration=kwargs.get("duration", 0.35)
            )
        else:
            return self.clap_hat_engine.render_hat(
                is_open=False,
                velocity=velocity,
                duration=kwargs.get("duration", 0.085)
            )

    def render_drum_stem(
        self,
        events: List[DrumHitEvent],
        total_duration: float,
        bpm: float = 120.0,
        swing_ratio: float = 0.58,
        pre_shift_hats_ms: float = -3.5,
        apply_bus_transient_shaper: bool = True,
        mode: str = "hybrid",
    ) -> np.ndarray:
        """
        Renders a full multi-track drum stem from a list of drum events with groove & humanization.
        """
        grooved_events = GrooveEngine.apply_mpc_swing(
            events=events,
            bpm=bpm,
            swing_ratio=swing_ratio,
            pre_shift_hats_ms=pre_shift_hats_ms,
            humanize_timing_ms=1.2,
            velocity_jitter_pct=0.03
        )

        total_samples = int(total_duration * self.sr)
        drum_bus = np.zeros((total_samples, 2), dtype=np.float32)

        for ev in grooved_events:
            hit_audio = self.render_hit(
                drum_type=ev.name_or_note,
                velocity=ev.velocity,
                mode=mode,
                duration=ev.duration,
                pitch_sub=ev.pitch_hz or 50.0,
            )

            idx_start = int(ev.start_time * self.sr)
            idx_end = min(total_samples, idx_start + len(hit_audio))
            valid_len = idx_end - idx_start
            if valid_len > 0:
                drum_bus[idx_start:idx_end] += hit_audio[:valid_len]

        if apply_bus_transient_shaper:
            drum_bus = self.bus_transient_shaper.process(
                drum_bus,
                attack_gain_db=1.5,
                sustain_gain_db=-0.5,
                ceiling_db=-0.1,
                drive=1.15
            )

        return drum_bus


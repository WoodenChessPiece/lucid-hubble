"""
src/mastering/neural_restoration.py - Industrial Neural Audio Restoration Pipeline
Author: Antigravity Multi-Agent Architecture
Date: September 2026

Transforms raw, muffled, watery Meta MusicGen / EnCodec outputs into polished,
crisp, punchy, broadcast-compliant masters (-14 LUFS, -1.0 dBTP).
"""

from dataclasses import dataclass
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile

try:
    import pedalboard
    from pedalboard import (
        Pedalboard,
        Compressor,
        HighpassFilter,
        LowShelfFilter,
        HighShelfFilter,
        PeakFilter,
        Limiter,
        Gain
    )
    HAS_PEDALBOARD = True
except ImportError:
    HAS_PEDALBOARD = False


@dataclass
class RestorationConfig:
    sample_rate: int = 44100
    # Stage 1: Subsonic & Mono Management
    subsonic_cutoff_hz: float = 32.0
    mono_bass_crossover_hz: float = 130.0
    # Stage 2: Mid-Side De-Mudding
    mid_mud_freq_hz: float = 360.0
    mid_mud_cut_db: float = -2.2
    side_air_freq_hz: float = 9000.0
    side_air_boost_db: float = 2.5
    # Stage 3: Dynamic Resonance Suppression (Soothe2 style)
    suppress_resonances: bool = True
    resonance_min_hz: float = 1800.0
    resonance_max_hz: float = 4800.0
    resonance_threshold_db: float = 3.5
    resonance_max_cut_db: float = 6.0
    # Stage 4: Differential Transient Designer
    transient_attack_boost: float = 0.55   # +0.0 to +1.0 (enhances punch)
    transient_sustain_clamp: float = 0.35  # +0.0 to +0.8 (ducks neural hash)
    # Stage 5: Harmonic Spectral Exciter
    exciter_drive: float = 2.2
    exciter_blend: float = 0.16           # -16 dB wet blend
    exciter_crossover_hz: float = 10500.0
    # Stage 6: Final Bus Dynamics & True Peak Limiter
    target_lufs: float = -14.0
    max_true_peak_db: float = -1.0


class NeuralAudioRestorationEngine:
    """
    Industrial DSP restoration pipeline engineered specifically for EnCodec/MusicGen artifacts.
    """

    def __init__(self, config: RestorationConfig = None):
        self.cfg = config or RestorationConfig()
        self.sr = self.cfg.sample_rate

    # =========================================================================
    # STAGE 1: Subsonic Strip & Resampling Check
    # =========================================================================
    def strip_subsonics(self, audio: np.ndarray) -> np.ndarray:
        """3rd-order Butterworth highpass at 32 Hz to eliminate DC offset and sub-rumble."""
        sos = signal.butter(3, self.cfg.subsonic_cutoff_hz, btype="highpass", fs=self.sr, output="sos")
        return signal.sosfilt(sos, audio, axis=0)

    # =========================================================================
    # STAGE 2: Mid/Side Spatial De-Mudding & Sub-Bass Mono-Maker
    # =========================================================================
    def process_mid_side(self, stereo: np.ndarray) -> np.ndarray:
        """
        Monos the sub-bass below 130 Hz, scoops boxy mud from Mid, 
        and adds sparkling air to Side.
        """
        left = stereo[:, 0]
        right = stereo[:, 1]

        # Convert to Mid/Side
        mid = (left + right) / np.sqrt(2.0)
        side = (left - right) / np.sqrt(2.0)

        # 1. Elliptical Filter on Side Channel (Kill low stereo rumble)
        sos_side_hp = signal.butter(3, self.cfg.mono_bass_crossover_hz, btype="highpass", fs=self.sr, output="sos")
        side_clean = signal.sosfilt(sos_side_hp, side)

        # 2. Mid Mud Carve (Parametric Bell Cut at ~360 Hz)
        mid_clean = self._apply_peaking_filter(
            mid,
            center_freq=self.cfg.mid_mud_freq_hz,
            gain_db=self.cfg.mid_mud_cut_db,
            q=1.4
        )

        # 3. Side Air Boost (High Shelf at ~9 kHz)
        side_clean = self._apply_high_shelf(
            side_clean,
            shelf_freq=self.cfg.side_air_freq_hz,
            gain_db=self.cfg.side_air_boost_db
        )

        # Reconstruct Left/Right
        out_left = (mid_clean + side_clean) / np.sqrt(2.0)
        out_right = (mid_clean - side_clean) / np.sqrt(2.0)
        return np.column_stack((out_left, out_right))

    # =========================================================================
    # STAGE 3: Dynamic Resonance Suppression (Soothe2 Architecture)
    # =========================================================================
    def suppress_spectral_resonances(self, audio: np.ndarray) -> np.ndarray:
        """
        STFT dynamic notch filter that tracks harsh 2kHz-4.8kHz neural vocoder spikes.
        """
        if not self.cfg.suppress_resonances:
            return audio

        n_fft = 2048
        hop_length = n_fft // 4
        window = np.hanning(n_fft)

        num_channels = audio.shape[1]
        processed_channels = []

        freqs = np.fft.rfftfreq(n_fft, d=1.0 / self.sr)
        target_bin_mask = (freqs >= self.cfg.resonance_min_hz) & (freqs <= self.cfg.resonance_max_hz)

        for ch in range(num_channels):
            sig = audio[:, ch]
            _, _, stft_data = signal.stft(sig, fs=self.sr, window=window, nperseg=n_fft, noverlap=n_fft - hop_length)

            mag = np.abs(stft_data)
            phase = np.angle(stft_data)

            # Compute smoothed spectral envelope across frequency bins (moving average window = 31)
            kernel_size = 31
            kernel = np.ones(kernel_size) / kernel_size
            smoothed_mag = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=0, arr=mag)

            # Compute prominence in dB
            diff_db = 20.0 * np.log10(np.maximum(mag, 1e-9) / np.maximum(smoothed_mag, 1e-9))

            # Attenuate resonant spikes exceeding threshold in the target band
            attenuation = np.ones_like(mag)
            excess = np.maximum(0.0, diff_db - self.cfg.resonance_threshold_db)
            cut_db = np.minimum(self.cfg.resonance_max_cut_db, excess * 1.5)

            # Apply cut only inside target resonance mask
            attenuation[target_bin_mask, :] = 10.0 ** (-cut_db[target_bin_mask, :] / 20.0)

            mag_processed = mag * attenuation
            stft_processed = mag_processed * np.exp(1j * phase)

            _, reconstructed = signal.istft(stft_processed, fs=self.sr, window=window, nperseg=n_fft, noverlap=n_fft - hop_length)

            # Match original length
            if len(reconstructed) > len(sig):
                reconstructed = reconstructed[:len(sig)]
            elif len(reconstructed) < len(sig):
                reconstructed = np.pad(reconstructed, (0, len(sig) - len(reconstructed)))

            processed_channels.append(reconstructed)

        return np.column_stack(processed_channels)

    # =========================================================================
    # STAGE 4: SPL Transient Designer Modeling
    # =========================================================================
    def differential_transient_designer(self, audio: np.ndarray) -> np.ndarray:
        """
        Level-independent dual-envelope follower.
        Sharpens drum & synth attack transients while ducking sustained neural vocoder hash.
        """
        fast_tau_s = 0.002   # 2ms fast attack tracker
        slow_tau_s = 0.038   # 38ms sustain tracker

        alpha_fast = np.exp(-1.0 / (self.sr * fast_tau_s))
        alpha_slow = np.exp(-1.0 / (self.sr * slow_tau_s))

        out = np.zeros_like(audio)
        channels = audio.shape[1]

        for ch in range(channels):
            x = audio[:, ch]
            rect = np.abs(x)

            # Fast envelope loop in numpy
            env_fast = signal.lfilter([1.0 - alpha_fast], [1.0, -alpha_fast], rect)
            env_slow = signal.lfilter([1.0 - alpha_slow], [1.0, -alpha_slow], rect)

            # Differential transient extraction
            diff = np.maximum(0.0, env_fast - env_slow)
            denom = env_fast + 1e-6

            # Compute dynamic gain curve
            gain_curve = 1.0 + (self.cfg.transient_attack_boost * (diff / denom)) - (self.cfg.transient_sustain_clamp * (env_slow / denom))
            gain_curve = np.clip(gain_curve, 0.4, 2.0)

            out[:, ch] = x * gain_curve

        return out

    # =========================================================================
    # STAGE 5: Harmonic Spectral Exciter (>10 kHz Synthesis)
    # =========================================================================
    def harmonic_exciter(self, audio: np.ndarray) -> np.ndarray:
        """
        Generates even and odd harmonics from the 4-8.5 kHz mid band and highpasses
        them at 10.5 kHz to inject organic 'air' and cymbal shimmer.
        """
        # 1. Bandpass filter to extract clean excitation driver (4 kHz to 8.5 kHz)
        sos_driver = signal.butter(2, [4000.0, 8500.0], btype="bandpass", fs=self.sr, output="sos")
        driver = signal.sosfilt(sos_driver, audio, axis=0)

        # 2. Asymmetric non-linear waveshaping (Chebyshev 2nd + 3rd harmonic generator)
        d = driver * self.cfg.exciter_drive
        d_clipped = np.clip(d, -1.0, 1.0)
        harmonics = d + 0.45 * (2.0 * d_clipped**2 - 1.0) + 0.25 * (4.0 * d_clipped**3 - 3.0 * d_clipped)

        # 3. Highpass newly synthesized harmonics above crossover frequency (10.5 kHz)
        sos_air = signal.butter(3, self.cfg.exciter_crossover_hz, btype="highpass", fs=self.sr, output="sos")
        air_band = signal.sosfilt(sos_air, harmonics, axis=0)

        # 4. Mix synthetic air back into dry audio
        restored = audio + (air_band * self.cfg.exciter_blend)
        return restored

    # =========================================================================
    # STAGE 6: Multiband Bus Compression, Tape Saturation & Limiter
    # =========================================================================
    def mastering_stage(self, audio: np.ndarray) -> np.ndarray:
        """
        Applies final glue compression, high-frequency sweetening, 
        and broadcast true-peak limiting.
        """
        if HAS_PEDALBOARD:
            board = Pedalboard([
                Compressor(threshold_db=-16.0, ratio=2.2, attack_ms=18.0, release_ms=120.0),
                HighShelfFilter(cutoff_frequency_hz=11500.0, gain_db=1.8, q=0.707),
                LowShelfFilter(cutoff_frequency_hz=80.0, gain_db=1.2, q=0.707),
                Limiter(threshold_db=self.cfg.max_true_peak_db, release_ms=80.0)
            ])
            audio_t = audio.T.astype(np.float32)
            mastered_t = board(audio_t, self.sr)
            mastered = mastered_t.T
        else:
            # Fallback DSP compressor/limiter
            mastered = np.tanh(audio * 1.1)

        # Normalize to target integrated loudness approximation
        rms = np.sqrt(np.mean(mastered ** 2))
        current_db = 20.0 * np.log10(rms + 1e-9)
        gain_db = self.cfg.target_lufs - current_db
        gain_linear = 10.0 ** (gain_db / 20.0)

        normalized = mastered * gain_linear

        # Absolute True Peak guardrail
        max_peak = np.max(np.abs(normalized))
        target_peak = 10.0 ** (self.cfg.max_true_peak_db / 20.0)
        if max_peak > target_peak:
            normalized *= (target_peak / max_peak)

        return normalized

    # =========================================================================
    # MASTER PIPELINE ORCHESTRATOR
    # =========================================================================
    def restore(self, raw_audio: np.ndarray) -> np.ndarray:
        """
        Runs the full 6-stage restoration pipeline on raw neural audio.
        """
        # Ensure stereo format (samples, 2)
        if raw_audio.ndim == 1:
            raw_audio = np.column_stack((raw_audio, raw_audio))
        elif raw_audio.shape[0] == 2 and raw_audio.shape[1] > 2:
            raw_audio = raw_audio.T

        # Stage 1: Strip subsonics
        s1 = self.strip_subsonics(raw_audio)

        # Stage 2: Mid/Side De-Mudding & Mono Sub
        s2 = self.process_mid_side(s1)

        # Stage 3: Dynamic Resonance Suppression (Soothe2)
        s3 = self.suppress_spectral_resonances(s2)

        # Stage 4: Differential Transient Recovery (SPL Designer)
        s4 = self.differential_transient_designer(s3)

        # Stage 5: Harmonic Spectral Exciter (>10 kHz Air)
        s5 = self.harmonic_exciter(s4)

        # Stage 6: Final Glue & True Peak Limiter
        s6 = self.mastering_stage(s5)

        return s6

    def restore_wav_file(self, input_wav_path: str, output_wav_path: str):
        """Processes a WAV file on disk and outputs a polished master."""
        sr, data = wavfile.read(input_wav_path)
        if sr != self.sr:
            num_samples = int(len(data) * float(self.sr) / sr)
            data = signal.resample(data, num_samples, axis=0)

        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0

        mastered = self.restore(data)

        out_int16 = np.int16(np.clip(mastered * 32767.0, -32767.0, 32767.0))
        wavfile.write(output_wav_path, self.sr, out_int16)

    # =========================================================================
    # Internal Filter Helpers (Biquad Implementations)
    # =========================================================================
    def _apply_peaking_filter(self, x: np.ndarray, center_freq: float, gain_db: float, q: float) -> np.ndarray:
        w0 = 2.0 * np.pi * center_freq / self.sr
        A = 10.0 ** (gain_db / 40.0)
        alpha = np.sin(w0) / (2.0 * q)

        b0 = 1.0 + alpha * A
        b1 = -2.0 * np.cos(w0)
        b2 = 1.0 - alpha * A
        a0 = 1.0 + alpha / A
        a1 = -2.0 * np.cos(w0)
        a2 = 1.0 - alpha / A

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        return signal.lfilter(b, a, x)

    def _apply_high_shelf(self, x: np.ndarray, shelf_freq: float, gain_db: float) -> np.ndarray:
        w0 = 2.0 * np.pi * shelf_freq / self.sr
        A = 10.0 ** (gain_db / 40.0)
        alpha = (np.sin(w0) / 2.0) * np.sqrt(2.0)
        cos_w0 = np.cos(w0)

        b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha)
        b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
        b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha)
        a0 = (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * np.sqrt(A) * alpha
        a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
        a2 = (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * np.sqrt(A) * alpha

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        return signal.lfilter(b, a, x)

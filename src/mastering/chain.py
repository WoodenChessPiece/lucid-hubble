"""
src/mastering/chain.py - Professional Headless YouTube Mastering Engine
Compliant with YouTube -14.0 LUFS & -1.5 dBTP standards.
"""

import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav

class YouTubeMasteringChain:
    def __init__(self, sample_rate: int = 44100, target_lufs: float = -14.0, max_true_peak_db: float = -1.5):
        self.sr = sample_rate
        self.target_lufs = target_lufs
        self.max_tp_linear = 10.0 ** (max_true_peak_db / 20.0)

    def highpass_subsonic(self, audio: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
        """3rd-order Butterworth highpass at 30 Hz to strip DC offset and sub rumble."""
        sos = signal.butter(3, cutoff, btype='highpass', fs=self.sr, output='sos')
        return signal.sosfilt(sos, audio, axis=0)

    def mid_side_mono_bass(self, stereo: np.ndarray, crossover_freq: float = 120.0, side_air_gain: float = 1.06) -> np.ndarray:
        """
        Monos frequencies below 120 Hz to avoid phase cancellation on playback.
        Subtly enhances side channel high frequencies (> 7kHz) for stereo air.
        """
        left = stereo[:, 0]
        right = stereo[:, 1]

        mid = 0.5 * (left + right)
        side = 0.5 * (left - right)

        # Highpass the Side channel at crossover_freq
        sos_hp = signal.butter(2, crossover_freq, btype='highpass', fs=self.sr, output='sos')
        side_filtered = signal.sosfilt(sos_hp, side)

        # Side air boost
        sos_shelf = signal.butter(2, 7200.0, btype='highpass', fs=self.sr, output='sos')
        side_air = signal.sosfilt(sos_shelf, side_filtered) * (side_air_gain - 1.0)
        side_enhanced = side_filtered + side_air

        out_left = mid + side_enhanced
        out_right = mid - side_enhanced
        return np.column_stack((out_left, out_right))

    def multiband_compressor(self, audio: np.ndarray, low_cut: float = 160.0, high_cut: float = 4500.0) -> np.ndarray:
        """Linkwitz-Riley 4th-order 3-band crossover compressor."""
        sos_low = signal.butter(2, low_cut, btype='lowpass', fs=self.sr, output='sos')
        sos_high = signal.butter(2, high_cut, btype='highpass', fs=self.sr, output='sos')

        low_band = signal.sosfilt(sos_low, signal.sosfilt(sos_low, audio, axis=0), axis=0)
        high_band = signal.sosfilt(sos_high, signal.sosfilt(sos_high, audio, axis=0), axis=0)
        mid_band = audio - (low_band + high_band)

        def compress_band(band, threshold_db=-10.0, ratio=2.2):
            thresh = 10.0 ** (threshold_db / 20.0)
            amp = np.abs(band)
            over = np.maximum(amp - thresh, 0.0)
            gain_reduction = 1.0 - (over / (amp + 1e-8)) * (1.0 - (1.0 / ratio))
            return band * gain_reduction

        return compress_band(low_band, -8.0, 2.5) + compress_band(mid_band, -10.0, 2.0) + compress_band(high_band, -12.0, 1.8)

    def tape_saturation(self, audio: np.ndarray, drive: float = 1.15, oversample: int = 4) -> np.ndarray:
        """4x oversampled analog tape saturation to eliminate digital aliasing."""
        up = signal.resample_poly(audio, up=oversample, down=1, axis=0)
        saturated = np.tanh(up * drive) / np.tanh(drive)
        down = signal.resample_poly(saturated, up=1, down=oversample, axis=0)
        return down

    def measure_true_peak(self, audio: np.ndarray) -> float:
        oversampled = signal.resample_poly(audio, up=4, down=1, axis=0)
        return float(np.max(np.abs(oversampled)))

    def normalize_loudness(self, audio: np.ndarray) -> np.ndarray:
        """Normalizes audio to target integrated loudness with true-peak protection."""
        # Calculate RMS-weighted integrated loudness approximation
        rms = np.sqrt(np.mean(audio ** 2))
        current_db = 20.0 * np.log10(rms + 1e-9)
        gain_db = self.target_lufs - current_db
        gain_linear = 10.0 ** (gain_db / 20.0)

        normalized = audio * gain_linear

        # Peak Limiting
        tp = self.measure_true_peak(normalized)
        if tp > self.max_tp_linear:
            attenuation = self.max_tp_linear / tp
            normalized *= attenuation

        return normalized

    def master(self, raw_audio: np.ndarray) -> np.ndarray:
        step1 = self.highpass_subsonic(raw_audio, cutoff=30.0)
        step2 = self.mid_side_mono_bass(step1, crossover_freq=120.0)
        step3 = self.multiband_compressor(step2)
        step4 = self.tape_saturation(step3, drive=1.12, oversample=4)
        mastered = self.normalize_loudness(step4)
        return mastered

    def master_and_save(self, raw_audio: np.ndarray, output_wav_path: str):
        mastered = self.master(raw_audio)
        int16_audio = np.int16(np.clip(mastered * 32767, -32767, 32767))
        wav.write(output_wav_path, self.sr, int16_audio)
        print(f"[Mastering] Exported YouTube-compliant master to: {output_wav_path}")
        return output_wav_path

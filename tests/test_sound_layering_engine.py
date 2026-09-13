import unittest
import numpy as np
import scipy.signal as signal
from src.engine.sound_layering import (
    LinkwitzRileyCrossover,
    MidSideProcessor,
    StemPhaseAligner,
    DynamicLayerDucker,
    LayerGainStager
)

class TestSoundLayeringEngine(unittest.TestCase):
    def test_lr4_crossover(self):
        crossover = LinkwitzRileyCrossover(sample_rate=44100)
        impulse = np.zeros(4096)
        impulse[0] = 1.0

        # 2-way split
        bands = crossover.split_2way(impulse, cutoff_hz=800.0)
        summed_2way = bands.low + bands.high
        mag_2way = np.abs(np.fft.rfft(summed_2way))
        self.assertTrue(np.allclose(mag_2way, 1.0, atol=1e-10))

        # 3-way split
        bands_3way = crossover.split_3way(impulse, low_cutoff_hz=150.0, high_cutoff_hz=3500.0)
        summed_3way = bands_3way.low + bands_3way.mid + bands_3way.high
        mag_3way = np.abs(np.fft.rfft(summed_3way))
        self.assertTrue(np.allclose(mag_3way, 1.0, atol=1e-8))

    def test_midside_processing(self):
        fs = 44100
        dur = 0.5
        t = np.linspace(0, dur, int(fs * dur), endpoint=False)
        L = np.sin(2 * np.pi * 440 * t)
        R = np.cos(2 * np.pi * 440 * t)
        stereo = np.stack([L, R], axis=0)

        # Invertible
        M, S = MidSideProcessor.encode(stereo)
        reconstructed = MidSideProcessor.decode(M, S)
        self.assertTrue(np.allclose(stereo, reconstructed, atol=1e-12))

        # Elliptical mono maker test
        # Create stereo signal with out-of-phase 40 Hz sub
        sub_stereo = np.stack([np.sin(2 * np.pi * 40 * t), -np.sin(2 * np.pi * 40 * t)], axis=0)
        mono_made = MidSideProcessor.elliptical_mono_maker(sub_stereo, cutoff_hz=120.0, fs=fs)
        _, S_mono = MidSideProcessor.encode(mono_made)
        # Check steady state (skip initial 50ms transient)
        steady_state_side = S_mono[int(0.05 * fs):]
        self.assertLess(np.mean(steady_state_side**2), 1e-4)

    def test_phase_alignment(self):
        fs = 44100
        t = np.linspace(0, 0.05, int(fs * 0.05), endpoint=False)
        ref = np.sin(2 * np.pi * 100 * t) * np.exp(-t * 50)
        delay_samples = 22
        target = -1.0 * np.roll(ref, delay_samples) # Polarity inverted and delayed

        aligned = StemPhaseAligner.align_stems(ref, target, auto_invert_polarity=True)
        lag, pol, corr = StemPhaseAligner.calculate_correlation(ref, aligned)
        self.assertEqual(lag, 0)
        self.assertEqual(pol, 1.0)
        self.assertGreater(corr, 0.99)

    def test_dynamic_ducker(self):
        fs = 44100
        total_samples = int(fs * 0.2) # 200 ms
        carrier = np.ones(total_samples)
        trigger = np.zeros(total_samples)
        trigger[50] = 1.0 # Sharp impulse spike

        ducked = DynamicLayerDucker.sidechain_duck(carrier, trigger, duck_depth_db=6.0, release_ms=15.0, fs=fs)
        self.assertLess(ducked[50], 0.55)
        self.assertEqual(ducked[0], 1.0)
        # After >100ms (many time constants), gain must be back to >0.98
        self.assertGreater(ducked[-1], 0.98)

    def test_gain_stager(self):
        audio = np.array([-1.5, 0.2, 0.8, -0.9, 1.4])
        limited = LayerGainStager.safety_limiter(audio, ceiling=0.95)
        self.assertLessEqual(np.max(np.abs(limited)), 0.95)
        
        saturated = LayerGainStager.soft_saturate(audio, drive_db=3.0)
        self.assertLess(np.max(np.abs(saturated)), 1.0)

if __name__ == '__main__':
    unittest.main()

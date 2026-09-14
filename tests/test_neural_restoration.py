"""
tests/test_neural_restoration.py - Unit tests for Neural Audio Restoration Engine
"""

import unittest
import numpy as np
from src.mastering.neural_restoration import NeuralAudioRestorationEngine, RestorationConfig


class TestNeuralRestoration(unittest.TestCase):

    def setUp(self):
        self.sr = 44100
        self.config = RestorationConfig(sample_rate=self.sr)
        self.engine = NeuralAudioRestorationEngine(self.config)

    def test_strip_subsonics(self):
        t = np.linspace(0, 1.0, self.sr, endpoint=False)
        # DC offset + 10 Hz sub rumble + 440 Hz tone
        dc_and_rumble = 0.5 + 0.3 * np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 440 * t)
        stereo = np.column_stack((dc_and_rumble, dc_and_rumble)).astype(np.float32)
        cleaned = self.engine.strip_subsonics(stereo)
        # DC offset should be virtually zero
        self.assertLess(np.abs(np.mean(cleaned)), 0.05)

    def test_process_mid_side(self):
        t = np.linspace(0, 1.0, self.sr, endpoint=False)
        # 50 Hz sub in left, -50 Hz sub in right (100% out of phase stereo bass)
        left = 0.5 * np.sin(2 * np.pi * 50 * t)
        right = -0.5 * np.sin(2 * np.pi * 50 * t)
        stereo = np.column_stack((left, right)).astype(np.float32)
        processed = self.engine.process_mid_side(stereo)
        # Side channel below 130 Hz should be heavily attenuated
        side = (processed[:, 0] - processed[:, 1]) / np.sqrt(2.0)
        self.assertLess(np.max(np.abs(side)), 0.15)

    def test_transient_designer(self):
        samples = self.sr
        # Create a single transient impulse followed by silence
        audio = np.zeros((samples, 2), dtype=np.float32)
        audio[100:150, :] = 0.8
        processed = self.engine.differential_transient_designer(audio)
        self.assertEqual(processed.shape, audio.shape)
        # Transient should be boosted or maintained
        self.assertGreater(np.max(np.abs(processed)), 0.5)

    def test_harmonic_exciter(self):
        t = np.linspace(0, 1.0, self.sr, endpoint=False)
        # 5 kHz tone
        mid_tone = 0.5 * np.sin(2 * np.pi * 5000 * t)
        stereo = np.column_stack((mid_tone, mid_tone)).astype(np.float32)
        excited = self.engine.harmonic_exciter(stereo)
        self.assertEqual(excited.shape, stereo.shape)
        # Should generate non-zero audio
        self.assertGreater(np.max(np.abs(excited)), 0.2)

    def test_end_to_end_restore(self):
        dummy = np.random.randn(self.sr * 2, 2).astype(np.float32) * 0.25
        restored = self.engine.restore(dummy)
        self.assertEqual(restored.shape, dummy.shape)
        self.assertLessEqual(np.max(np.abs(restored)), 1.0)


if __name__ == "__main__":
    unittest.main()

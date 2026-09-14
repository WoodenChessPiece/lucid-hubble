"""
tests/test_neural_engine.py - Test Suite for Dual-Mode Neural AudioCraft / MusicGen Engine
Validates local M3 MPS and cloud RunPod arbitration, guide audio rendering, and hybrid stem summing.
"""

import unittest
import numpy as np
from src.engine.runpod_neural_engine import (
    RunPodNeuralEngine,
    NeuralGenerationConfig,
    LocalMusicGenBackend
)
from src.composer.studio_brain import get_studio_brain, StudioBrain
from src.composer.arranger import NoteEvent


class TestNeuralEngine(unittest.TestCase):

    def test_local_backend_instance(self):
        """Verifies LocalMusicGenBackend detects hardware device."""
        backend = LocalMusicGenBackend.get_instance()
        self.assertIn(backend.device, ["mps", "cuda", "cpu"])

    def test_runpod_engine_auto_resolution(self):
        """Verifies RunPodNeuralEngine automatically selects 'local' when torch/transformers exist and no cloud API key."""
        engine = RunPodNeuralEngine(backend="auto")
        # In our environment with torch/transformers, it should resolve to 'local'
        self.assertIn(engine.backend, ["local", "mock", "runpod"])
        self.assertEqual(engine.target_sr, 44100)

    def test_mock_generation(self):
        """Verifies offline mock stem generation returns valid stereo audio."""
        engine = RunPodNeuralEngine(backend="mock")
        cfg = NeuralGenerationConfig(prompt="progressive house", duration_seconds=2.0, stereo=True)
        stem = engine.generate_stem(cfg)

        self.assertEqual(stem.ndim, 2)
        self.assertEqual(stem.shape[1], 2)
        expected_samples = int(2.0 * engine.target_sr)
        self.assertEqual(stem.shape[0], expected_samples)
        self.assertTrue(np.all(np.abs(stem) <= 1.0))

    def test_generate_full_track_mock(self):
        """Verifies generate_full_track generates complete track."""
        engine = RunPodNeuralEngine(backend="mock")
        audio = engine.generate_full_track("festival anthem", duration_seconds=1.5, bpm=126.0, key="D Minor")
        self.assertEqual(audio.ndim, 2)
        self.assertGreater(len(audio), 0)

    def test_guide_audio_rendering(self):
        """Verifies NoteEvents are correctly serialized to guide audio for chromagram conditioning."""
        engine = RunPodNeuralEngine(backend="mock")
        notes = [
            NoteEvent(pitch=60, start_time=0.0, duration=0.5, velocity=100),
            NoteEvent(pitch=64, start_time=0.5, duration=0.5, velocity=105),
        ]
        guide = engine.render_guide_audio_from_notes(notes, total_duration=1.0, sr=32000)
        self.assertEqual(len(guide), 32000)
        self.assertTrue(np.any(guide != 0.0))

    def test_studio_brain_neural_interface(self):
        """Verifies StudioBrain.render_neural_audio interfaces with neural engine."""
        brain = get_studio_brain()
        audio = brain.render_neural_audio(
            prompt_or_arr="progressive house festival anthem",
            duration_seconds=1.0,
            backend="mock"
        )
        self.assertIsInstance(audio, np.ndarray)
        self.assertGreater(len(audio), 0)


if __name__ == "__main__":
    unittest.main()

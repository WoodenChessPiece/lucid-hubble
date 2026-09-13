"""
tests/test_soundfont_synth.py - Comprehensive Unit & Acoustic Verification Suite
Tests:
1. SoundFontRegistry discovery and prioritization.
2. VelocityScaler response curves, monotonicity, and dynamic range.
3. SoundFontSamplerEngine multi-velocity rendering for all 5 melodic instrument families.
4. Polyphonic chord rendering with micro-strumming.
5. HeadlessVST3SynthHost hosting, parameterization, and audio rendering (Dexed & Surge XT).
6. Multi-track stem generation and headroom safety.
"""

import unittest
import numpy as np
from src.engine.soundfont_synth import (
    SoundFontRegistry,
    VelocityScaler,
    SoundFontSamplerEngine,
    HeadlessVST3SynthHost,
    InstrumentPreset,
    PRESET_CATALOG,
    HAS_FLUIDSYNTH,
    HAS_PEDALBOARD
)
from src.composer.arranger import NoteEvent


class TestVelocityScaler(unittest.TestCase):
    def test_curves_within_valid_midi_bounds(self):
        curves = ["warm_log", "punchy", "ballad", "linear", "exponential"]
        for c in curves:
            for raw_v in range(1, 128):
                scaled = VelocityScaler.scale(raw_v, curve=c)
                self.assertGreaterEqual(scaled, 1)
                self.assertLessEqual(scaled, 127)

    def test_monotonic_scaling(self):
        for raw_v in range(1, 127):
            v1 = VelocityScaler.scale(raw_v, curve="warm_log")
            v2 = VelocityScaler.scale(raw_v + 1, curve="warm_log")
            self.assertLessEqual(v1, v2)


class TestSoundFontRegistry(unittest.TestCase):
    def test_registry_discovery(self):
        registry = SoundFontRegistry()
        available = registry.list_available()
        self.assertGreater(len(available), 0, "Should discover at least one soundfont in storage")
        self.assertIn("general_user", available)
        self.assertIn("fluid_r3", available)


class TestSoundFontSamplerEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SoundFontSamplerEngine(sample_rate=44100)

    @classmethod
    def tearDownClass(cls):
        cls.engine.close()

    def test_all_five_melodic_instruments(self):
        instruments = [
            ("grand_piano", 60),       # C4
            ("rhodes", 64),            # E4
            ("strings", 69),           # A4
            ("warm_french_horn", 55),  # G3
            ("electric_bass", 36),     # C2
        ]
        for preset_name, pitch in instruments:
            audio = self.engine.render_note(
                pitch=pitch,
                velocity=85,
                duration=0.6,
                preset=preset_name
            )
            self.assertEqual(audio.ndim, 2, f"{preset_name} should be stereo (N, 2)")
            self.assertEqual(audio.shape[1], 2)
            self.assertGreater(len(audio), int(0.6 * 44100), f"{preset_name} should include release tail")
            peak = float(np.max(np.abs(audio)))
            rms = float(np.sqrt(np.mean(audio**2)))
            self.assertGreater(peak, 0.01, f"{preset_name} audio should be non-silent")
            self.assertLess(peak, 1.0, f"{preset_name} audio must not clip (> 1.0)")
            self.assertGreater(rms, 0.001, f"{preset_name} RMS energy should be robust")

    def test_chord_rendering_micro_strum(self):
        chord_pitches = [60, 64, 67, 71] # Cmaj7
        audio = self.engine.render_chord(
            chord_pitches,
            duration=1.0,
            velocity=80,
            preset="rhodes",
            strum_delay_ms=12.0
        )
        self.assertEqual(audio.shape[1], 2)
        peak = float(np.max(np.abs(audio)))
        self.assertGreater(peak, 0.02)
        self.assertLess(peak, 0.98)

    def test_render_note_events_timeline(self):
        events = [
            NoteEvent(pitch=48, start_time=0.0, duration=0.4, velocity=90),
            NoteEvent(pitch=52, start_time=0.2, duration=0.4, velocity=85),
            NoteEvent(pitch=55, start_time=0.4, duration=0.5, velocity=80),
        ]
        audio = self.engine.render_note_events(events, preset="grand_piano")
        self.assertGreater(len(audio), int(0.9 * 44100))
        self.assertFalse(np.isnan(audio).any())

    def test_multitrack_rendering(self):
        tracks = {
            "bass": [NoteEvent(pitch=36, start_time=0.0, duration=0.5, velocity=100)],
            "piano": [NoteEvent(pitch=60, start_time=0.0, duration=0.8, velocity=80)],
            "strings": [NoteEvent(pitch=72, start_time=0.2, duration=1.0, velocity=75)]
        }
        stems = self.engine.render_multitrack(tracks)
        self.assertEqual(set(stems.keys()), {"bass", "piano", "strings"})
        for name, stem in stems.items():
            self.assertEqual(stem.shape[1], 2)
            self.assertGreater(np.max(np.abs(stem)), 0.01)


class TestHeadlessVST3SynthHost(unittest.TestCase):
    def test_dexed_hosting(self):
        if not HAS_PEDALBOARD:
            self.skipTest("Pedalboard not available")

        host = HeadlessVST3SynthHost("Dexed")
        self.assertTrue(host.is_instrument)
        params = host.list_parameters()
        self.assertIn("cutoff", params)
        self.assertIn("algorithm", params)

        # Test parameter mutation
        host.set_parameter("cutoff", 0.75)
        self.assertAlmostEqual(host.get_parameter("cutoff"), 0.75, places=2)

        # Test state save/restore
        state = host.get_state()
        self.assertGreater(len(state), 0)
        host.set_state(state)

        # Test audio rendering
        events = [NoteEvent(pitch=60, start_time=0.0, duration=0.5, velocity=90)]
        audio = host.render_notes(events, duration=1.0)
        self.assertEqual(audio.shape[1], 2)
        peak = float(np.max(np.abs(audio)))
        self.assertGreater(peak, 0.01)

    def test_surge_xt_hosting(self):
        if not HAS_PEDALBOARD:
            self.skipTest("Pedalboard not available")

        host = HeadlessVST3SynthHost("Surge XT")
        self.assertTrue(host.is_instrument)
        params = host.list_parameters()
        self.assertGreater(len(params), 100)

        events = [NoteEvent(pitch=55, start_time=0.0, duration=0.4, velocity=85)]
        audio = host.render_notes(events, duration=0.8)
        self.assertEqual(audio.shape[1], 2)
        self.assertGreater(float(np.max(np.abs(audio))), 0.01)


if __name__ == "__main__":
    unittest.main()

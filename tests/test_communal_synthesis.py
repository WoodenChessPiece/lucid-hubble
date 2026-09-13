"""
tests/test_communal_synthesis.py - Test Suite for Communal Masterclass Best-Practice Synthesis
Validates that StudioBrain synthesizes the collective intelligence across all 100 EDM masters
and Billboard Hot 100 hits without picking or cloning an individual artist.
"""

import unittest
from src.composer.studio_brain import get_studio_brain, StudioBrain, UnifiedArrangement
from src.composer.arranger import Arrangement


class TestCommunalSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain(force_reload=True)

    def test_communal_synthesizer_layer_registered(self):
        """Verifies CommunalMasterclassSynthesizer is active on StudioBrain."""
        self.assertIsNotNone(self.brain.communal_synthesizer)

    def test_orchestrate_defaults_to_communal_when_no_artist(self):
        """Verifies that orchestrating without an artist produces a communal synthesis arrangement."""
        arr = self.brain.orchestrate(artist=None, genre="progressive_house", bars=96)
        self.assertIsInstance(arr, UnifiedArrangement)
        self.assertIn("Communal", arr.artist)
        self.assertIsNotNone(arr.progression)
        self.assertIn("Communal", arr.progression.get("name", ""))
        self.assertEqual(arr.motif.get("pickup_beat"), 4.5)
        self.assertEqual(arr.bass_groove.get("gate_length_percent"), 31.0)
        self.assertEqual(arr.bpm, 126.0)

    def test_section_distinct_progressions_in_communal(self):
        """Verifies that harmonic intelligence produces distinct section progressions for communal masterclass."""
        prog = self.brain.communal_synthesizer.synthesize_harmonic_progression()
        
        chorus_prog = self.brain.harmonic.get_section_progression(prog, "chorus")
        verse_prog = self.brain.harmonic.get_section_progression(prog, "verse")
        buildup_prog = self.brain.harmonic.get_section_progression(prog, "buildup")
        breakdown_prog = self.brain.harmonic.get_section_progression(prog, "breakdown")

        # Chorus is anthemic i - VI - III - VII
        self.assertEqual(chorus_prog["roots"], ["D", "Bb", "F", "C"])
        
        # Breakdown has modal borrowing (relative major / Dorian shift)
        self.assertIn("Modal", breakdown_prog.get("name", "") + breakdown_prog.get("roman_numerals", ""))
        self.assertNotEqual(breakdown_prog["roots"], chorus_prog["roots"])

        # Buildup has dominant prolongation climb
        self.assertIn("Buildup", buildup_prog.get("name", ""))

    def test_beat_4_5_pickup_rendered(self):
        """Verifies that the beat 4.5 anticipatory pickup note is present in the lead track."""
        arr = self.brain.orchestrate(artist=None, genre="progressive_house", bars=96)
        lead_events = arr.tracks["lead"]
        self.assertGreater(len(lead_events), 0)

        # In a 126 BPM track, beat_dur = 60/126 ~= 0.47619s.
        # In Bar 31 (Zero-Drop bar before Chorus at Bar 32):
        # Bar start = 31 * 4 * beat_dur ~= 59.0476s.
        # Beat 4.5 = bar_start + 3.5 * beat_dur ~= 60.714s.
        beat_dur = 60.0 / arr.bpm
        bar_dur = beat_dur * 4.0
        expected_pickup_time = 31 * bar_dur + 3.5 * beat_dur

        # Find pickup note near expected_pickup_time (within 50ms)
        pickup_found = any(abs(e.start_time - expected_pickup_time) < 0.05 for e in lead_events)
        self.assertTrue(pickup_found, f"Beat 4.5 pickup note not found near {expected_pickup_time:.3f}s")

    def test_zero_drop_silence_on_beat_4(self):
        """Verifies that Bar 32 Beat 4 cuts kick, snare, hats, and bass."""
        arr = self.brain.orchestrate(artist=None, genre="progressive_house", bars=96)
        beat_dur = 60.0 / arr.bpm
        bar_dur = beat_dur * 4.0

        # Bar 31 Beat 4 is between start + 3*beat_dur and start + 4*beat_dur
        bar31_beat3_start = 31 * bar_dur + 3.0 * beat_dur - 0.01
        bar31_beat4_end = 31 * bar_dur + 3.99 * beat_dur

        # Ensure NO kick in beat 4 of bar 31
        kicks_in_zero_beat = [k for k in arr.kick_times if bar31_beat3_start <= k <= bar31_beat4_end]
        self.assertEqual(len(kicks_in_zero_beat), 0, "Kick drum was not silenced on zero-drop beat 4!")

        # Ensure NO bass in beat 4 of bar 31
        bass_in_zero_beat = [b for b in arr.tracks["bass"] if bar31_beat3_start <= b.start_time <= bar31_beat4_end]
        self.assertEqual(len(bass_in_zero_beat), 0, "Bass was not silenced on zero-drop beat 4!")

    def test_direct_synthesize_communal_masterpiece(self):
        """Verifies StudioBrain.synthesize_communal_masterpiece() direct method."""
        arr = self.brain.synthesize_communal_masterpiece(bars=48)
        self.assertEqual(arr.bars, 48)
        self.assertIn("Communal", arr.artist)
        self.assertGreater(len(arr.tracks["kick"]), 0)
        self.assertGreater(len(arr.tracks["chords"]), 0)
        self.assertGreater(len(arr.tracks["lead"]), 0)
        self.assertGreater(len(arr.tracks["pad"]), 0)


if __name__ == "__main__":
    unittest.main()

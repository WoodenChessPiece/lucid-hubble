"""
tests/test_open_midi_loader.py - Test suite for OpenMidiLibrary.
Verifies chord progression ingestion from free-midi-progressions.zip.
"""

import unittest
import time
from src.composer.open_midi_loader import OpenMidiLibrary, MidiChord, ProgressionList


class TestOpenMidiLibrary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.library = OpenMidiLibrary()

    def test_library_indexing(self):
        self.assertGreater(len(self.library.index), 10000)
        self.assertIn("soul", self.library.get_available_styles())

    def test_d_minor_soul_nostalgic(self):
        prog = self.library.get_progression(
            key="D", mode="Minor", style="soul", mood="Nostalgic", random_choice=False
        )
        self.assertIsInstance(prog, list)
        self.assertGreater(len(prog), 0)
        for chord in prog:
            self.assertIsInstance(chord, MidiChord)
            self.assertIsInstance(chord["notes"], list)
            self.assertIsInstance(chord.notes, list)
            self.assertGreater(chord.duration, 0.0)
            self.assertTrue(chord.root)
            for pitch in chord.notes:
                self.assertGreaterEqual(pitch, 0)
                self.assertLessEqual(pitch, 127)

    def test_c_major_soul_nostalgic(self):
        prog = self.library.get_progression(
            key="C", mode="Major", style="soul", mood="Nostalgic", random_choice=False
        )
        self.assertIsInstance(prog, list)
        self.assertGreater(len(prog), 0)
        for chord in prog:
            self.assertGreater(chord.duration, 0.0)
            for pitch in chord.notes:
                self.assertGreaterEqual(pitch, 0)
                self.assertLessEqual(pitch, 127)

    def test_fsharp_minor_soul_nostalgic(self):
        prog = self.library.get_progression(
            key="F#", mode="Minor", style="soul", mood="Nostalgic", random_choice=False
        )
        self.assertIsInstance(prog, list)
        self.assertGreater(len(prog), 0)
        for chord in prog:
            self.assertGreater(chord.duration, 0.0)
            for pitch in chord.notes:
                self.assertGreaterEqual(pitch, 0)
                self.assertLessEqual(pitch, 127)

    def test_enharmonic_resolution(self):
        # In Minor, C# is standard; Db should resolve to C#
        prog_db = self.library.get_progression(key="Db", mode="Minor", style="soul", mood="Nostalgic", random_choice=False)
        self.assertEqual(prog_db.key, "C#")

        # In Major, Db is standard; C# should resolve to Db
        prog_cs = self.library.get_progression(key="C#", mode="Major", style="soul", mood="Nostalgic", random_choice=False)
        self.assertEqual(prog_cs.key, "Db")

    def test_fallback_robustness(self):
        prog = self.library.get_progression(
            key="A", mode="Minor", style="unknown_alien_genre", mood="NonExistentMood123"
        )
        self.assertGreater(len(prog), 0)
        for chord in prog:
            self.assertGreater(chord.duration, 0.0)
            self.assertTrue(chord.notes)

    def test_caching_speed(self):
        # Warm up
        _ = self.library.get_progression(key="D", mode="Minor", style="soul", mood="Nostalgic", random_choice=False)
        
        t0 = time.time()
        for _ in range(500):
            _ = self.library.get_progression(key="D", mode="Minor", style="soul", mood="Nostalgic", random_choice=False)
        elapsed_ms = (time.time() - t0) * 1000
        # 500 calls should easily be under 500ms (< 1ms per call)
        self.assertLess(elapsed_ms, 500.0)


if __name__ == "__main__":
    unittest.main()

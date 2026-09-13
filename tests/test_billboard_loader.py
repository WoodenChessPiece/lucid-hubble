"""
tests/test_billboard_loader.py - Test Suite for Billboard Hit Knowledge Base & Loader
"""

import unittest
from src.composer.billboard_loader import BillboardHitLoader, get_billboard_loader, HitProgression
from src.composer.open_midi_loader import OpenMidiLoader


class TestBillboardLoader(unittest.TestCase):
    def setUp(self):
        self.loader = get_billboard_loader()
        self.midi_loader = OpenMidiLoader()

    def test_database_loaded(self):
        self.assertGreaterEqual(len(self.loader.progressions), 15)
        self.assertGreaterEqual(len(self.loader.melodic_motifs), 9)
        self.assertGreaterEqual(len(self.loader.bass_grooves), 4)

    def test_query_by_artist(self):
        sabrina_prog = self.loader.get_hit_progression(artist="Sabrina Carpenter")
        self.assertIsNotNone(sabrina_prog)
        self.assertIn("Sabrina Carpenter", sabrina_prog["artist"])
        self.assertTrue(len(sabrina_prog["chords"]) > 0)

        billie_prog = self.loader.get_hit_progression(artist="Billie Eilish")
        self.assertIsNotNone(billie_prog)
        self.assertIn("Billie Eilish", billie_prog["artist"])

        chappell_prog = self.loader.get_hit_progression(artist="Chappell Roan")
        self.assertIsNotNone(chappell_prog)
        self.assertIn("Chappell Roan", chappell_prog["artist"])

    def test_query_by_style(self):
        dreamy_prog = self.loader.get_hit_progression(style="dreamy_pop")
        self.assertIsNotNone(dreamy_prog)
        self.assertTrue(any("dreamy_pop" in st for st in dreamy_prog["style_tags"]))

        synthpop_prog = self.loader.get_hit_progression(style="synthpop")
        self.assertIsNotNone(synthpop_prog)
        self.assertTrue(any("synthpop" in st for st in synthpop_prog["style_tags"]))

    def test_open_midi_loader_integration(self):
        p_artist = self.midi_loader.get_hit_progression(artist="Sabrina Carpenter")
        self.assertIsNotNone(p_artist)
        self.assertIn("Sabrina Carpenter", p_artist["artist"])

        p_style = self.midi_loader.get_hit_progression(style="dreamy_pop")
        self.assertIsNotNone(p_style)
        self.assertTrue(any("dreamy_pop" in st for st in p_style["style_tags"]))

    def test_melodic_motifs(self):
        motif = self.loader.get_hit_motif(title="Espresso")
        self.assertIsNotNone(motif)
        self.assertEqual(motif["artist"], "Sabrina Carpenter")
        self.assertIn("climax_target", motif)
        self.assertEqual(motif["climax_target"]["pitch"], "C5")
        self.assertGreaterEqual(len(motif["midi_sequence"]), 5)

    def test_bass_grooves(self):
        brat_groove = self.loader.get_hit_bass_groove(artist="Charli XCX")
        self.assertIsNotNone(brat_groove)
        self.assertIn("Charli XCX", brat_groove["artist"])
        self.assertEqual(len(brat_groove["steps"]), 16)
        self.assertIn("drum_pocket", brat_groove)


if __name__ == "__main__":
    unittest.main()

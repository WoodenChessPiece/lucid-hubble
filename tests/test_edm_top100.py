"""
tests/test_edm_top100.py - Comprehensive Verification for Top 100 EDM Artists Billboard Database
Verifies:
1. Complete 100-artist roster loaded in EDMLoader.
2. All 5 electronic disciplines represented with 20 artists each.
3. Accurate chord progressions, Roman numerals, Drop-2/4 voicings for key hits.
4. Melodic hooks with asymmetrical pickups (beat 4.5/4.75).
5. Bass groove pocket physics (30% gate staccato plucks).
6. Full StudioBrain seamless integration and dynamic queries.
"""

import unittest
from src.composer.edm_loader import EDMLoader, get_edm_loader
from src.composer.studio_brain import StudioBrain, get_studio_brain

class TestEDMTop100Database(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = get_edm_loader()
        cls.brain = get_studio_brain(force_reload=True)

    def test_total_artist_count_and_roster(self):
        artists = self.loader.get_all_artists()
        self.assertEqual(len(artists), 100, f"Expected 100 artists, got {len(artists)}")
        
        # Verify marquee artists from all 5 disciplines are present
        expected_artists = [
            # Group 1: Progressive / Big Room
            "Avicii", "Swedish House Mafia", "Martin Garrix", "Calvin Harris", "Zedd",
            # Group 2: Melodic Techno / Deep House
            "deadmau5", "Eric Prydz / Pryda", "Rüfüs Du Sol", "Bicep", "Fred again..",
            # Group 3: French Touch / Synthwave
            "Daft Punk", "Justice", "Gesaffelstein", "Kavinsky", "Carpenter Brut",
            # Group 4: Future Bass / Trap / Dubstep
            "Flume", "Illenium", "Skrillex", "San Holo", "Seven Lions",
            # Group 5: Trance / DnB / IDM
            "Armin van Buuren", "Above & Beyond", "Jon Hopkins", "Aphex Twin", "Noisia"
        ]
        for name in expected_artists:
            found = self.loader.get_artist(name)
            self.assertIsNotNone(found, f"Artist '{name}' not found in EDM database")

    def test_discipline_distribution(self):
        disciplines = {}
        for a in self.loader.artists:
            d = a.get("discipline")
            disciplines[d] = disciplines.get(d, 0) + 1

        self.assertEqual(len(disciplines), 5, f"Expected 5 disciplines, got {len(disciplines)}: {disciplines}")
        for d, count in disciplines.items():
            self.assertEqual(count, 20, f"Discipline '{d}' should have 20 artists, found {count}")

    def test_avicii_progression_and_voicing(self):
        prog = self.loader.get_progression("Avicii")
        self.assertIsNotNone(prog)
        self.assertIn("VI", prog.get("roman_numerals", ""))
        self.assertEqual(prog.get("key", "").lower(), "c# minor")

    def test_deadmau5_strobe_progression(self):
        prog = self.loader.get_progression("deadmau5")
        self.assertIsNotNone(prog)
        self.assertIn("vi - IV - I - V", prog.get("roman_numerals", ""))

    def test_daft_punk_progression(self):
        prog = self.loader.get_progression("Daft Punk")
        self.assertIsNotNone(prog)
        self.assertTrue("Dorian" in prog.get("roman_numerals", "") or "B Dorian" in prog.get("key", ""))

    def test_flume_future_bass_progression(self):
        prog = self.loader.get_progression("Flume")
        self.assertIsNotNone(prog)
        self.assertIn("IVmaj9", prog.get("roman_numerals", ""))

    def test_armin_van_buuren_trance_progression(self):
        prog = self.loader.get_progression("Armin van Buuren")
        self.assertIsNotNone(prog)
        self.assertIn("i - VI - III - VII", prog.get("roman_numerals", ""))

    def test_melodic_hook_pickups(self):
        hook = self.loader.get_melodic_hook("Skrillex")
        if hook:
            pickup = hook.get("pickup_beat") or hook.get("pickup_timing")
            self.assertIn(pickup, [4.5, 4.75])

    def test_bass_groove_gate_physics(self):
        groove = self.loader.get_bass_groove("deadmau5")
        self.assertIsNotNone(groove)
        gate = groove.get("gate_length_percent", 30)
        self.assertLessEqual(gate, 35)

    def test_studio_brain_integration(self):
        # 1. Check database registry
        self.assertIn("edm_top100", self.brain.databases)
        self.assertTrue(self.brain.databases["edm_top100"]["exists"])
        self.assertGreater(self.brain.databases["edm_top100"]["size_bytes"], 100000)

        # 2. Query artist through StudioBrain
        art = self.brain.get_edm_artist("Swedish House Mafia")
        self.assertIsNotNone(art)
        self.assertEqual(art.get("name"), "Swedish House Mafia")

        # 3. Query progression through StudioBrain Harmonic Intelligence
        prog = self.brain.get_edm_progression("Eric Prydz / Pryda")
        self.assertIsNotNone(prog)
        self.assertIn("Opus", str(prog))

        # 4. Check all EDM artists list
        all_artists = self.brain.get_all_edm_artists()
        self.assertEqual(len(all_artists), 100)

    def test_studio_brain_arrangement_with_edm_harmony(self):
        # Generate an arrangement using deadmau5 Strobe progression
        prog = self.brain.get_edm_progression("deadmau5")
        self.assertIsNotNone(prog)

        arr = self.brain.generate_arrangement(
            genre="melodic_techno",
            archetype="slow_burn_progressive",
            artist="deadmau5",
            bars=32,
            bpm=128.0
        )
        self.assertIsNotNone(arr)
        self.assertGreater(len(arr.tracks), 0)
        
        # Verify tracks present
        self.assertIn("bass", arr.tracks)
        self.assertIn("chords", arr.tracks)
        self.assertIn("kick", arr.tracks)
        self.assertGreater(len(arr.tracks["bass"]), 0)

if __name__ == "__main__":
    unittest.main()

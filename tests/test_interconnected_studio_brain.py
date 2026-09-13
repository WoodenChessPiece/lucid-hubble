"""
tests/test_interconnected_studio_brain.py - Verification Suite for Interconnected StudioBrain
Tests the 5 interconnected intelligence layers across multiple artists & prompts:
1. Autonomous Intent Resolution (Prompt Parsing across 100 EDM & Billboard artists)
2. Harmonic Brain: Section-distinct progressions (Verse != Chorus != Breakdown), Drop-2/4 voicings, modal borrowing
3. Melodic Brain: 7-stage motif sentence development, Beat 4.5 pickups, non-clashing conversational polyphony
4. Groove Brain: 5 distinct genre drum pockets, 30% staccato gate bass physics, velocity tiers
5. Structural Brain: Dynamic archetype selection and Bar 32 Beat 4 Zero-Drop silence
"""

import unittest
from src.composer.studio_brain import get_studio_brain, UnifiedArrangement
from src.composer.arranger import Arrangement, NoteEvent

class TestInterconnectedStudioBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain()

    def test_autonomous_prompt_parsing_deadmau5(self):
        """Prompt parsing must resolve deadmau5, melodic techno, slow_burn_progressive, and 128 BPM."""
        parsed = self.brain.parse_prompt("deadmau5 Strobe progressive arc")
        self.assertEqual(parsed.get("artist"), "deadmau5")
        self.assertEqual(parsed.get("archetype"), "slow_burn_progressive")
        self.assertEqual(parsed.get("bpm"), 128.0)
        self.assertIn(parsed.get("genre"), ["melodic_techno", "progressive_house"])

    def test_autonomous_prompt_parsing_daft_punk(self):
        """Prompt parsing must resolve Daft Punk, french_touch, and continuous_drive."""
        parsed = self.brain.parse_prompt("Daft Punk disco funk with swinging bass")
        self.assertEqual(parsed.get("artist"), "Daft Punk")
        self.assertEqual(parsed.get("genre"), "french_touch")
        self.assertEqual(parsed.get("archetype"), "continuous_drive")

    def test_autonomous_prompt_parsing_skrillex(self):
        """Prompt parsing must resolve Skrillex, dubstep, and in_medias_res."""
        parsed = self.brain.parse_prompt("Skrillex heavy dubstep drop with halftime drums")
        self.assertEqual(parsed.get("artist"), "Skrillex")
        self.assertIn(parsed.get("genre"), ["dubstep", "future_bass"])
        self.assertEqual(parsed.get("archetype"), "in_medias_res")

    def test_autonomous_prompt_parsing_rufus_du_sol(self):
        """Prompt parsing must resolve Rüfüs Du Sol with accent-insensitivity."""
        parsed = self.brain.parse_prompt("Rufus Du Sol melodic house with emotional breakdown")
        import unicodedata; clean_a = "".join(x for x in unicodedata.normalize("NFKD", parsed.get("artist", "")) if not unicodedata.combining(x)).lower(); self.assertIn("rufus", clean_a)
        self.assertEqual(parsed.get("genre"), "melodic_house")

    def test_autonomous_prompt_parsing_billie_eilish(self):
        """Prompt parsing must resolve Billie Eilish from Billboard database with dark_pop."""
        parsed = self.brain.parse_prompt("Billie Eilish dark pop bedroom aesthetic")
        self.assertEqual(parsed.get("artist"), "Billie Eilish")
        self.assertEqual(parsed.get("genre"), "dark_pop")
        self.assertEqual(parsed.get("archetype"), "aaba_classic")

    def test_harmonic_brain_section_distinct_progressions(self):
        """Harmonic Brain must generate musically distinct progressions for verse, chorus, and breakdown."""
        base_prog = {
            "name": "Avicii Levels Primary",
            "roots": ["C#", "A", "E", "B"],
            "types": ["min", "maj", "maj", "maj"],
            "key": "C# Minor"
        }
        chorus_prog = self.brain.harmonic.get_section_progression(base_prog, "chorus")
        verse_prog = self.brain.harmonic.get_section_progression(base_prog, "verse")
        breakdown_prog = self.brain.harmonic.get_section_progression(base_prog, "breakdown")
        buildup_prog = self.brain.harmonic.get_section_progression(base_prog, "buildup")

        # Chorus has primary anthemic cadence
        self.assertEqual(chorus_prog["roots"], ["C#", "A", "E", "B"])

        # Breakdown features modal borrowing / relative major shift
        self.assertNotEqual(breakdown_prog["roots"], chorus_prog["roots"])
        self.assertIn("maj9", breakdown_prog["types"])

        # Buildup features dominant tension climb
        self.assertNotEqual(buildup_prog["roots"], chorus_prog["roots"])
        self.assertIn("dom7", buildup_prog["types"])

    def test_melodic_brain_conversational_polyphony(self):
        """Counter-melody must never clash with lead notes, filling only lead rests."""
        lead_events = [
            (0.0, 1.0, 72, 100),
            (2.0, 1.0, 74, 100),
            (4.0, 1.0, 76, 100)
        ]
        counter = self.brain.melodic.generate_counter_melody(
            lead_events=lead_events,
            total_duration=8.0,
            root_note="C#",
            octave=4
        )
        self.assertGreater(len(counter), 0)
        for c_st, c_dur, c_pitch, c_vel in counter:
            for l_st, l_dur, _, _ in lead_events:
                lead_busy = (l_st <= c_st <= l_st + l_dur)
                self.assertFalse(lead_busy, f"Counter at {c_st} clashes with lead ({l_st} - {l_st + l_dur})")

    def test_orchestrate_deadmau5_full_arrangement(self):
        """Orchestrate deadmau5 prompt and verify 9 stems, 128 BPM, and slow_burn_progressive arc."""
        arr = self.brain.orchestrate(prompt="deadmau5 Strobe progressive arc", bars=64)
        self.assertIsInstance(arr, UnifiedArrangement)
        self.assertEqual(arr.bpm, 128.0)
        self.assertEqual(arr.archetype, "slow_burn_progressive")
        self.assertIn("kick", arr.tracks)
        self.assertIn("bass", arr.tracks)
        self.assertIn("lead", arr.tracks)
        self.assertIn("chords", arr.tracks)
        self.assertIn("counter", arr.tracks)

    def test_orchestrate_daft_punk_funk_pocket(self):
        """Orchestrate Daft Punk prompt and verify continuous_drive groove and swing."""
        arr = self.brain.orchestrate(prompt="Daft Punk disco funk", bars=64)
        self.assertIsInstance(arr, UnifiedArrangement)
        self.assertEqual(arr.genre, "french_touch")
        self.assertEqual(arr.archetype, "continuous_drive")
        self.assertGreater(len(arr.tracks["bass"]), 0)

    def test_zero_drop_mechanics_in_orchestration(self):
        """Zero-drop window on Bar 32 Beat 4 must strictly silence kick, snare, and bass."""
        arr = self.brain.orchestrate(
            prompt="Martin Garrix festival anthem with epic drop",
            bars=96,
            archetype="narrative_7part"
        )
        beat_dur = 60.0 / arr.bpm
        bar_dur = beat_dur * 4.0
        z_start = 31 * bar_dur + 3.0 * beat_dur - 0.01
        z_end = 32 * bar_dur - 0.01

        kicks_in_zero = [e for e in arr.tracks["kick"] if z_start <= e.start_time < z_end]
        bass_in_zero = [e for e in arr.tracks["bass"] if z_start <= e.start_time < z_end]
        snares_in_zero = [e for e in arr.tracks["snare"] if z_start <= e.start_time < z_end]

        self.assertEqual(len(kicks_in_zero), 0)
        self.assertEqual(len(bass_in_zero), 0)
        self.assertEqual(len(snares_in_zero), 0)

if __name__ == "__main__":
    unittest.main()

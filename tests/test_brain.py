"""
tests/test_brain.py - Comprehensive Unit & Integration Tests for StudioBrain
"""

import unittest
from src.composer.brain import (
    StudioBrain,
    HarmonicIntelligence,
    MelodicIntelligence,
    GrooveIntelligence,
    StructuralIntelligence,
    DynamicKnowledgeGraph,
    apply_drop_2,
    apply_drop_4,
    apply_drop_2_and_4,
    parsimonious_voice_leading
)


class TestStudioBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brain = StudioBrain.get_instance(auto_scan=True)

    def test_singleton_instance(self):
        instance1 = StudioBrain.get_instance()
        instance2 = StudioBrain.get_instance()
        self.assertIs(instance1, instance2)

    def test_harmonic_intelligence_progressions(self):
        h = self.brain.harmonic
        # 1. Open MIDI 11,400 query
        if h.midi_library is not None:
            prog = h.get_open_midi_progression(key="D", mode="Minor", style="soul", mood="Nostalgic")
            self.assertGreater(len(prog), 0)
            self.assertTrue(hasattr(prog[0], "notes"))

        # 2. Billboard Hot 100 query
        billboard_prog = h.get_billboard_progression(artist="Sabrina Carpenter")
        self.assertIsNotNone(billboard_prog)
        self.assertIn("Sabrina Carpenter", billboard_prog.get("artist", ""))

        # 3. Markov chain synthesis
        markov = h.get_markov_progression(length=4, cluster_name="melancholic_yearning", tonic="D", mode="minor")
        self.assertEqual(len(markov), 4)

        # 4. Turnaround query
        turnaround = h.get_leadsheet_turnaround(turnaround_key="lady_bird_dameron", tonic="C")
        self.assertGreater(len(turnaround), 0)

    def test_parsimonious_voice_leading_and_drops(self):
        voicing = [60, 64, 67, 71] # Cmaj7 close voicing: C4, E4, G4, B4
        drop2 = apply_drop_2(voicing)
        # Drop-2 drops G4 (67) down to G3 (55)
        self.assertEqual(drop2, [55, 60, 64, 71])

        drop4 = apply_drop_4(voicing)
        # Drop-4 drops C4 (60) down to C3 (48)
        self.assertEqual(drop4, [48, 64, 67, 71])

        drop24 = apply_drop_2_and_4(voicing)
        # Drop 2 & 4 drops C4 -> C3 (48) and G4 -> G3 (55)
        self.assertEqual(drop24, [48, 55, 64, 71])

        # Parsimonious transition
        chords = [("D", "min7"), ("Bb", "maj7")]
        results = self.brain.harmonic.voice_lead_progression(chords, voicing_type="drop2")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["voicing_type"], "drop2")

    def test_melodic_intelligence(self):
        m = self.brain.melodic
        # Asymmetrical pickup
        pickup = m.generate_asymmetrical_pickup(key_root="D", chord_type="min7", pickup_beat=4.5)
        self.assertGreaterEqual(len(pickup), 1)
        self.assertIn(pickup[0].role, ("pickup_speech", "pickup_push"))

        # Golden-ratio climax calculation
        climax_16 = m.calculate_golden_ratio_climax(total_bars=16)
        self.assertEqual(climax_16["climax_bar_human"], 10)
        self.assertEqual(climax_16["climax_bar_index"], 9)

        climax_8 = m.calculate_golden_ratio_climax(total_bars=8)
        self.assertEqual(climax_8["climax_bar_human"], 5)

        # Thematic arc and conversational counterpoint
        chords = [("D", "min7"), ("Bb", "maj7"), ("F", "maj7"), ("C", "dom7")]
        lead = m.generate_thematic_arc(chords, target_bars=16, seed=42)
        self.assertGreater(len(lead), 10)

        counter = m.generate_conversational_counterpoint(lead, chords, target_bars=16)
        self.assertGreater(len(counter), 10)

    def test_groove_intelligence(self):
        g = self.brain.groove
        # Carpenter Brut staccato pattern
        cb_bass = g.generate_bass_groove(root="D", chord_type="min7", style="carpenter_brut", total_bars=4)
        self.assertEqual(len(cb_bass), 60) # 15 notes per bar * 4 bars
        
        # Check staccato gate physics (30-35% gate)
        staccato_notes = [n for n in cb_bass if n["articulation"] == "staccato"]
        self.assertGreater(len(staccato_notes), 40)
        for sn in staccato_notes:
            self.assertLessEqual(sn["gate_ratio"], 0.40)

        # Check turnaround legato slide on final bar
        turnaround_legato = [n for n in cb_bass if n["bar"] == 3 and n["articulation"] == "legato"]
        self.assertGreaterEqual(len(turnaround_legato), 1)

        # Velocity tiers check
        self.assertEqual(g.classify_velocity_tier(45), "ghost")
        self.assertEqual(g.classify_velocity_tier(70), "offbeat")
        self.assertEqual(g.classify_velocity_tier(88), "pocket")
        self.assertEqual(g.classify_velocity_tier(115), "accent")

    def test_structural_intelligence_archetypes(self):
        s = self.brain.structural
        # Must contain at least 7 archetypes
        self.assertGreaterEqual(len(s.archetypes), 7)
        self.assertIn("narrative_7part", s.archetypes)
        self.assertIn("in_medias_res", s.archetypes)
        self.assertIn("slow_burn_progressive", s.archetypes)
        self.assertIn("aaba_classic", s.archetypes)
        self.assertIn("continuous_drive", s.archetypes)
        self.assertIn("episodic_rondo", s.archetypes)
        self.assertIn("two_act_hybrid", s.archetypes)
        self.assertIn("minimalist_polymetric", s.archetypes)

        # Plan arrangement
        plan = s.plan_arrangement(genre="synthwave", archetype_name="narrative_7part", total_bars=96)
        self.assertEqual(plan["total_bars"], 96)
        self.assertGreaterEqual(len(plan["sections"]), 7)
        for sec in plan["sections"]:
            self.assertIn("stem_mask", sec)
            self.assertIn("energy_target", sec)
            self.assertIn("kick", sec["stem_mask"])
            self.assertIn("bass", sec["stem_mask"])

    def test_dynamic_knowledge_graph_ingestion_and_query(self):
        kg = self.brain.knowledge_graph
        stats = self.brain.get_knowledge_stats()
        self.assertGreater(stats["total_nodes"], 100)
        self.assertGreater(stats["total_edges"], 100)

        # Search query
        results = self.brain.query_knowledge("voice leading", limit=5)
        self.assertGreater(len(results), 0)
        self.assertIsNotNone(results[0]["title"])

    def test_compose_song_blueprint(self):
        bp = self.brain.compose_song_blueprint(
            genre="synthwave",
            archetype="narrative_7part",
            key="D",
            mode="minor",
            bpm=118.0,
            total_bars=96
        )
        self.assertIn("structural_plan", bp)
        self.assertIn("harmonic_layers", bp)
        self.assertIn("melodic_layers", bp)
        self.assertIn("groove_layers", bp)
        self.assertEqual(bp["total_bars"], 96)
        self.assertGreater(len(bp["melodic_layers"]["lead_hook_16bars"]), 0)
        self.assertGreater(len(bp["melodic_layers"]["counter_melody_16bars"]), 0)
        self.assertGreater(len(bp["groove_layers"]["verse_bass_loop_4bars"]), 0)


if __name__ == "__main__":
    unittest.main()

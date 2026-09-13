"""
tests/test_studio_brain.py - Comprehensive Verification Test Suite for StudioBrain
Agent 4: Studio Brain System Verifier

Verifies:
1. StudioBrain initializes and unifies all 5 intelligence layers:
   - Harmonic Layer
   - Melodic Layer
   - Groove Layer
   - Structural Layer
   - Timbral Layer
2. Automatic discovery of all existing databases:
   - music_knowledge_base.json
   - billboard_hits_database.json
   - 11,400 MIDI files library (free-midi-progressions.zip)
3. Generation of unified arrangements containing ALL required disciplines in a single pass:
   - All 9 required instrument tracks (kick, snare, hihat, bass, chords, lead, counter, pad, fx)
   - Masterclass arrangement archetypes and 7-part narrative arc
   - Zero-drop bar 32 beat 4 silence mechanics
   - Timbral profiles and frequency slotting metadata
4. Dynamic hot-reloading and live ingestion of new data (progressions, motifs, grooves, archetypes, timbral profiles).
"""

import os
import unittest
import time
from typing import List, Dict, Any

from src.composer.studio_brain import (
    StudioBrain,
    get_studio_brain,
    UnifiedArrangement,
    HarmonicIntelligence,
    MelodicIntelligence,
    GrooveIntelligence,
    StructuralIntelligence,
    TimbralIntelligence,
    TimbralProfile,
)
from src.composer.arranger import Arrangement, NoteEvent, ARCHETYPES


class TestStudioBrainInitializationAndLayers(unittest.TestCase):
    """Verifies StudioBrain initialization and unification of all 5 intelligence layers."""

    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain()

    def test_brain_initialization(self):
        """StudioBrain must initialize cleanly as a singleton master orchestrator."""
        self.assertIsNotNone(self.brain)
        self.assertTrue(getattr(self.brain, "_initialized", False))
        brain_singleton = get_studio_brain()
        self.assertIs(self.brain, brain_singleton)

    def test_all_five_intelligence_layers_present(self):
        """StudioBrain must unify all 5 intelligence layers."""
        self.assertIsInstance(self.brain.harmonic, HarmonicIntelligence)
        self.assertIsInstance(self.brain.melodic, MelodicIntelligence)
        self.assertIsInstance(self.brain.groove, GrooveIntelligence)
        self.assertIsInstance(self.brain.structural, StructuralIntelligence)
        self.assertIsInstance(self.brain.timbral, TimbralIntelligence)

        # Dictionary registry verification
        self.assertIn("harmonic", self.brain.layers)
        self.assertIn("melodic", self.brain.layers)
        self.assertIn("groove", self.brain.layers)
        self.assertIn("structural", self.brain.layers)
        self.assertIn("timbral", self.brain.layers)
        self.assertEqual(len(self.brain.layers), 5)

    def test_harmonic_intelligence_operations(self):
        """Harmonic layer resolves progressions, Drop-2 voicings, voice leading, and reharmonizations."""
        prog = self.brain.harmonic.get_progression(genre="synthwave", section="chorus")
        self.assertIn("roots", prog)
        self.assertIn("types", prog)
        self.assertGreater(len(prog["roots"]), 0)

        # Voice leading and Drop-2
        voiced = self.brain.harmonic.voice_chords(prog["roots"][:4], prog["types"][:4], octave=4, drop_2=True)
        self.assertEqual(len(voiced), 4)
        for chord in voiced:
            self.assertGreaterEqual(len(chord), 3)

        # Reharmonization
        reharm_roots, reharm_types = self.brain.harmonic.reharmonize(["D", "Bb", "F", "C"], ["min", "maj", "maj", "dom7"])
        self.assertEqual(reharm_roots, ["D", "Bb", "F", "C"])
        self.assertIn("min9", reharm_types[0])
        self.assertIn("maj7", reharm_types[1])

    def test_melodic_intelligence_operations(self):
        """Melodic layer creates classical/pop phrase sentences and conversational counter-melodies."""
        lead_events = self.brain.melodic.generate_motif_phrase(
            root_note="D", octave=5, bars=8, bpm=118.0
        )
        self.assertGreaterEqual(len(lead_events), 10)
        for st, dur, pitch, vel in lead_events:
            self.assertGreater(dur, 0.0)
            self.assertGreaterEqual(pitch, 60)
            self.assertLessEqual(pitch, 108)
            self.assertGreaterEqual(vel, 70)
            self.assertLessEqual(vel, 127)

        # Conversational polyphony: counter-melody fills temporal gaps
        total_dur = 8 * (60.0 / 118.0 * 4.0)
        counter_events = self.brain.melodic.generate_counter_melody(
            lead_events=lead_events, total_duration=total_dur, root_note="D", octave=4
        )
        self.assertGreater(len(counter_events), 0)
        for c_st, c_dur, c_pitch, c_vel in counter_events:
            # Verify counter does not clash with peak lead notes
            for l_st, l_dur, _, _ in lead_events:
                lead_busy = (l_st <= c_st <= l_st + l_dur)
                self.assertFalse(lead_busy, f"Counter note at {c_st} clashes with lead ({l_st} - {l_st + l_dur})")

    def test_groove_intelligence_operations(self):
        """Groove layer generates pocket bass patterns and dynamic drum sections."""
        pattern = self.brain.groove.get_bass_pattern(style="carpenter_brut_staccato")
        self.assertIn("steps", pattern)
        self.assertEqual(len(pattern["steps"]), 16)

        # Drum generation for chorus
        drums = self.brain.groove.generate_drums_for_section(
            section_name="chorus", start_bar=32, end_bar=48, bpm=118.0, energy=0.85
        )
        self.assertIn("kick", drums)
        self.assertIn("snare", drums)
        self.assertIn("hihat", drums)
        self.assertEqual(len(drums["kick"]), 64) # 16 bars * 4 kicks
        self.assertEqual(len(drums["snare"]), 32) # 16 bars * 2 snares

    def test_structural_intelligence_operations(self):
        """Structural layer provides all archetypes, section masks, and zero-drop timing."""
        archetypes = self.brain.structural.get_available_archetypes()
        self.assertIn("narrative_7part", archetypes)
        self.assertIn("in_medias_res", archetypes)
        self.assertIn("slow_burn_progressive", archetypes)
        self.assertIn("aaba_classic", archetypes)
        self.assertIn("continuous_drive", archetypes)
        self.assertIn("episodic_rondo", archetypes)

        sections = self.brain.structural.get_sections(archetype_id="narrative_7part", total_bars=96)
        self.assertGreaterEqual(len(sections), 7)

        # Zero-drop window on Bar 32 Beat 4
        z_start, z_end = self.brain.structural.get_zero_drop_window(bar_index=31, bpm=118.0)
        bar_dur = (60.0 / 118.0) * 4.0
        beat_dur = 60.0 / 118.0
        self.assertAlmostEqual(z_start, 31 * bar_dur + 3 * beat_dur, places=3)
        self.assertAlmostEqual(z_end, 32 * bar_dur, places=3)

    def test_timbral_intelligence_operations(self):
        """Timbral layer provides instrument frequency slots, synth topologies, and saturation."""
        profiles = self.brain.timbral.get_all_profiles()
        required_instruments = ["kick", "snare", "hihat", "bass", "chords", "lead", "counter", "pad", "fx"]
        for inst in required_instruments:
            self.assertIn(inst, profiles)
            prof = profiles[inst]
            self.assertEqual(prof.instrument, inst)
            self.assertTrue(prof.freq_range)
            self.assertTrue(prof.synth_topology)
            self.assertTrue(prof.filter_type)
            self.assertGreater(prof.saturation_drive, 0.0)

        # Sidechain ducking configuration
        self.assertTrue(profiles["bass"].sidechain_ducking)
        self.assertTrue(profiles["chords"].sidechain_ducking)
        self.assertTrue(profiles["pad"].sidechain_ducking)
        self.assertFalse(profiles["kick"].sidechain_ducking)


class TestStudioBrainDatabaseDiscovery(unittest.TestCase):
    """Verifies automatic discovery and loading of all databases."""

    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain()

    def test_music_knowledge_base_discovered(self):
        """music_knowledge_base.json must be auto-discovered and verified."""
        self.assertIn("music_knowledge_base", self.brain.databases)
        kb_info = self.brain.databases["music_knowledge_base"]
        self.assertTrue(kb_info["exists"], f"Knowledge base missing at {kb_info['path']}")
        self.assertGreater(kb_info["size_bytes"], 1000)
        self.assertEqual(kb_info["filename"], "music_knowledge_base.json")

    def test_billboard_hits_database_discovered(self):
        """billboard_hits_database.json must be auto-discovered and verified."""
        self.assertIn("billboard_hits", self.brain.databases)
        bb_info = self.brain.databases["billboard_hits"]
        self.assertTrue(bb_info["exists"], f"Billboard hits database missing at {bb_info['path']}")
        self.assertGreater(bb_info["size_bytes"], 5000)
        self.assertEqual(bb_info["filename"], "billboard_hits_database.json")
        self.assertGreaterEqual(len(self.brain.billboard_loader.progressions), 15)

    def test_open_midi_library_11400_files_discovered(self):
        """11,400 Open MIDI chord progressions archive must be auto-discovered and indexed."""
        self.assertIn("midi_library", self.brain.databases)
        midi_info = self.brain.databases["midi_library"]
        self.assertTrue(midi_info["exists"], f"MIDI library missing at {midi_info['path']}")
        self.assertGreater(midi_info["size_bytes"], 1000000)
        self.assertEqual(midi_info["filename"], "free-midi-progressions.zip")

        # OpenMidiLibrary index verification (> 10,000 files)
        self.assertIsNotNone(self.brain.midi_library)
        self.assertGreater(len(self.brain.midi_library.index), 10000)


class TestStudioBrainUnifiedArrangement(unittest.TestCase):
    """Verifies single-pass generation of unified arrangements containing ALL required disciplines."""

    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain()
        cls.arr = cls.brain.generate_arrangement(
            genre="synthwave",
            bpm=118.0,
            bars=96,
            archetype="narrative_7part"
        )

    def test_unified_arrangement_instance_and_metadata(self):
        """Generated object must be UnifiedArrangement with all disciplines and timbral profiles attached."""
        self.assertIsInstance(self.arr, UnifiedArrangement)
        self.assertIsInstance(self.arr, Arrangement)
        self.assertEqual(self.arr.bpm, 118.0)
        self.assertEqual(self.arr.bars, 96)
        self.assertEqual(self.arr.genre, "synthwave")
        self.assertEqual(self.arr.archetype, "narrative_7part")
        self.assertGreater(self.arr.total_duration, 190.0)

        # Disciplines checklist
        for disc in ["Harmonic", "Melodic", "Groove", "Structural", "Timbral"]:
            self.assertIn(disc, self.arr.disciplines)

        # Database sources verified
        self.assertIn("music_knowledge_base", self.arr.database_sources)
        self.assertIn("billboard_hits", self.arr.database_sources)
        self.assertIn("midi_library", self.arr.database_sources)

    def test_all_nine_instrument_tracks_present_and_populated(self):
        """All 9 required tracks plus aliases must be present and contain active NoteEvents."""
        required_tracks = ["kick", "snare", "hihat", "bass", "chords", "lead", "counter", "pad", "fx"]
        for track in required_tracks:
            self.assertIn(track, self.arr.tracks, f"Track {track} missing from arrangement")
            events = self.arr.tracks[track]
            self.assertGreater(len(events), 0, f"Track {track} must contain events")
            for e in events[:10]:
                self.assertIsInstance(e, NoteEvent)
                self.assertGreater(e.duration, 0.0)
                self.assertGreaterEqual(e.pitch, 0)
                self.assertLessEqual(e.pitch, 127)
                self.assertGreater(e.velocity, 0)

        # Backward-compatible aliases
        self.assertIn("hats", self.arr.tracks)
        self.assertIn("pads", self.arr.tracks)

    def test_section_masks_and_zero_drop_in_arrangement(self):
        """Arrangement must honor strict section masks and Bar 32 Beat 4 Zero-Drop cutoff."""
        beat_dur = 60.0 / self.arr.bpm
        bar_dur = beat_dur * 4.0

        # Bar 32 Beat 4 cutoff
        bar32_beat4_start = 31 * bar_dur + 3 * beat_dur - 0.01
        bar32_end = 32 * bar_dur - 0.01

        zero_drop_kicks = [e for e in self.arr.tracks["kick"] if bar32_beat4_start <= e.start_time < bar32_end]
        zero_drop_bass = [e for e in self.arr.tracks["bass"] if bar32_beat4_start <= e.start_time < bar32_end]
        zero_drop_snares = [e for e in self.arr.tracks["snare"] if bar32_beat4_start <= e.start_time < bar32_end]
        zero_drop_fx = [e for e in self.arr.tracks["fx"] if bar32_beat4_start <= e.start_time < bar32_end]

        self.assertEqual(len(zero_drop_kicks), 0, "Bar 32 beat 4 must cut kick for Zero-Drop")
        self.assertEqual(len(zero_drop_bass), 0, "Bar 32 beat 4 must cut bass for Zero-Drop")
        self.assertEqual(len(zero_drop_snares), 0, "Bar 32 beat 4 must cut snare for Zero-Drop")
        self.assertGreater(len(zero_drop_fx), 0, "Bar 32 beat 4 must have sweep FX")

    def test_arrangement_generation_across_all_archetypes(self):
        """StudioBrain must successfully generate unified arrangements across all archetypes."""
        for arch_id in ["in_medias_res", "slow_burn_progressive", "aaba_classic", "continuous_drive", "episodic_rondo"]:
            arr = self.brain.generate_arrangement(genre="synthwave", bpm=120.0, bars=64, archetype=arch_id)
            self.assertIsInstance(arr, UnifiedArrangement)
            self.assertEqual(arr.archetype, arch_id)
            self.assertIn("kick", arr.tracks)
            self.assertIn("bass", arr.tracks)
            self.assertIn("lead", arr.tracks)


class TestStudioBrainDynamicHotReloadingAndIngestion(unittest.TestCase):
    """Verifies dynamic hot-reloading and live ingestion without restart."""

    @classmethod
    def setUpClass(cls):
        cls.brain = get_studio_brain()

    def test_reload_databases(self):
        """reload_databases() must execute cleanly and refresh discovery states."""
        t0 = time.time()
        res = self.brain.reload_databases()
        self.assertEqual(res["status"], "reloaded_successfully")
        self.assertGreaterEqual(res["timestamp"], t0)
        self.assertTrue(res["databases"]["music_knowledge_base"])
        self.assertTrue(res["databases"]["billboard_hits"])
        self.assertTrue(res["databases"]["midi_library"])

    def test_hot_reload_alias(self):
        """hot_reload() must be a working alias for reload_databases()."""
        res = self.brain.hot_reload()
        self.assertEqual(res["status"], "reloaded_successfully")

    def test_dynamic_ingest_progression(self):
        """Harmonic layer dynamically ingests new chord progression."""
        custom_prog = {
            "name": "Lucid Quantum Minor",
            "roots": ["D", "F#", "G", "Bb"],
            "types": ["min9", "dim7", "maj7", "maj9"],
            "genre": "futuristic"
        }
        initial_count = len(self.brain.harmonic.custom_progressions)
        success = self.brain.ingest_data("progression", custom_prog)
        self.assertTrue(success)
        self.assertEqual(len(self.brain.harmonic.custom_progressions), initial_count + 1)
        self.assertIn(custom_prog, self.brain.harmonic.custom_progressions)

    def test_dynamic_ingest_motif(self):
        """Melodic layer dynamically ingests new melodic hook motif."""
        custom_motif = {
            "id": "lucid_cyber_hook_01",
            "notes": [0, 7, 10, 12, 15, 14, 12, 10],
            "rhythm": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        }
        initial_count = len(self.brain.melodic.custom_motifs)
        success = self.brain.ingest_data("motif", custom_motif)
        self.assertTrue(success)
        self.assertEqual(len(self.brain.melodic.custom_motifs), initial_count + 1)
        self.assertIn(custom_motif, self.brain.melodic.custom_motifs)

    def test_dynamic_ingest_groove(self):
        """Groove layer dynamically ingests custom bass groove pattern."""
        custom_groove = {
            "name": "Syncopated Cyber Break",
            "steps": [(0, 0.4, 110), (2, 0.25, 85), (6, 0.35, 95), (10, 0.3, 90)]
        }
        initial_count = len(self.brain.groove.custom_grooves)
        success = self.brain.ingest_data("groove", custom_groove)
        self.assertTrue(success)
        self.assertEqual(len(self.brain.groove.custom_grooves), initial_count + 1)

    def test_dynamic_ingest_archetype(self):
        """Structural layer dynamically ingests custom arrangement archetype."""
        class CustomAmbientArchetype:
            def build_sections(self, total_bars=96):
                return []
        
        success = self.brain.ingest_data("archetype", {"id": "custom_ambient_flow", "obj": CustomAmbientArchetype()})
        self.assertTrue(success)
        self.assertIn("custom_ambient_flow", self.brain.structural.get_available_archetypes())

    def test_dynamic_ingest_timbre(self):
        """Timbral layer dynamically ingests / updates custom timbral profile."""
        custom_profile = TimbralProfile(
            instrument="granular_pad",
            freq_range="200 Hz - 8 kHz",
            synth_topology="Granular Cloud Synthesizer",
            filter_type="Formant 4-pole Filter",
            saturation_drive=1.45,
            space_reverb_send=0.75,
            sidechain_ducking=True,
            eq_target={"air_12khz": 2.5}
        )
        success = self.brain.ingest_data("timbre", {"instrument": "granular_pad", "profile": custom_profile})
        self.assertTrue(success)
        self.assertIn("granular_pad", self.brain.timbral.profiles)

    def test_dynamic_ingest_invalid_type_raises_error(self):
        """Unknown data_type must raise ValueError."""
        with self.assertRaises(ValueError):
            self.brain.ingest_data("invalid_data_category_123", {})

    def test_diagnostic_summary(self):
        """summary() provides comprehensive diagnostic health metrics."""
        summary = self.brain.summary()
        self.assertIn("studio_brain", summary)
        self.assertIn("version", summary)
        self.assertIn("databases_discovered", summary)
        self.assertIn("layers", summary)
        self.assertEqual(len(summary["layers"]), 5)
        for layer in ["harmonic", "melodic", "groove", "structural", "timbral"]:
            self.assertIn(layer, summary["layers"])


if __name__ == "__main__":
    unittest.main()

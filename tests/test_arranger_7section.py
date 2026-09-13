"""
tests/test_arranger_7section.py - Masterclass 7-Section & Multi-Archetype Arranger Verification
Tests:
1. 7-Part Narrative Arc (Bars 1-8 Intro, 9-24 Verse, 25-31 Buildup, 32 Zero-Drop, 33-48 Chorus, 49-64 Breakdown, 65-80 Climax, 81-96 Outro)
2. Zero-Drop rule on Bar 32 Beat 4 (Total silence on kick/bass/drums with subtle transition sweep)
3. Active track masks across all 9 instruments (kick, snare, hihat, bass, chords, lead, counter, pad, fx)
4. Human chord progressions from OpenMidiLoader and MusicKnowledgeBase
5. Multiple arrangement archetypes (In Medias Res, Slow-Burn Progressive, AABA Classic, Continuous Drive, Episodic Rondo)
"""

import unittest
from src.composer.arranger import create_arrangement, ARCHETYPES, Arrangement
from src.composer.open_midi_loader import OpenMidiLoader

class TestArrangerMasterclass(unittest.TestCase):

    def setUp(self):
        self.bpm = 118.0
        self.bars = 96
        self.beat_dur = 60.0 / self.bpm
        self.bar_dur = self.beat_dur * 4.0
        self.arr = create_arrangement(genre="synthwave", bpm=self.bpm, bars=self.bars, archetype="narrative_7part")

    def _events_in_bar_range(self, track_name: str, start_bar: int, end_bar: int):
        t_start = start_bar * self.bar_dur - 0.05
        t_end = end_bar * self.bar_dur - 0.05
        return [e for e in self.arr.tracks[track_name] if t_start <= e.start_time < t_end]

    def test_tracks_and_duration(self):
        """All 9 required instrument tracks plus backward-compatible aliases must exist."""
        required_tracks = ["kick", "snare", "hihat", "bass", "chords", "lead", "counter", "pad", "fx"]
        for t in required_tracks:
            self.assertIn(t, self.arr.tracks, f"Track {t} must be present in arrangement")
        self.assertIn("hats", self.arr.tracks)
        self.assertIn("pads", self.arr.tracks)
        self.assertGreater(self.arr.total_duration, 190.0)

    def test_section_1_intro(self):
        """Intro (Bars 1-8): Ambient pad + subtle texture, NO kick/bass."""
        kicks = self._events_in_bar_range("kick", 0, 8)
        bass = self._events_in_bar_range("bass", 0, 8)
        pads = self._events_in_bar_range("pad", 0, 8)
        fx = self._events_in_bar_range("fx", 0, 8)

        self.assertEqual(len(kicks), 0, "Intro must have NO kicks")
        self.assertEqual(len(bass), 0, "Intro must have NO bass")
        self.assertGreater(len(pads), 0, "Intro must have ambient pads")
        self.assertGreater(len(fx), 0, "Intro must have subtle texture/FX")

    def test_section_2_verse(self):
        """Verse 1 (Bars 9-24): Introduces syncopated pocket bassline + soft hats. No lead hook yet."""
        bass = self._events_in_bar_range("bass", 8, 24)
        hats = self._events_in_bar_range("hihat", 8, 24)
        leads = self._events_in_bar_range("lead", 8, 24)

        self.assertGreater(len(bass), 0, "Verse 1 must introduce pocket bassline")
        self.assertGreater(len(hats), 0, "Verse 1 must have soft hats")
        self.assertEqual(len(leads), 0, "Verse 1 must have NO lead hook yet")

    def test_section_3_buildup(self):
        """Build-up (Bars 25-31): Rising snare fill, rising hi-pass energy."""
        snares = self._events_in_bar_range("snare", 24, 31)
        fx = self._events_in_bar_range("fx", 24, 31)

        self.assertGreater(len(snares), 30, "Buildup must feature accelerating snare roll")
        self.assertGreater(len(fx), 0, "Buildup must have rising energy riser FX")

    def test_section_4_bar_32_zero_drop(self):
        """Bar 32 'Zero-Drop': TOTAL SILENCE or subtle transition sweep on beat 4, cutting kick and bass."""
        bar32_start = 31 * self.bar_dur
        beat4_start = bar32_start + 3 * self.beat_dur - 0.01
        bar32_end = 32 * self.bar_dur - 0.01

        beat4_kicks = [e for e in self.arr.tracks["kick"] if beat4_start <= e.start_time < bar32_end]
        beat4_bass = [e for e in self.arr.tracks["bass"] if beat4_start <= e.start_time < bar32_end]
        beat4_snares = [e for e in self.arr.tracks["snare"] if beat4_start <= e.start_time < bar32_end]
        beat4_fx = [e for e in self.arr.tracks["fx"] if beat4_start <= e.start_time < bar32_end]

        self.assertEqual(len(beat4_kicks), 0, "Bar 32 beat 4 must cut kick")
        self.assertEqual(len(beat4_bass), 0, "Bar 32 beat 4 must cut bass")
        self.assertEqual(len(beat4_snares), 0, "Bar 32 beat 4 must cut snare")
        self.assertGreater(len(beat4_fx), 0, "Bar 32 beat 4 must have subtle transition sweep")

    def test_section_5_chorus(self):
        """Chorus 1 (Bars 33-48): Full impact drop, 4-on-the-floor kick, driving bass, lead motif hook."""
        kicks = self._events_in_bar_range("kick", 32, 48)
        bass = self._events_in_bar_range("bass", 32, 48)
        lead = self._events_in_bar_range("lead", 32, 48)

        self.assertGreaterEqual(len(kicks), 64, "Chorus 1 must have 4-on-the-floor kick (64 kicks across 16 bars)")
        self.assertGreater(len(bass), 100, "Chorus 1 must have driving bass")
        self.assertGreater(len(lead), 50, "Chorus 1 must introduce lead motif hook")

    def test_section_6_breakdown(self):
        """Breakdown (Bars 49-64): Cuts drums, introduces emotional piano/Rhodes counterpoint."""
        kicks = self._events_in_bar_range("kick", 48, 64)
        snares = self._events_in_bar_range("snare", 48, 64)
        chords = self._events_in_bar_range("chords", 48, 64)
        counter = self._events_in_bar_range("counter", 48, 64)

        self.assertEqual(len(kicks), 0, "Breakdown must CUT drums (no kick)")
        self.assertEqual(len(snares), 0, "Breakdown must CUT drums (no snare)")
        self.assertGreater(len(chords), 0, "Breakdown must feature emotional piano/Rhodes chords")
        self.assertGreater(len(counter), 0, "Breakdown must feature emotional piano/Rhodes counterpoint")

    def test_section_7_climax_drop(self):
        """Climax Drop (Bars 65-80): Highest energy, lead motif layered with counter-melody and turnaround drum fills."""
        kicks = self._events_in_bar_range("kick", 64, 80)
        lead = self._events_in_bar_range("lead", 64, 80)
        counter = self._events_in_bar_range("counter", 64, 80)
        snares = self._events_in_bar_range("snare", 64, 80)

        self.assertGreaterEqual(len(kicks), 64, "Climax Drop must have 4-on-the-floor driving kick")
        self.assertGreater(len(lead), 50, "Climax Drop must feature lead motif hook")
        self.assertGreater(len(counter), 0, "Climax Drop must layer counter-melody simultaneously")
        self.assertGreater(len(snares), 32, "Climax Drop must have snare backbeats and turnaround fills")

    def test_section_8_outro(self):
        """Outro (Bars 81-96): Deconstructive fadeout."""
        pads = self._events_in_bar_range("pad", 80, 96)
        late_kicks = self._events_in_bar_range("kick", 88, 96)
        late_bass = self._events_in_bar_range("bass", 88, 96)

        self.assertGreater(len(pads), 0, "Outro must have decaying pad")
        self.assertEqual(len(late_kicks), 0, "Final 8 bars of outro must cut kick completely")
        self.assertEqual(len(late_bass), 0, "Final 8 bars of outro must cut bass completely")

    def test_multiple_archetypes(self):
        """Arranger must support distinct archetypes without forcing cookie-cutter structure."""
        archetype_ids = ["narrative_7part", "in_medias_res", "slow_burn_progressive", "aaba_classic", "continuous_drive", "episodic_rondo"]
        for arch_id in archetype_ids:
            arr = create_arrangement(genre="synthwave", bpm=118.0, bars=96, archetype=arch_id)
            self.assertEqual(arr.archetype, arch_id)
            self.assertGreater(len(arr.sections), 0)
            self.assertGreater(len(arr.tracks["pad"]), 0)
            self.assertGreater(len(arr.tracks["bass"]), 0)

    def test_open_midi_loader_integration(self):
        """OpenMidiLoader must provide human progressions with micro-timing and voicings."""
        loader = OpenMidiLoader()
        prog = loader.get_progression(genre="synthwave", section="chorus")
        self.assertIn("roots", prog)
        self.assertIn("types", prog)
        self.assertIn("human_offsets_ms", prog)
        self.assertIn("velocities", prog)
        self.assertGreater(len(prog["roots"]), 0)

if __name__ == "__main__":
    unittest.main()

"""
tests/test_ingest_hub.py - Unit Test Suite for Modular Data Ingestion & StudioBrain Dynamic Extensibility
Verifies:
1. Ingesting single MIDI and zip archive into storage/samples/midi_library/
2. Ingesting harmonic progression JSONs into src/composer/database/
3. Ingesting MusicXML leadsheets with chord & melody extraction
4. Ingesting markdown chord charts
5. Dynamic on-the-fly absorption of new datasets by StudioBrain without restarts or code edits
"""

import os
import io
import json
import zipfile
import unittest
import mido

from src.composer.ingest_hub import IngestionHub, get_ingest_hub
from src.composer.knowledge_base import StudioBrain, get_studio_brain, MusicKnowledgeBase


class TestIngestionHubAndStudioBrain(unittest.TestCase):

    def setUp(self):
        self.hub = get_ingest_hub()
        self.brain = get_studio_brain()
        # Clean any leftover test artifacts from prior runs
        self.hub.clean_test_artifacts(pattern="test_*")

    def tearDown(self):
        # Clean up test artifacts created during testing
        self.hub.clean_test_artifacts(pattern="test_*")

    def _create_mock_midi_bytes(self, note: int = 60, duration_ticks: int = 480) -> bytes:
        """Helper to create valid SMF MIDI bytes."""
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=duration_ticks))
        buf = io.BytesIO()
        mid.save(file=buf)
        return buf.getvalue()

    def test_01_ingest_single_midi(self):
        """Verify single MIDI file ingestion, validation, and storage."""
        midi_data = self._create_mock_midi_bytes(note=62) # D4
        res = self.hub.ingest_midi(
            source=midi_data,
            filename="test_lead_motif.mid",
            metadata={"instrument": "supersaw_lead"}
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "midi_file")
        self.assertTrue(os.path.exists(res["file_path"]))
        self.assertEqual(res["total_note_events"], 1)
        self.assertEqual(res["estimated_bpm"], 120.0)
        self.assertEqual(res["estimated_root"], "D")

    def test_02_ingest_midi_zip_archive(self):
        """Verify zip archive containing multiple MIDIs is validated and ingested."""
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            zf.writestr("pack/track_01.mid", self._create_mock_midi_bytes(note=60))
            zf.writestr("pack/track_02.mid", self._create_mock_midi_bytes(note=64))
            zf.writestr("pack/track_03.mid", self._create_mock_midi_bytes(note=67))

        res = self.hub.ingest_midi(
            source=zip_buf.getvalue(),
            filename="test_midi_collection.zip"
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "midi_zip_archive")
        self.assertTrue(os.path.exists(res["file_path"]))
        self.assertEqual(res["midi_files_count"], 3)

    def test_03_ingest_musicxml_leadsheet(self):
        """Verify MusicXML parsing, harmony extraction, and dynamic progression creation."""
        xml_source = """<?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
          <work><work-title>Test Autumn Modal Drift</work-title></work>
          <part id="P1">
            <measure number="1">
              <attributes>
                <divisions>1</divisions>
                <key><fifths>-1</fifths><mode>minor</mode></key>
                <time><beats>4</beats><beat-type>4</beat-type></time>
              </attributes>
              <harmony>
                <root><root-step>D</root-step></root>
                <kind>minor-seventh</kind>
              </harmony>
              <note><pitch><step>D</step><octave>4</octave></pitch><duration>4</duration></note>
            </measure>
            <measure number="2">
              <harmony>
                <root><root-step>G</root-step></root>
                <kind>dominant</kind>
              </harmony>
              <note><pitch><step>B</step><octave>4</octave></pitch><duration>4</duration></note>
            </measure>
            <measure number="3">
              <harmony>
                <root><root-step>C</root-step></root>
                <kind>major-seventh</kind>
              </harmony>
              <note><pitch><step>C</step><octave>5</octave></pitch><duration>4</duration></note>
            </measure>
            <measure number="4">
              <harmony>
                <root><root-step>F</root-step></root>
                <kind>major-seventh</kind>
              </harmony>
              <note><pitch><step>A</step><octave>4</octave></pitch><duration>4</duration></note>
            </measure>
          </part>
        </score-partwise>
        """

        res = self.hub.ingest_leadsheet_musicxml(
            source=xml_source.encode("utf-8"),
            filename="test_autumn_modal.musicxml",
            genre="modal_jazz_leadsheet",
            section="chorus"
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["title"], "Test Autumn Modal Drift")
        self.assertEqual(res["key"], "D")
        self.assertEqual(res["chords_count"], 4)
        self.assertEqual(res["progression"]["roots"], ["D", "G", "C", "F"])
        self.assertEqual(res["progression"]["types"], ["min7", "dom7", "maj7", "maj7"])

        # Confirm StudioBrain dynamically indexed modal_jazz_leadsheet
        self.assertIn("modal_jazz_leadsheet", self.brain.list_genres())
        p = self.brain.get_progression(genre="modal_jazz_leadsheet", section="chorus")
        self.assertEqual(p["roots"], ["D", "G", "C", "F"])

    def test_04_ingest_markdown_chords(self):
        """Verify markdown chord chart extraction into StudioBrain."""
        md_content = """# Deepdive Research: Cyber Darksynth
## Chorus Progressions
| Section | Chords | Mood |
| :--- | :--- | :--- |
| Chorus | Dm - Eb - Bb - A | Menacing Heavy |
| Verse | Dm - C - Bb - A | Rolling Cyber |
"""
        res = self.hub.ingest_markdown_chords(
            source=md_content,
            filename="test_cyber_darksynth_research",
            genre="cyber_darksynth_extracted"
        )

        self.assertEqual(res["status"], "success")
        self.assertIn("cyber_darksynth_extracted", self.brain.list_genres())
        prog = self.brain.get_progression(genre="cyber_darksynth_extracted")
        self.assertTrue(len(prog["roots"]) >= 4)

    def test_05_dynamic_absorption_without_restart(self):
        """
        TASK 3 VERIFICATION:
        Confirm StudioBrain dynamically absorbs a mock new knowledge dataset
        (test_new_genre_database.json) on the fly without requiring code edits or restarts.
        """
        mock_dataset = {
            "metadata": {
                "database_name": "Cyberpunk Hyperpop 2026",
                "version": "1.0.0",
                "genre": "cyberpunk_hyperpop"
            },
            "progressions": [
                {
                    "id": "hyper_hook_01",
                    "title": "Neon Glitch Outrun Drop",
                    "genre": "cyberpunk_hyperpop",
                    "section": "chorus",
                    "key": "F#",
                    "mode": "minor",
                    "roots": ["F#", "D#", "B", "C#"],
                    "types": ["min7", "maj7", "maj9", "dom7"],
                    "roman_numerals": "i7 - VImaj7 - IVmaj9 - V7",
                    "style_tags": ["hyperpop", "glitch_outrun", "cyberpunk"]
                },
                {
                    "id": "hyper_verse_01",
                    "title": "Bitcrushed Sub Intro",
                    "genre": "cyberpunk_hyperpop",
                    "section": "verse",
                    "key": "F#",
                    "mode": "minor",
                    "roots": ["F#", "B", "G#", "C#"],
                    "types": ["min9", "maj7", "min7", "dom7"],
                    "roman_numerals": "i9 - IVmaj7 - ii7 - V7",
                    "style_tags": ["sub_bass", "intimate_intro"]
                }
            ],
            "melodic_motifs": [
                {
                    "id": "hyper_lead_motif",
                    "name": "Glitch Lead Hook",
                    "genre": "cyberpunk_hyperpop",
                    "notes": [0, 3, 5, 7, 10, 12, 10, 7],
                    "rhythm": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
                }
            ],
            "bass_grooves": [
                {
                    "id": "hyper_808_glide",
                    "name": "808 Stutter Glide",
                    "genre": "cyberpunk_hyperpop",
                    "style": "808_stutter_glide",
                    "steps": [
                        (0, 0.8, 127), (2, 0.4, 90), (4, 0.8, 120), (6, 0.5, 95),
                        (8, 0.8, 125), (10, 0.4, 90), (12, 0.8, 120), (14, 0.9, 127)
                    ]
                }
            ]
        }

        # 1. Ingest via IngestionHub
        res = self.hub.ingest_progression_json(
            source=mock_dataset,
            filename="test_new_genre_database.json"
        )
        self.assertEqual(res["status"], "success")

        # 2. Verify StudioBrain immediately absorbed the new genre without restart
        genres = self.brain.list_genres()
        self.assertIn("cyberpunk_hyperpop", genres, "cyberpunk_hyperpop should be dynamically present in StudioBrain!")

        # 3. Query the dynamically absorbed progression
        chorus_prog = self.brain.get_progression(genre="cyberpunk_hyperpop", section="chorus")
        self.assertIsNotNone(chorus_prog)
        self.assertEqual(chorus_prog["roots"], ["F#", "D#", "B", "C#"])
        self.assertEqual(chorus_prog["types"], ["min7", "maj7", "maj9", "dom7"])
        self.assertEqual(chorus_prog["title"], "Neon Glitch Outrun Drop")

        verse_prog = self.brain.get_progression(genre="cyberpunk_hyperpop", section="verse")
        self.assertIsNotNone(verse_prog)
        self.assertEqual(verse_prog["roots"], ["F#", "B", "G#", "C#"])

        # 4. Query the dynamically absorbed motif
        motif = self.brain.get_motif(genre="cyberpunk_hyperpop")
        self.assertIsNotNone(motif)
        self.assertEqual(motif["notes"], [0, 3, 5, 7, 10, 12, 10, 7])

        # 5. Query the dynamically absorbed bass groove
        groove = self.brain.get_bass_pattern(style="808_stutter_glide")
        self.assertIsNotNone(groove)
        self.assertEqual(len(groove["steps"]), 8)

        # 6. Verify MusicKnowledgeBase backward-compatible alias also sees it immediately
        legacy_kb = MusicKnowledgeBase()
        legacy_prog = legacy_kb.get_progression(genre="cyberpunk_hyperpop", section="chorus")
        self.assertEqual(legacy_prog["roots"], ["F#", "D#", "B", "C#"])

    def test_06_hub_status_reporting(self):
        """Verify overall hub status and inventory reporting."""
        status = self.hub.get_status()
        self.assertIn("midi_assets_count", status)
        self.assertIn("database_files_count", status)
        self.assertIn("studio_brain_summary", status)
        self.assertGreaterEqual(status["studio_brain_summary"]["genres_count"], 48)


if __name__ == "__main__":
    unittest.main()

"""
scripts/verify_ingestion_hub.py - End-to-End Ingestion Hub & StudioBrain Extensibility Validator
Demonstrates:
1. Review of dataset ingestion pathways (MIDI, JSON, MusicXML leadsheets, Markdown).
2. Standardized ingestion via IngestionHub:
   - MIDI SMF / Zip into storage/samples/midi_library/
   - Harmonic progression JSON into src/composer/database/
   - Leadsheets / MusicXML into storage/samples/leadsheets/
3. Dynamic absorption of a mock dataset (test_new_genre_database.json) by StudioBrain
   without code edits or process restarts.
"""

import os
import io
import sys
import json
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import mido

from src.composer.ingest_hub import get_ingest_hub
from src.composer.knowledge_base import get_studio_brain, StudioBrain, MusicKnowledgeBase


def print_banner(text: str):
    print("\n" + "=" * 75)
    print(f"  {text}")
    print("=" * 75)


def run_verification():
    hub = get_ingest_hub()
    brain = get_studio_brain()

    # Step 0: Baseline state
    print_banner("STEP 0: BASELINE STUDIOBRAIN & INGESTION HUB STATUS")
    status_initial = hub.get_status()
    initial_genres = brain.list_genres()
    print(f"[*] Initial Active Databases: {status_initial['database_files_count']}")
    print(f"[*] Initial Active Genres: {len(initial_genres)}")
    print(f"[*] Sample genres: {', '.join(initial_genres[:8])}...")
    print(f"[*] Initial Progressions Indexed: {brain.summary()['total_indexed_progressions']}")

    # Step 1: Ingest new MIDI file
    print_banner("STEP 1: INGESTING NEW MIDI SMF ASSET")
    test_mid = mido.MidiFile()
    track = mido.MidiTrack()
    test_mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(128)))
    # Play a quick D minor arp: D4, F4, A4, C5
    for note, time_offset in [(62, 0), (65, 120), (69, 120), (72, 120)]:
        track.append(mido.Message('note_on', note=note, velocity=105, time=time_offset))
        track.append(mido.Message('note_off', note=note, velocity=0, time=100))
    midi_buf = io.BytesIO()
    test_mid.save(file=midi_buf)

    midi_res = hub.ingest_midi(
        source=midi_buf.getvalue(),
        filename="test_d_minor_synth_arp.mid",
        metadata={"author": "Lucid Ingest Hub", "purpose": "Arp Motif"}
    )
    print(f"  ✓ Ingested: {midi_res['filename']}")
    print(f"    Path: {midi_res['file_path']}")
    print(f"    Tracks: {midi_res['tracks_count']} | Note events: {midi_res['total_note_events']}")
    print(f"    Estimated BPM: {midi_res['estimated_bpm']} | Estimated Root: {midi_res['estimated_root']}")
    assert os.path.exists(midi_res["file_path"]), "MIDI file not created!"

    # Step 2: Ingest MusicXML Leadsheet
    print_banner("STEP 2: INGESTING MUSICXML LEADSHEET & CHORD EXTRACTION")
    musicxml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <score-partwise version="3.1">
      <work><work-title>Modal Drift in F</work-title></work>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>1</divisions>
            <key><fifths>-1</fifths><mode>major</mode></key>
            <time><beats>4</beats><beat-type>4</beat-type></time>
          </attributes>
          <harmony>
            <root><root-step>F</root-step></root>
            <kind>major-seventh</kind>
          </harmony>
          <note><pitch><step>F</step><octave>4</octave></pitch><duration>4</duration></note>
        </measure>
        <measure number="2">
          <harmony>
            <root><root-step>G</root-step></root>
            <kind>minor-seventh</kind>
          </harmony>
          <note><pitch><step>B</step><alter>-1</alter><octave>4</octave></pitch><duration>4</duration></note>
        </measure>
        <measure number="3">
          <harmony>
            <root><root-step>A</root-step></root>
            <kind>minor-seventh</kind>
          </harmony>
          <note><pitch><step>C</step><octave>5</octave></pitch><duration>4</duration></note>
        </measure>
        <measure number="4">
          <harmony>
            <root><root-step>B</root-step><root-alter>-1</root-alter></root>
            <kind>major-seventh</kind>
          </harmony>
          <note><pitch><step>D</step><octave>5</octave></pitch><duration>4</duration></note>
        </measure>
      </part>
    </score-partwise>
    """
    leadsheet_res = hub.ingest_leadsheet_musicxml(
        source=musicxml_content.encode("utf-8"),
        filename="test_modal_drift.musicxml",
        genre="modal_breeze",
        section="verse"
    )
    print(f"  ✓ Leadsheet: '{leadsheet_res['title']}' (Key: {leadsheet_res['key']})")
    print(f"    Raw XML: {leadsheet_res['raw_leadsheet_path']}")
    print(f"    Progressions JSON: {leadsheet_res['progression_json_path']}")
    print(f"    Chords ({leadsheet_res['chords_count']}): {[c['chord_symbol'] for c in leadsheet_res['progression']['chords']]}")
    print(f"    Roots: {leadsheet_res['progression']['roots']} | Types: {leadsheet_res['progression']['types']}")
    assert "modal_breeze" in brain.list_genres(), "modal_breeze should be indexed in StudioBrain!"

    # Step 3: Dynamic Knowledge Dataset Absorption (Task 3)
    print_banner("STEP 3: DYNAMIC LIVE ABSORPTION OF MOCK NEW GENRE DATASET")
    mock_new_genre = {
        "metadata": {
            "database_name": "Afro House & Melodic Future Bass 2026",
            "version": "1.0.0",
            "genre": "afro_melodic_future"
        },
        "progressions": [
            {
                "id": "afro_future_drop_01",
                "title": "Sunlit Serengeti Anthem",
                "genre": "afro_melodic_future",
                "section": "chorus",
                "key": "Ab",
                "mode": "minor",
                "roots": ["Ab", "F", "Db", "Eb"],
                "types": ["min9", "min7", "maj7", "dom7"],
                "chords": [
                    {"chord_symbol": "Abm9", "root": "Ab", "type": "min9"},
                    {"chord_symbol": "Fm7", "root": "F", "type": "min7"},
                    {"chord_symbol": "Dbmaj7", "root": "Db", "type": "maj7"},
                    {"chord_symbol": "Eb7", "root": "Eb", "type": "dom7"}
                ],
                "roman_numerals": "i9 - vi7 - IVmaj7 - V7",
                "style_tags": ["afro_house", "polyrhythmic", "sunset_vibe"]
            },
            {
                "id": "afro_future_verse_01",
                "title": "Kalimba Shaker Pocket",
                "genre": "afro_melodic_future",
                "section": "verse",
                "key": "Ab",
                "mode": "minor",
                "roots": ["Ab", "Db", "Eb", "Ab"],
                "types": ["min7", "maj7", "dom7", "min7"],
                "chords": [
                    {"chord_symbol": "Abm7", "root": "Ab", "type": "min7"},
                    {"chord_symbol": "Dbmaj7", "root": "Db", "type": "maj7"},
                    {"chord_symbol": "Eb7", "root": "Eb", "type": "dom7"},
                    {"chord_symbol": "Abm7", "root": "Ab", "type": "min7"}
                ],
                "roman_numerals": "i7 - IVmaj7 - V7 - i7",
                "style_tags": ["minimal_pocket", "organic_percussion"]
            }
        ],
        "melodic_motifs": [
            {
                "id": "afro_future_hook_motif",
                "name": "Pentatonic Kalimba Ostinato",
                "genre": "afro_melodic_future",
                "notes": [0, 3, 5, 7, 10, 7, 5, 0],
                "rhythm": [0.0, 0.75, 1.5, 2.0, 2.75, 3.25, 3.75, 4.0]
            }
        ],
        "bass_grooves": [
            {
                "id": "afro_sub_groove_01",
                "name": "Syncopated 3-against-2 Sub Bounce",
                "genre": "afro_melodic_future",
                "style": "afro_polyrhythmic_sub",
                "steps": [
                    (0, 0.70, 115), (3, 0.50, 95), (6, 0.70, 110),
                    (8, 0.40, 85), (11, 0.70, 115), (14, 0.60, 105)
                ]
            }
        ]
    }

    print("[*] Ingesting 'test_new_genre_database.json' into src/composer/database/...")
    t_ingest_start = time.time()
    ingest_json_res = hub.ingest_progression_json(
        source=mock_new_genre,
        filename="test_new_genre_database.json"
    )
    ingest_dur_ms = (time.time() - t_ingest_start) * 1000
    print(f"  ✓ Ingested in {ingest_dur_ms:.2f} ms: {ingest_json_res['filename']}")
    print(f"  ✓ Progressions count: {ingest_json_res['progressions_count']}")
    print(f"  ✓ Genres indexed: {ingest_json_res['genres_indexed']}")

    # Step 4: Verify Zero-Restart Live Query
    print_banner("STEP 4: VERIFYING ZERO-RESTART LIVE QUERY ON STUDIOBRAIN")
    all_genres_now = brain.list_genres()
    print(f"[*] Total active genres in StudioBrain now: {len(all_genres_now)}")
    assert "afro_melodic_future" in all_genres_now, "afro_melodic_future must be immediately in list_genres()!"
    print("  ✓ Genre 'afro_melodic_future' dynamically registered in StudioBrain index!")

    # 4.1 Query chorus progression
    p_chorus = brain.get_progression(genre="afro_melodic_future", section="chorus")
    print(f"\n[Dynamic Query 1 - Chorus]: {p_chorus['title']} ({p_chorus['genre']})")
    print(f"  • Roots: {p_chorus['roots']}")
    print(f"  • Types: {p_chorus['types']}")
    print(f"  • Chords: {[c['chord_symbol'] for c in p_chorus['chords']]}")
    print(f"  • Roman Numerals: {p_chorus['roman_numerals']}")
    assert p_chorus["roots"] == ["Ab", "F", "Db", "Eb"]
    assert p_chorus["title"] == "Sunlit Serengeti Anthem"

    # 4.2 Query verse progression
    p_verse = brain.get_progression(genre="afro_melodic_future", section="verse")
    print(f"\n[Dynamic Query 2 - Verse]: {p_verse['title']}")
    print(f"  • Roots: {p_verse['roots']}")
    assert p_verse["roots"] == ["Ab", "Db", "Eb", "Ab"]

    # 4.3 Query motif
    motif = brain.get_motif(genre="afro_melodic_future")
    print(f"\n[Dynamic Query 3 - Melodic Motif]: {motif['name']}")
    print(f"  • Intervals: {motif['notes']}")
    print(f"  • Rhythm: {motif['rhythm']}")
    assert motif["notes"] == [0, 3, 5, 7, 10, 7, 5, 0]

    # 4.4 Query bass groove
    groove = brain.get_bass_pattern(style="afro_polyrhythmic_sub")
    print(f"\n[Dynamic Query 4 - Bass Groove]: {groove['name']}")
    print(f"  • Steps ({len(groove['steps'])}): {groove['steps']}")
    assert len(groove["steps"]) == 6

    # 4.5 Verify MusicKnowledgeBase backward-compatible alias also sees it immediately
    legacy_kb = MusicKnowledgeBase()
    legacy_chorus = legacy_kb.get_progression(genre="afro_melodic_future", section="chorus")
    assert legacy_chorus["roots"] == ["Ab", "F", "Db", "Eb"]
    print(f"\n[Backward Compatibility]: MusicKnowledgeBase() dynamically returned identical progression roots: {legacy_chorus['roots']}")

    # Step 5: Clean Test Artifacts
    print_banner("STEP 5: CLEANING UP TEST ARTIFACTS")
    cleaned = hub.clean_test_artifacts(pattern="test_*")
    print(f"[*] Safely cleaned {cleaned} test artifact(s) from database, midi, and leadsheet folders.")
    brain.refresh(force=True)
    print(f"[*] StudioBrain refreshed. Current active genres: {len(brain.list_genres())}")

    print_banner("ALL VERIFICATION CHECKS PASSED: MODULAR INGESTION HUB & STUDIOBRAIN CONFIRMED 100% OPERATIONAL")


if __name__ == "__main__":
    run_verification()

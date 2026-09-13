"""
src/composer/ingest_hub.py - Modular Data Ingestion & Extensibility Hub
Standardized ingestion interface for the Lucid Hubble headless music studio:
1. Ingests new MIDI files/zips into storage/samples/midi_library/.
2. Ingests new harmonic progression JSONs into src/composer/database/.
3. Ingests new leadsheets / MusicXML files into storage/samples/leadsheets/.
4. Ingests markdown research chord charts.
5. Auto-updates StudioBrain's live index on the fly without code edits or restarts.
"""

import os
import io
import sys
import glob
import json
import shutil
import zipfile
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import mido

from src.composer.knowledge_base import StudioBrain, get_studio_brain

# Base project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
MIDI_LIBRARY_DIR = os.path.join(STORAGE_DIR, "samples", "midi_library")
DATABASE_DIR = os.path.join(PROJECT_ROOT, "src", "composer", "database")
LEADSHEET_DIR = os.path.join(STORAGE_DIR, "samples", "leadsheets")

# Pitch conversion tables
FIFTHS_TO_KEY = {
    0: ("C", "A"), 1: ("G", "E"), 2: ("D", "B"), 3: ("A", "F#"), 4: ("E", "C#"),
    5: ("B", "G#"), 6: ("F#", "D#"), 7: ("C#", "A#"), -1: ("F", "D"), -2: ("Bb", "G"),
    -3: ("Eb", "C"), -4: ("Ab", "F"), -5: ("Db", "Bb"), -6: ("Gb", "Eb"), -7: ("Cb", "Ab")
}

MUSICXML_KIND_MAP = {
    "major": "maj",
    "minor": "min",
    "major-seventh": "maj7",
    "minor-seventh": "min7",
    "dominant": "dom7",
    "dominant-seventh": "dom7",
    "major-ninth": "maj9",
    "minor-ninth": "min9",
    "dominant-ninth": "dom9",
    "diminished": "dim",
    "diminished-seventh": "dim7",
    "half-diminished": "half-dim7",
    "augmented": "aug",
    "augmented-seventh": "aug7",
    "suspended-fourth": "sus4",
    "suspended-second": "sus2",
    "major-sixth": "maj6",
    "minor-sixth": "min6",
    "power": "5"
}


class IngestionHub:
    """
    Unified Ingestion & Extensibility Engine for Lucid Hubble.
    Provides standardized methods to ingest, validate, convert, and hot-reload
    MIDI libraries, harmonic progression databases, leadsheets, and MusicXML files.
    """

    _instance: Optional['IngestionHub'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IngestionHub, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        midi_dir: Optional[str] = None,
        database_dir: Optional[str] = None,
        leadsheet_dir: Optional[str] = None
    ):
        if getattr(self, "_initialized", False):
            return
        self.midi_dir = midi_dir or MIDI_LIBRARY_DIR
        self.database_dir = database_dir or DATABASE_DIR
        self.leadsheet_dir = leadsheet_dir or LEADSHEET_DIR

        # Ensure target directories exist
        os.makedirs(self.midi_dir, exist_ok=True)
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.leadsheet_dir, exist_ok=True)

        self.brain = get_studio_brain(self.database_dir)
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'IngestionHub':
        """Convenience singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ==========================================================================
    # 1. MIDI Ingestion (Single files or Zip archives)
    # ==========================================================================

    def ingest_midi(
        self,
        source: Union[str, bytes, io.BytesIO],
        filename: Optional[str] = None,
        destination_subfolder: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingests a standard MIDI file (.mid, .midi) or zip archive of MIDIs into storage/samples/midi_library/.
        Validates the SMF stream with mido, extracts musical statistics, writes to storage,
        and triggers StudioBrain/OpenMidiLibrary cache invalidation.
        """
        target_dir = self.midi_dir
        if destination_subfolder:
            target_dir = os.path.join(target_dir, destination_subfolder)
            os.makedirs(target_dir, exist_ok=True)

        # 1. Resolve raw bytes and filename
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source MIDI file not found: {source}")
            fname = filename or os.path.basename(source)
            with open(source, "rb") as f:
                data = f.read()
        elif isinstance(source, io.BytesIO):
            fname = filename or "ingested_track.mid"
            data = source.getvalue()
        elif isinstance(source, bytes):
            fname = filename or "ingested_track.mid"
            data = source
        else:
            raise TypeError(f"Unsupported source type for MIDI ingestion: {type(source)}")

        # 2. Check if Zip Archive
        is_zip = False
        try:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                is_zip = True
                midi_files_inside = [n for n in zf.namelist() if n.lower().endswith(('.mid', '.midi'))]
        except zipfile.BadZipFile:
            is_zip = False

        if is_zip:
            out_filename = fname if fname.lower().endswith(".zip") else f"{fname}.zip"
            dest_path = os.path.join(target_dir, out_filename)
            with open(dest_path, "wb") as f:
                f.write(data)

            # Invalidate any old open midi library pickle cache
            cache_file = os.path.join(self.midi_dir, "index_cache.pkl")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except OSError:
                    pass

            return {
                "status": "success",
                "type": "midi_zip_archive",
                "filename": out_filename,
                "file_path": dest_path,
                "file_size_bytes": len(data),
                "midi_files_count": len(midi_files_inside),
                "contained_samples": midi_files_inside[:10],
                "metadata": metadata or {}
            }

        # 3. Single MIDI file validation via mido
        try:
            mid = mido.MidiFile(file=io.BytesIO(data))
        except Exception as e:
            raise ValueError(f"Corrupt or invalid Standard MIDI File (SMF): {e}") from e

        tracks_count = len(mid.tracks)
        note_events = 0
        tempos: List[float] = []
        pitches: List[int] = []

        for track in mid.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity > 0:
                    note_events += 1
                    pitches.append(msg.note)
                elif msg.type == "set_tempo":
                    tempos.append(mido.tempo2bpm(msg.tempo))

        bpm_estimate = round(tempos[0], 2) if tempos else 120.0
        pitch_class_counts: Dict[int, int] = {}
        for p in pitches:
            pc = p % 12
            pitch_class_counts[pc] = pitch_class_counts.get(pc, 0) + 1

        pitch_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        dominant_pc = max(pitch_class_counts, key=pitch_class_counts.get) if pitch_class_counts else 0
        estimated_root = pitch_names[dominant_pc]

        out_filename = fname if fname.lower().endswith((".mid", ".midi")) else f"{fname}.mid"
        dest_path = os.path.join(target_dir, out_filename)
        with open(dest_path, "wb") as f:
            f.write(data)

        # Notify StudioBrain / refresh
        self.brain.refresh(force=False)

        return {
            "status": "success",
            "type": "midi_file",
            "filename": out_filename,
            "file_path": dest_path,
            "file_size_bytes": len(data),
            "tracks_count": tracks_count,
            "total_note_events": note_events,
            "ticks_per_beat": mid.ticks_per_beat,
            "estimated_bpm": bpm_estimate,
            "estimated_root": estimated_root,
            "metadata": metadata or {}
        }

    # ==========================================================================
    # 2. Harmonic Progression JSON Ingestion
    # ==========================================================================

    def ingest_progression_json(
        self,
        source: Union[str, Dict[str, Any], List[Any]],
        filename: Optional[str] = None,
        schema_validate: bool = True
    ) -> Dict[str, Any]:
        """
        Ingests a new harmonic progression JSON dataset into src/composer/database/.
        Validates harmonic consistency, writes to storage, and hot-reloads StudioBrain
        so new genres and chords become instantly available without restarts.
        """
        # 1. Parse JSON content
        if isinstance(source, str):
            if os.path.exists(source):
                default_fname = os.path.basename(source)
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                try:
                    data = json.loads(source)
                    default_fname = "imported_progressions.json"
                except json.JSONDecodeError as e:
                    raise ValueError(f"String provided is neither a valid file path nor valid JSON: {e}") from e
        elif isinstance(source, (dict, list)):
            data = source
            default_fname = "imported_progressions.json"
        else:
            raise TypeError(f"Unsupported source type for JSON ingestion: {type(source)}")

        # 2. Schema Validation & Normalization
        genres_found = set()
        progressions_count = 0

        if isinstance(data, dict):
            # Check metadata
            meta = data.get("metadata", {})
            if "genre" in meta:
                genres_found.add(meta["genre"].lower())
            if not filename and "database_name" in meta:
                clean_name = re.sub(r"[^\w\-]", "_", meta["database_name"].lower()).strip("_")
                default_fname = f"{clean_name}.json"

            # Check progressions array
            progs = data.get("progressions", [])
            for p in progs:
                if isinstance(p, dict):
                    g = p.get("genre", meta.get("genre", "general")).lower()
                    genres_found.add(g)
                    progressions_count += 1
                    if schema_validate:
                        if "roots" not in p and "chords" not in p and "data" not in p:
                            raise ValueError(f"Progression entry missing 'roots' or 'chords': {p}")

            # Check direct genre map
            for key, val in data.items():
                if key not in ("metadata", "progressions", "melodic_motifs", "bass_grooves"):
                    if isinstance(val, dict):
                        genres_found.add(key.lower())
                        for sec_progs in val.values():
                            if isinstance(sec_progs, list):
                                progressions_count += len(sec_progs)

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    genres_found.add(item.get("genre", "general").lower())
                    progressions_count += 1

        if progressions_count == 0 and not isinstance(data, dict):
            raise ValueError("No valid progressions found in dataset.")

        # 3. Write to src/composer/database/
        target_filename = filename or default_fname
        if not target_filename.endswith(".json"):
            target_filename += ".json"

        dest_path = os.path.join(self.database_dir, target_filename)
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # 4. Trigger Live StudioBrain Hot-Reload
        self.brain.refresh(force=True)

        return {
            "status": "success",
            "type": "progression_database_json",
            "filename": target_filename,
            "file_path": dest_path,
            "genres_indexed": sorted(list(genres_found)),
            "progressions_count": progressions_count,
            "live_studio_brain_genres_count": len(self.brain.harmonic_catalog)
        }

    # ==========================================================================
    # 3. Leadsheet / MusicXML Ingestion
    # ==========================================================================

    def ingest_leadsheet_musicxml(
        self,
        source: Union[str, bytes, io.BytesIO],
        filename: Optional[str] = None,
        genre: str = "jazz_standard",
        section: str = "chorus",
        save_progression_json: bool = True
    ) -> Dict[str, Any]:
        """
        Ingests a standard MusicXML (.xml, .musicxml) or compressed (.mxl) leadsheet.
        Parses measures, extracts key/meter, extracts <harmony> chord progressions and <note> melodies,
        saves to storage/samples/leadsheets/, and converts to StudioBrain progression format.
        """
        # 1. Read data bytes
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"MusicXML leadsheet not found: {source}")
            fname = filename or os.path.basename(source)
            with open(source, "rb") as f:
                data = f.read()
        elif isinstance(source, io.BytesIO):
            fname = filename or "leadsheet.musicxml"
            data = source.getvalue()
        elif isinstance(source, bytes):
            fname = filename or "leadsheet.musicxml"
            data = source
        else:
            raise TypeError(f"Unsupported source type for MusicXML: {type(source)}")

        # 2. Check for compressed MXL zip
        xml_content = None
        try:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                # Find root XML file
                for name in zf.namelist():
                    if name.endswith(".xml") and not name.startswith("META-INF"):
                        xml_content = zf.read(name)
                        break
        except zipfile.BadZipFile:
            pass

        if xml_content is None:
            xml_content = data

        # 3. Parse XML DOM
        try:
            root_elem = ET.fromstring(xml_content)
        except Exception as e:
            raise ValueError(f"Failed to parse MusicXML: {e}") from e

        # Extract Work Title
        title = fname.rsplit(".", 1)[0].replace("_", " ").title()
        work_title = root_elem.find(".//work-title")
        if work_title is not None and work_title.text:
            title = work_title.text.strip()
        movement_title = root_elem.find(".//movement-title")
        if movement_title is not None and movement_title.text:
            title = movement_title.text.strip()

        # Extract Key and Time Signature
        fifths = 0
        mode = "major"
        key_elem = root_elem.find(".//key")
        if key_elem is not None:
            f_elem = key_elem.find("fifths")
            if f_elem is not None and f_elem.text:
                fifths = int(f_elem.text.strip())
            m_elem = key_elem.find("mode")
            if m_elem is not None and m_elem.text:
                mode = m_elem.text.strip().lower()

        maj_k, min_k = FIFTHS_TO_KEY.get(fifths, ("C", "A"))
        key_name = min_k if mode == "minor" else maj_k

        beats = 4
        beat_type = 4
        time_elem = root_elem.find(".//time")
        if time_elem is not None:
            b_elem = time_elem.find("beats")
            bt_elem = time_elem.find("beat-type")
            if b_elem is not None and b_elem.text:
                beats = int(b_elem.text.strip())
            if bt_elem is not None and bt_elem.text:
                beat_type = int(bt_elem.text.strip())

        # Extract Harmony (Chords)
        chords: List[Dict[str, Any]] = []
        roots: List[str] = []
        types: List[str] = []

        for harmony in root_elem.findall(".//harmony"):
            root_step_elem = harmony.find(".//root-step")
            if root_step_elem is None or not root_step_elem.text:
                continue
            r_step = root_step_elem.text.strip().upper()
            r_alter_elem = harmony.find(".//root-alter")
            if r_alter_elem is not None and r_alter_elem.text:
                alt = int(r_alter_elem.text.strip())
                if alt == 1: r_step += "#"
                elif alt == -1: r_step += "b"

            kind_elem = harmony.find("kind")
            kind_raw = kind_elem.text.strip().lower() if kind_elem is not None and kind_elem.text else "major"
            q_type = MUSICXML_KIND_MAP.get(kind_raw, "maj")

            chord_symbol = f"{r_step}{q_type if q_type != 'maj' else ''}"
            chords.append({
                "chord_symbol": chord_symbol,
                "root": r_step,
                "type": q_type
            })
            roots.append(r_step)
            types.append(q_type)

        # Fallback if no <harmony> elements: derive from note pitches
        notes_parsed = 0
        melody_notes: List[int] = []
        for note in root_elem.findall(".//note"):
            p_elem = note.find("pitch")
            if p_elem is not None:
                step_el = p_elem.find("step")
                oct_el = p_elem.find("octave")
                alt_el = p_elem.find("alter")
                if step_el is not None and oct_el is not None:
                    step = step_el.text.strip().upper()
                    octave = int(oct_el.text.strip())
                    alter = int(alt_el.text.strip()) if alt_el is not None and alt_el.text else 0
                    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}.get(step, 0)
                    midi_num = (octave + 1) * 12 + semitones + alter
                    melody_notes.append(midi_num)
                    notes_parsed += 1

        if not roots and melody_notes:
            # Synthetic 4-chord fallback using melody pitch classes
            pitch_names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
            roots = [pitch_names[melody_notes[i % len(melody_notes)] % 12] for i in range(4)]
            types = ["maj7", "min7", "min7", "dom7"]
            chords = [{"chord_symbol": f"{roots[i]}{types[i]}", "root": roots[i], "type": types[i]} for i in range(4)]

        # 4. Save raw file into storage/samples/leadsheets/
        out_filename = fname if fname.lower().endswith((".xml", ".musicxml", ".mxl")) else f"{fname}.musicxml"
        leadsheet_path = os.path.join(self.leadsheet_dir, out_filename)
        with open(leadsheet_path, "wb") as f:
            f.write(data)

        # 5. Convert to Studio Progression & Hot-Reload StudioBrain
        progression_entry = {
            "id": re.sub(r"[^\w\-]", "_", title.lower()),
            "title": title,
            "name": title,
            "artist": "Leadsheet Archive",
            "section": section,
            "genre": genre.lower().replace("-", "_"),
            "key": key_name,
            "mode": mode,
            "time_signature": f"{beats}/{beat_type}",
            "roots": roots or ["C", "F", "G", "C"],
            "types": types or ["maj", "maj", "maj", "maj"],
            "chords": chords,
            "style_tags": ["leadsheet", "musicxml", genre],
            "description": f"Extracted from MusicXML leadsheet: {title}"
        }

        json_out_path = None
        if save_progression_json and roots:
            safe_genre_name = genre.lower().replace(" ", "_").replace("-", "_")
            json_filename = f"leadsheet_{safe_genre_name}_{progression_entry['id']}.json"
            json_out_path = os.path.join(self.database_dir, json_filename)
            db_payload = {
                "metadata": {
                    "database_name": f"Leadsheet {title}",
                    "genre": genre,
                    "source": out_filename
                },
                "progressions": [progression_entry]
            }
            if melody_notes:
                db_payload["melodic_motifs"] = [{
                    "id": f"{progression_entry['id']}_motif",
                    "title": f"{title} Main Hook",
                    "genre": genre,
                    "notes": [(p - melody_notes[0]) % 12 for p in melody_notes[:8]],
                    "rhythm": [i * 0.5 for i in range(min(8, len(melody_notes)))]
                }]

            with open(json_out_path, "w", encoding="utf-8") as f:
                json.dump(db_payload, f, indent=2)

            self.brain.refresh(force=True)

        return {
            "status": "success",
            "type": "musicxml_leadsheet",
            "title": title,
            "key": key_name,
            "mode": mode,
            "time_signature": f"{beats}/{beat_type}",
            "raw_leadsheet_path": leadsheet_path,
            "progression_json_path": json_out_path,
            "chords_count": len(chords),
            "melody_notes_count": notes_parsed,
            "progression": progression_entry
        }

    # ==========================================================================
    # 4. Markdown Chord Chart Ingestion
    # ==========================================================================

    def ingest_markdown_chords(
        self,
        source: Union[str, os.PathLike],
        filename: Optional[str] = None,
        genre: str = "genre_study"
    ) -> Dict[str, Any]:
        """
        Parses markdown research documents containing chord tables or progression definitions,
        extracts roots/qualities, compiles them into a database JSON, and triggers hot-reload.
        """
        if os.path.exists(source):
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
            base_name = os.path.basename(source).rsplit(".", 1)[0]
        else:
            content = str(source)
            base_name = filename or "markdown_progressions"

        # Regex to find chord rows: e.g. | Section | Roots | Chords | Roman Numerals |
        progressions = []
        lines = content.split("\n")
        current_section = "chorus"

        for line in lines:
            line_str = line.strip()
            # Check for section header
            if line_str.startswith("#"):
                clean_header = line_str.lstrip("#").strip().lower()
                if "verse" in clean_header: current_section = "verse"
                elif "chorus" in clean_header: current_section = "chorus"
                elif "intro" in clean_header: current_section = "intro"
                elif "breakdown" in clean_header: current_section = "breakdown"
                elif "climax" in clean_header: current_section = "climax"

            # Parse lines with chord lists e.g. "Dm - Bb - F - C" or "roots: [D, Bb, F, C]"
            chord_matches = re.findall(r"\b([A-G][b#]?(?:maj7|min7|min9|maj9|dom7|sus2|sus4|min|maj|dim|aug|m7|M7|m9|M9|m6|maj6|min6|m11|m13|m|6|7|9|11|13)?)\b", line_str)
            if len(chord_matches) >= 3 and not line_str.startswith("#"):
                roots = []
                types = []
                for c in chord_matches[:8]:
                    root = c[0]
                    if len(c) > 1 and c[1] in ("#", "b"):
                        root += c[1]
                        qual = c[2:]
                    else:
                        qual = c[1:]
                    roots.append(root)
                    types.append("min" if qual.startswith("m") and not qual.startswith("maj") else ("maj7" if "maj7" in qual else ("min7" if "min7" in qual else "maj")))

                progressions.append({
                    "name": f"Markdown Progression {len(progressions) + 1}",
                    "genre": genre,
                    "section": current_section,
                    "roots": roots,
                    "types": types,
                    "roman_numerals": " - ".join(chord_matches[:8])
                })

        if not progressions:
            raise ValueError("No chord progressions could be parsed from the markdown source.")

        db_payload = {
            "metadata": {
                "database_name": f"Extracted from {base_name}",
                "genre": genre
            },
            "progressions": progressions
        }

        out_fname = f"{base_name}_extracted.json"
        return self.ingest_progression_json(db_payload, filename=out_fname)

    # ==========================================================================
    # 5. Global Inventory & Cleaners
    # ==========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status of all ingestion targets and StudioBrain index."""
        midi_files = glob.glob(os.path.join(self.midi_dir, "*.mid*")) + glob.glob(os.path.join(self.midi_dir, "*.zip"))
        db_files = glob.glob(os.path.join(self.database_dir, "*.json"))
        leadsheet_files = glob.glob(os.path.join(self.leadsheet_dir, "*"))

        brain_stats = self.brain.summary()

        return {
            "midi_library_directory": self.midi_dir,
            "midi_assets_count": len(midi_files),
            "database_directory": self.database_dir,
            "database_files_count": len(db_files),
            "database_files": [os.path.basename(f) for f in db_files],
            "leadsheet_directory": self.leadsheet_dir,
            "leadsheet_files_count": len(leadsheet_files),
            "studio_brain_summary": brain_stats
        }

    def clean_test_artifacts(self, pattern: str = "test_*") -> int:
        """Safely removes temporary testing files from database, midi, and leadsheets."""
        removed = 0
        for directory in [self.database_dir, self.midi_dir, self.leadsheet_dir]:
            for f in glob.glob(os.path.join(directory, pattern)):
                try:
                    os.remove(f)
                    removed += 1
                except OSError:
                    pass
        self.brain.refresh(force=True)
        return removed


def get_ingest_hub() -> IngestionHub:
    """Convenience factory returning the singleton IngestionHub instance."""
    return IngestionHub.get_instance()


if __name__ == "__main__":
    hub = IngestionHub()
    status = hub.get_status()
    print("=" * 70)
    print("INGESTION HUB INVENTORY & STATUS")
    print("=" * 70)
    print(f"MIDI Directory:      {status['midi_library_directory']} ({status['midi_assets_count']} items)")
    print(f"Database Directory:  {status['database_directory']} ({status['database_files_count']} JSON files)")
    print(f"Leadsheet Directory: {status['leadsheet_directory']} ({status['leadsheet_files_count']} leadsheets)")
    print(f"StudioBrain Genres:  {status['studio_brain_summary']['genres_count']} active genres")
    print(f"StudioBrain Progs:   {status['studio_brain_summary']['total_indexed_progressions']} progressions")
    print("=" * 70)

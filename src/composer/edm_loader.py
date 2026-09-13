"""
src/composer/edm_loader.py - Accessor & Query Engine for Top 100 EDM Artists Billboard Database
Provides instantaneous in-memory indexing and structured access to 100 premier electronic artists,
including harmonic progressions with Drop-2/4 voicings, melodic hook seeds with pickups,
30% gate staccato bass grooves, timbral profiles, and macro-arrangement archetypes.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "edm_top100_database.json")


NOTE_OFFSETS = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}


def note_str_to_midi(note_str: str, default_octave: int = 4) -> int:
    """Converts a note string like 'G#5', 'C#4', 'Bb3' into a MIDI pitch number."""
    note_str = note_str.strip()
    if not note_str:
        return 60
    if note_str[-1].isdigit():
        octave = int(note_str[-1])
        pitch_name = note_str[:-1]
    else:
        octave = default_octave
        pitch_name = note_str
    offset = NOTE_OFFSETS.get(pitch_name, 0)
    return offset + (octave + 1) * 12


def parse_chord_symbol(chord: str) -> Tuple[str, str, str]:
    """Parses chord symbol (e.g. 'C#m', 'A', 'Bbmaj7', 'A/C#') into (root, type, bass_note)."""
    chord = chord.strip()
    bass_note = None
    if "/" in chord:
        parts = chord.split("/")
        chord = parts[0].strip()
        bass_note = parts[1].strip()

    if len(chord) >= 2 and chord[1] in ("#", "b"):
        root = chord[:2]
        suffix = chord[2:]
    else:
        root = chord[:1]
        suffix = chord[1:]

    if not bass_note:
        bass_note = root

    suffix_lower = suffix.lower()
    if suffix_lower in ("m7", "min7"):
        ctype = "min7"
    elif suffix_lower in ("maj7", "m7+"):
        ctype = "maj7"
    elif suffix_lower in ("7", "dom7"):
        ctype = "dom7"
    elif suffix_lower in ("m9", "min9"):
        ctype = "min9"
    elif suffix_lower in ("maj9",):
        ctype = "maj9"
    elif suffix_lower in ("sus4",):
        ctype = "sus4"
    elif suffix_lower in ("sus2",):
        ctype = "sus2"
    elif suffix_lower in ("dim", "dim7"):
        ctype = "dim"
    elif suffix_lower in ("m", "min", "-"):
        ctype = "min"
    else:
        ctype = "maj"

    return root, ctype, bass_note


def extract_roots_and_types_from_chords(raw_chords: list, key: str = "") -> Tuple[List[str], List[str], List[str], List[List[int]]]:
    """Extracts roots, types, bass notes, and Drop-2 voicings from strings or dict chord structures."""
    roots = []
    types = []
    bass_notes = []
    drop2_voicings = []
    for c in raw_chords:
        if isinstance(c, str):
            r, t, b = parse_chord_symbol(c)
            roots.append(r)
            types.append(t)
            bass_notes.append(b)
        elif isinstance(c, dict):
            if "drop2_voicing" in c:
                drop2_voicings.append(c["drop2_voicing"])
            r = c.get("root")
            rn = c.get("roman_numeral", "")
            if not r:
                key_l = key.lower()
                rn_map = {
                    "i": "Bb" if "bb" in key_l else ("F#" if "f#" in key_l else "D"),
                    "vi": "Bb" if "bb" in key_l else ("B" if "d" in key_l else "G"),
                    "iv": "Eb" if "bb" in key_l else ("B" if "f#" in key_l else "G"),
                    "IV": "Gb" if "bb" in key_l else ("G" if "d" in key_l else "F"),
                    "I": "Db" if "db" in key_l or "bb" in key_l else ("D" if "d" in key_l else "C"),
                    "V": "Ab" if "bb" in key_l else ("A" if "d" in key_l else "G"),
                    "VII": "Db" if "bb" in key_l else ("C" if "d" in key_l else "F"),
                    "v": "F" if "bb" in key_l else ("C#" if "f#" in key_l else "A"),
                    "VI": "Gb" if "bb" in key_l else ("D" if "f#" in key_l else "Bb"),
                    "III": "Db" if "bb" in key_l else ("A" if "f#" in key_l else "F")
                }
                r = rn_map.get(rn, "Bb" if "bb" in key_l else "D")
            roots.append(r)
            t = c.get("type")
            if not t:
                t = "min" if rn.islower() else "maj"
            types.append(t)
            bass_notes.append(c.get("bass", r))

    if not roots:
        roots = ["Bb", "Gb", "Db", "Ab"] if "bb" in key.lower() else ["D", "Bb", "F", "C"]
        types = ["min", "maj", "maj", "maj"]
        bass_notes = list(roots)

    return roots, types, bass_notes, drop2_voicings


class EDMLoader:
    """Fast-indexing in-memory reader and query engine for Top 100 EDM Artists Billboard Database."""

    _instance: Optional[EDMLoader] = None

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.data: Dict[str, Any] = {}
        self.artists: List[Dict[str, Any]] = []
        self.progressions: List[Dict[str, Any]] = []
        self.melodic_motifs: List[Dict[str, Any]] = []
        self.bass_grooves: List[Dict[str, Any]] = []

        self._artist_index: Dict[str, Dict[str, Any]] = {}
        self._progression_index: Dict[str, List[Dict[str, Any]]] = {}
        self._discipline_index: Dict[str, List[Dict[str, Any]]] = {}

        self.load_database()

    @classmethod
    def get_instance(cls, db_path: str = DB_PATH) -> EDMLoader:
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def load_database(self) -> None:
        """Loads and indexes the JSON database in memory."""
        if not os.path.exists(self.db_path):
            logger.warning(f"EDM Top 100 database not found at {self.db_path}")
            return

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            self.artists = self.data.get("artists", [])
            self.progressions = self.data.get("progressions", [])
            self.melodic_motifs = self.data.get("melodic_motifs", [])
            self.bass_grooves = self.data.get("bass_grooves", [])

            # Build fast lookup indexes
            for a in self.artists:
                name_key = a.get("name", "").lower().strip()
                self._artist_index[name_key] = a

                disc = a.get("discipline", "").lower().strip()
                if disc not in self._discipline_index:
                    self._discipline_index[disc] = []
                self._discipline_index[disc].append(a)

            for p in self.progressions:
                p_artist = p.get("artist", "").lower().strip()
                if p_artist not in self._progression_index:
                    self._progression_index[p_artist] = []
                self._progression_index[p_artist].append(p)

            logger.info(f"Successfully loaded {len(self.artists)} EDM artists and {len(self.progressions)} progressions.")
        except Exception as e:
            logger.error(f"Error loading EDM database from {self.db_path}: {e}")

    def get_all_artists(self) -> List[str]:
        """Returns the full list of all 100 artist names."""
        return [a.get("name", "") for a in self.artists]

    def get_artist(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Finds an artist by name with case-insensitive and fuzzy matching."""
        q = artist_name.lower().strip()
        if q in self._artist_index:
            return self._artist_index[q]

        for k, v in self._artist_index.items():
            if q in k or k in q:
                return v
        return None

    def get_progression(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns the primary harmonic progression for a given artist with parsed roots, types, and voicings."""
        # 1. Check artist entry directly first for rich primary_tracks data
        art = self.get_artist(artist_name)
        if art:
            if art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
                pt = art["primary_tracks"][0]
                if "progression" in pt:
                    prog = pt["progression"]
                    raw_chords = prog.get("chords", [])
                    roots, types, bass_notes, parsed_drop2 = extract_roots_and_types_from_chords(raw_chords, key=pt.get("key", ""))

                    # Extract Drop-2 and Drop-4 voicings if present
                    voicings_data = prog.get("voicings", {})
                    drop2_voicings = parsed_drop2
                    drop4_voicings = []
                    if isinstance(voicings_data, dict):
                        if "drop2_midi" in voicings_data and not drop2_voicings:
                            drop2_voicings = [
                                item["notes"] if isinstance(item, dict) else item
                                for item in voicings_data["drop2_midi"]
                            ]
                        if "drop4_midi" in voicings_data:
                            drop4_voicings = [
                                item["notes"] if isinstance(item, dict) else item
                                for item in voicings_data["drop4_midi"]
                            ]

                    return {
                        "artist": art.get("name", ""),
                        "title": pt.get("title", ""),
                        "key": pt.get("key", ""),
                        "mode": pt.get("mode", ""),
                        "roman_numerals": " - ".join(prog.get("roman_numerals", [])) if isinstance(prog.get("roman_numerals"), list) else prog.get("roman_numerals", ""),
                        "chords": raw_chords,
                        "roots": roots,
                        "types": types,
                        "bass_notes": bass_notes,
                        "voicings": voicings_data,
                        "drop2_voicings": drop2_voicings,
                        "drop4_voicings": drop4_voicings,
                        "bpm": pt.get("tempo_bpm", 128)
                    }

            if "harmonic_progression" in art and art["harmonic_progression"]:
                hp = art["harmonic_progression"]
                raw_chords = hp.get("chords", [])
                roots, types, bass_notes, drop2_voicings = extract_roots_and_types_from_chords(raw_chords, key=hp.get("key", ""))
                pt = art.get("primary_tracks", [""])[0]
                title = pt.get("title", "") if isinstance(pt, dict) else str(pt)
                return {
                    "artist": art.get("name", ""),
                    "title": title,
                    "key": hp.get("key", ""),
                    "roman_numerals": hp.get("roman_numerals", ""),
                    "chords": raw_chords,
                    "roots": roots,
                    "types": types,
                    "bass_notes": bass_notes,
                    "drop2_voicings": drop2_voicings,
                    "bpm": hp.get("bpm", 128)
                }

        # 2. Check top-level progressions index
        q = artist_name.lower().strip()
        found_prog = None
        if q in self._progression_index and self._progression_index[q]:
            found_prog = dict(self._progression_index[q][0])
        else:
            for k, v in self._progression_index.items():
                if (q in k or k in q) and v:
                    found_prog = dict(v[0])
                    break

        if found_prog:
            chords_list = found_prog.get("chords", [])
            roots, types, bass_notes, drop2_voicings = extract_roots_and_types_from_chords(chords_list, key=found_prog.get("key", ""))
            found_prog["drop2_voicings"] = drop2_voicings or found_prog.get("drop2_voicings", [])
            found_prog["roots"] = roots or found_prog.get("roots", ["Bb", "Gb", "Db", "Ab"])
            found_prog["types"] = types or found_prog.get("types", ["min", "maj", "maj", "maj"])
            found_prog["bass_notes"] = bass_notes or found_prog.get("bass_notes", found_prog["roots"])
            return found_prog

        return None

    def get_progressions_by_discipline(self, discipline_query: str) -> List[Dict[str, Any]]:
        """Returns all progressions belonging to a discipline (e.g. 'progressive', 'techno', 'french', 'bass', 'trance')."""
        q = discipline_query.lower().strip()
        results = []
        for p in self.progressions:
            disc = p.get("discipline", "").lower()
            if q in disc:
                results.append(p)
        return results

    def get_melodic_hook(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns the signature melodic hook and pickup timing for an artist."""
        art = self.get_artist(artist_name)
        if art:
            if art.get("topline_melody") and len(art["topline_melody"]) > 0:
                return dict(art["topline_melody"])
            if art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
                pt = art["primary_tracks"][0]
                if pt.get("topline_hook") and len(pt["topline_hook"]) > 0:
                    hook = dict(pt["topline_hook"])
                    hook["artist"] = art.get("name", "")
                    hook["title"] = pt.get("title", "")
                    hook["key"] = pt.get("key", "")
                    if "resolution_path" in hook and isinstance(hook["resolution_path"], list):
                        hook["notes_midi"] = [note_str_to_midi(n) for n in hook["resolution_path"]]
                        hook["notes"] = hook["notes_midi"]
                    if "climax_midi" not in hook and hook.get("climax_note"):
                        hook["climax_midi"] = note_str_to_midi(hook["climax_note"])
                    if "rhythm" not in hook:
                        hook["rhythm"] = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
                    return hook

        q = artist_name.lower().strip()
        for m in self.melodic_motifs:
            if q in m.get("artist", "").lower():
                return dict(m)
        return None

    def get_bass_groove(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns the signature bass pocket physics and gate settings for an artist."""
        art = self.get_artist(artist_name)
        if art:
            if art.get("bass_groove") and len(art["bass_groove"]) > 0:
                return dict(art["bass_groove"])
            if art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
                pt = art["primary_tracks"][0]
                if pt.get("bass_groove") and len(pt["bass_groove"]) > 0:
                    bg = dict(pt["bass_groove"])
                    bg["artist"] = art.get("name", "")
                    bg["title"] = pt.get("title", "")
                    gate_pct = bg.get("gate_length_percent", 42.0) / 100.0
                    tiers = bg.get("velocity_tiers", {})
                    accent = tiers.get("accent", 124)
                    groove = tiers.get("groove", 90)
                    ghost = tiers.get("ghost", 72)
                    bg["steps"] = [
                        (0, gate_pct, accent),
                        (1, max(0.20, gate_pct * 0.75), ghost),
                        (2, gate_pct, groove),
                        (3, max(0.20, gate_pct * 0.75), ghost),
                        (4, gate_pct, accent),
                        (5, max(0.20, gate_pct * 0.75), ghost),
                        (6, gate_pct, groove),
                        (7, max(0.20, gate_pct * 0.75), ghost),
                        (8, gate_pct, accent),
                        (9, max(0.20, gate_pct * 0.75), ghost),
                        (10, gate_pct, groove),
                        (11, max(0.20, gate_pct * 0.75), ghost),
                        (12, gate_pct, accent),
                        (13, max(0.20, gate_pct * 0.75), ghost),
                        (14, gate_pct, groove),
                        (15, max(0.20, gate_pct * 0.75), ghost),
                    ]
                    return bg

        q = artist_name.lower().strip()
        for bg in self.bass_grooves:
            if q in bg.get("artist", "").lower():
                return dict(bg)
        return None

    def get_timbral_profile(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns synthesizer topology, filter cutoffs, and saturation profiles for an artist."""
        art = self.get_artist(artist_name)
        if art and "timbral_profile" in art and len(art["timbral_profile"]) > 0:
            return art["timbral_profile"]
        if art and art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
            return art["primary_tracks"][0].get("timbre")
        return None

    def get_macro_structure(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns arrangement archetype and zero-drop breakdown specifications for an artist."""
        art = self.get_artist(artist_name)
        if art and "macro_structure" in art and len(art["macro_structure"]) > 0:
            return art["macro_structure"]
        if art and art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
            return art["primary_tracks"][0].get("structural_arc")
        return None


def get_edm_loader() -> EDMLoader:
    """Returns the singleton EDMLoader instance."""
    return EDMLoader.get_instance()


if __name__ == "__main__":
    loader = get_edm_loader()
    print(f"EDM Loader Initialized with {len(loader.artists)} artists.")
    print("Artists list (sample 10):", loader.get_all_artists()[:10])

    for test_artist in ["Avicii", "deadmau5", "Daft Punk", "Skrillex", "Armin van Buuren"]:
        prog = loader.get_progression(test_artist)
        art = loader.get_artist(test_artist)
        print(f"\n[{test_artist}]")
        print(f"  Discipline: {art.get('discipline') if art else 'N/A'}")
        print(f"  Hit Track: {art.get('primary_tracks', ['N/A'])[0] if art else 'N/A'}")
        print(f"  Progression: {prog.get('roman_numerals') if prog else 'N/A'}")
        print(f"  Key: {prog.get('key') if prog else 'N/A'}")

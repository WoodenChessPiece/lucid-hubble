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
        """Returns the primary harmonic progression for a given artist."""
        q = artist_name.lower().strip()
        if q in self._progression_index and self._progression_index[q]:
            return self._progression_index[q][0]

        for k, v in self._progression_index.items():
            if (q in k or k in q) and v:
                return v[0]

        # Check artist entry directly
        art = self.get_artist(artist_name)
        if art:
            if art.get("primary_tracks") and isinstance(art["primary_tracks"][0], dict):
                pt = art["primary_tracks"][0]
                if "progression" in pt:
                    prog = pt["progression"]
                    return {
                        "artist": art.get("name", ""),
                        "title": pt.get("title", ""),
                        "key": pt.get("key", ""),
                        "mode": pt.get("mode", ""),
                        "roman_numerals": " - ".join(prog.get("roman_numerals", [])) if isinstance(prog.get("roman_numerals"), list) else prog.get("roman_numerals", ""),
                        "chords": prog.get("chords", []),
                        "voicings": prog.get("voicings", {}),
                        "bpm": pt.get("tempo_bpm", 128)
                    }

            if "harmonic_progression" in art and art["harmonic_progression"]:
                hp = art["harmonic_progression"]
                return {
                    "artist": art.get("name", ""),
                    "key": hp.get("key", ""),
                    "roman_numerals": hp.get("roman_numerals", ""),
                    "chords": hp.get("chords", []),
                    "bpm": hp.get("bpm", 128)
                }
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
        if art and "topline_melody" in art:
            return art["topline_melody"]

        q = artist_name.lower().strip()
        for m in self.melodic_motifs:
            if q in m.get("artist", "").lower():
                return m
        return None

    def get_bass_groove(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns the signature bass pocket physics and gate settings for an artist."""
        art = self.get_artist(artist_name)
        if art and "bass_groove" in art:
            return art["bass_groove"]

        q = artist_name.lower().strip()
        for bg in self.bass_grooves:
            if q in bg.get("artist", "").lower():
                return bg
        return None

    def get_timbral_profile(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns synthesizer topology, filter cutoffs, and saturation profiles for an artist."""
        art = self.get_artist(artist_name)
        if art and "timbral_profile" in art:
            return art["timbral_profile"]
        return None

    def get_macro_structure(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Returns arrangement archetype and zero-drop breakdown specifications for an artist."""
        art = self.get_artist(artist_name)
        if art and "macro_structure" in art:
            return art["macro_structure"]
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

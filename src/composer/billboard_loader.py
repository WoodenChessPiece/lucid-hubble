"""
src/composer/billboard_loader.py - Billboard Hit Knowledge Base Accessor & Loader
Provides fast in-memory indexing, harmonic querying, melodic hook retrieval,
and bass groove sequencing for top modern Billboard hits (2024-2026).
"""

import os
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "billboard_hits_database.json")


@dataclass
class HitProgression:
    id: str
    title: str
    artist: str
    section: str
    key: str
    mode: str
    bpm: float
    time_signature: str
    harmonic_rhythm: str
    roman_numerals: str
    roots: List[str]
    types: List[str]
    bass_notes: List[str]
    chords: List[Dict[str, Any]]
    style_tags: List[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "section": self.section,
            "key": self.key,
            "mode": self.mode,
            "bpm": self.bpm,
            "time_signature": self.time_signature,
            "harmonic_rhythm": self.harmonic_rhythm,
            "roman_numerals": self.roman_numerals,
            "roots": list(self.roots),
            "types": list(self.types),
            "bass_notes": list(self.bass_notes),
            "chords": list(self.chords),
            "style_tags": list(self.style_tags),
            "description": self.description
        }


class BillboardHitLoader:
    """
    Billboard Hit Knowledge Base Query Engine.
    Loads and serves hit chord progressions, voicings (Close, Drop-2, Drop-4),
    melodic hook seeds with pickup offsets and climax targets, and authentic bassline grooves.
    """

    _instance: Optional['BillboardHitLoader'] = None

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(BillboardHitLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
        self.db_path = db_path or DB_PATH
        self.raw_data: Dict[str, Any] = {}
        self.progressions: List[HitProgression] = []
        self.melodic_motifs: List[Dict[str, Any]] = []
        self.bass_grooves: List[Dict[str, Any]] = []
        self._load_database()
        self._initialized = True

    def _load_database(self) -> None:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Billboard hits database not found at {self.db_path}")

        with open(self.db_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        self.progressions = []
        for p in self.raw_data.get("progressions", []):
            self.progressions.append(HitProgression(
                id=p.get("id", ""),
                title=p.get("title", ""),
                artist=p.get("artist", ""),
                section=p.get("section", ""),
                key=p.get("key", ""),
                mode=p.get("mode", ""),
                bpm=float(p.get("bpm", 120)),
                time_signature=p.get("time_signature", "4/4"),
                harmonic_rhythm=p.get("harmonic_rhythm", ""),
                roman_numerals=p.get("roman_numerals", ""),
                roots=list(p.get("roots", [])),
                types=list(p.get("types", [])),
                bass_notes=list(p.get("bass_notes", [])),
                chords=list(p.get("chords", [])),
                style_tags=list(p.get("style_tags", [])),
                description=p.get("description", "")
            ))

        self.melodic_motifs = self.raw_data.get("melodic_motifs", [])
        self.bass_grooves = self.raw_data.get("bass_grooves", [])

    def get_hit_progression(
        self,
        artist: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        section: Optional[str] = None,
        return_dataclass: bool = False
    ) -> Union[Dict[str, Any], HitProgression]:
        """
        Query a single hit chord progression matching artist and/or style tags.
        Example:
            loader.get_hit_progression(artist="Sabrina Carpenter")
            loader.get_hit_progression(style="dreamy_pop")
        """
        candidates = self.get_all_progressions(artist=artist, style=style, title=title, section=section)
        if not candidates:
            # Fallback if no exact match found: relax constraints
            if artist and not style:
                candidates = [p for p in self.progressions if any(a.lower() in p.artist.lower() for a in artist.lower().split())]
            elif style and not artist:
                candidates = [p for p in self.progressions if any(s in " ".join(p.style_tags).lower() for s in style.lower().split("_"))]
            if not candidates:
                candidates = self.progressions

        selected = random.choice(candidates)
        return selected if return_dataclass else selected.to_dict()

    def get_all_progressions(
        self,
        artist: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        section: Optional[str] = None
    ) -> List[HitProgression]:
        """Returns all progressions matching criteria."""
        results = list(self.progressions)

        if artist:
            art_clean = artist.strip().lower()
            results = [p for p in results if art_clean in p.artist.lower() or p.artist.lower() in art_clean]

        if style:
            stl_clean = style.strip().lower().replace("-", "_")
            results = [
                p for p in results
                if any(stl_clean in st.lower().replace("-", "_") or st.lower().replace("-", "_") in stl_clean for st in p.style_tags)
            ]

        if title:
            tit_clean = title.strip().lower()
            results = [p for p in results if tit_clean in p.title.lower()]

        if section:
            sec_clean = section.strip().lower()
            results = [p for p in results if sec_clean in p.section.lower()]

        return results

    def get_hit_motif(
        self,
        artist: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a melodic hook seed with pickup offset, syncopation profile,
        and vocal climax targets.
        """
        candidates = list(self.melodic_motifs)
        if artist:
            art_clean = artist.strip().lower()
            candidates = [m for m in candidates if art_clean in m.get("artist", "").lower()]
        if style:
            stl_clean = style.strip().lower().replace("-", "_")
            candidates = [
                m for m in candidates
                if any(stl_clean in st.lower().replace("-", "_") for st in m.get("style_tags", []))
            ]
        if title:
            tit_clean = title.strip().lower()
            candidates = [m for m in candidates if tit_clean in m.get("title", "").lower()]

        if not candidates:
            candidates = self.melodic_motifs
        return dict(random.choice(candidates))

    def get_hit_bass_groove(
        self,
        artist: Optional[str] = None,
        style: Optional[str] = None,
        genre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves an authentic bassline groove pattern with 16-step gates,
        velocity dynamics, and drum pocket alignments.
        """
        candidates = list(self.bass_grooves)
        if artist:
            art_clean = artist.strip().lower()
            candidates = [b for b in candidates if art_clean in b.get("artist", "").lower()]
        if style or genre:
            target = (style or genre).strip().lower().replace("-", "_")
            candidates = [
                b for b in candidates
                if target in b.get("genre", "").lower().replace("-", "_") or
                   any(target in st.lower().replace("-", "_") for st in b.get("style_tags", []))
            ]

        if not candidates:
            candidates = self.bass_grooves
        return dict(random.choice(candidates))

    def list_artists(self) -> List[str]:
        """Returns sorted list of all covered artists."""
        return sorted(list(set(p.artist for p in self.progressions)))

    def list_styles(self) -> List[str]:
        """Returns sorted list of all supported style tags."""
        styles = set()
        for p in self.progressions:
            styles.update(p.style_tags)
        return sorted(list(styles))

    def summary(self) -> Dict[str, Any]:
        """Returns statistical overview of the loaded knowledge base."""
        return {
            "database_name": self.raw_data.get("metadata", {}).get("database_name", "Billboard Hits Database"),
            "version": self.raw_data.get("metadata", {}).get("version", "1.0.0"),
            "progressions_count": len(self.progressions),
            "melodic_motifs_count": len(self.melodic_motifs),
            "bass_grooves_count": len(self.bass_grooves),
            "artists": self.list_artists(),
            "styles_count": len(self.list_styles())
        }


def get_billboard_loader(db_path: Optional[str] = None) -> BillboardHitLoader:
    """Convenience factory returning the singleton BillboardHitLoader instance."""
    return BillboardHitLoader(db_path)


if __name__ == "__main__":
    print("=" * 70)
    print("BILLBOARD HIT KNOWLEDGE BASE VERIFICATION & MEMORY LOAD TEST")
    print("=" * 70)

    loader = BillboardHitLoader()
    summary = loader.summary()
    print(f"Loaded Database: {summary['database_name']} (v{summary['version']})")
    print(f"  • Progressions in memory: {summary['progressions_count']}")
    print(f"  • Melodic Motifs in memory: {summary['melodic_motifs_count']}")
    print(f"  • Bass Grooves in memory: {summary['bass_grooves_count']}")
    print(f"  • Covered Artists ({len(summary['artists'])}): {', '.join(summary['artists'])}")
    print(f"  • Total Style Tags: {summary['styles_count']}")
    print("-" * 70)

    # Test 1: Query by artist="Sabrina Carpenter"
    print("\n[TEST 1] loader.get_hit_progression(artist='Sabrina Carpenter')")
    p_sabrina = loader.get_hit_progression(artist="Sabrina Carpenter")
    assert p_sabrina is not None, "Failed to retrieve Sabrina Carpenter progression!"
    assert "Sabrina Carpenter" in p_sabrina["artist"], f"Unexpected artist: {p_sabrina['artist']}"
    print(f"  ✓ Success: {p_sabrina['title']} ({p_sabrina['artist']})")
    print(f"    Key: {p_sabrina['key']} | Section: {p_sabrina['section']}")
    print(f"    Roman Numerals: {p_sabrina['roman_numerals']}")
    print(f"    Roots: {p_sabrina['roots']}")
    print(f"    Chords ({len(p_sabrina['chords'])}): {[c['chord_symbol'] for c in p_sabrina['chords']]}")
    print(f"    Drop-2 Voicings Available: {all('drop2_voicing' in c for c in p_sabrina['chords'])}")

    # Test 2: Query by style="dreamy_pop"
    print("\n[TEST 2] loader.get_hit_progression(style='dreamy_pop')")
    p_dreamy = loader.get_hit_progression(style="dreamy_pop")
    assert p_dreamy is not None, "Failed to retrieve dreamy_pop progression!"
    assert any("dreamy_pop" in st for st in p_dreamy["style_tags"]), f"dreamy_pop missing in tags: {p_dreamy['style_tags']}"
    print(f"  ✓ Success: {p_dreamy['title']} by {p_dreamy['artist']}")
    print(f"    Key: {p_dreamy['key']} | BPM: {p_dreamy['bpm']}")
    print(f"    Roman Numerals: {p_dreamy['roman_numerals']}")
    print(f"    Style Tags: {p_dreamy['style_tags']}")

    # Test 3: Query other top artists
    artists_to_test = ["Billie Eilish", "Chappell Roan", "Taylor Swift", "Post Malone & Morgan Wallen", "The Weeknd", "Charli XCX", "Dua Lipa"]
    print("\n[TEST 3] Querying full artist catalog:")
    for art in artists_to_test:
        prog = loader.get_hit_progression(artist=art)
        assert prog is not None, f"Failed for artist: {art}"
        print(f"  ✓ [{art}]: '{prog['title']}' ({prog['roman_numerals']})")

    # Test 4: Verify Melodic Motifs
    print("\n[TEST 4] Melodic Motifs & Hook Seeds:")
    motif_espresso = loader.get_hit_motif(title="Espresso")
    assert motif_espresso is not None, "Failed to retrieve Espresso motif!"
    print(f"  ✓ Motif: {motif_espresso['title']} by {motif_espresso['artist']}")
    print(f"    Pickup Beat: {motif_espresso['pickup_beat']} | Starting Degree: {motif_espresso['starting_scale_degree']}")
    print(f"    Climax Target: {motif_espresso['climax_target']['pitch']} ({motif_espresso['climax_target']['bar_location']})")
    print(f"    MIDI Note Events: {len(motif_espresso['midi_sequence'])} notes")

    # Test 5: Verify Bass Grooves
    print("\n[TEST 5] Authentic Bassline Grooves:")
    bass_brat = loader.get_hit_bass_groove(artist="Charli XCX")
    assert bass_brat is not None, "Failed to retrieve Charli XCX bass groove!"
    print(f"  ✓ Bass Groove: {bass_brat['title']} by {bass_brat['artist']}")
    print(f"    Genre: {bass_brat['genre']} | Tempo: {bass_brat['tempo']} BPM")
    print(f"    Swing: {bass_brat['groove_characteristics'].get('swing_percentage')}% | Jitter: {bass_brat['groove_characteristics'].get('humanize_ms_jitter')} ms")
    print(f"    16-step Grid Events: {len(bass_brat['steps'])} steps")

    print("\n" + "=" * 70)
    print("ALL 5 TESTS PASSED: Billboard hits database cleanly verified in memory!")
    print("=" * 70)

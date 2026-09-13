"""
src/composer/knowledge_base.py - High-Performance Musical Knowledge Base & StudioBrain
Loads masterclass research papers, Billboard hit progressions, and dynamically discovers
and indexes all harmonic databases in src/composer/database/.
Provides live dynamic absorption of new datasets on the fly without requiring code edits or restarts.
"""

import os
import glob
import json
import random
import time
from typing import List, Dict, Any, Optional, Union

DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_FILE = os.path.join(DB_DIR, "music_knowledge_base.json")


class StudioBrain:
    """
    Central Musical Intelligence & Knowledge Graph Engine for Lucid Hubble.
    Provides live indexing, dynamic absorption of harmonic progression databases,
    melodic motifs, and authentic bassline grooves.
    Automatically checks and reloads databases when new files are ingested into database/.
    """

    _instance: Optional['StudioBrain'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StudioBrain, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_dir: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
        self.db_dir = db_dir or DB_DIR
        self.loaded_file_stats: Dict[str, float] = {}  # filepath -> mtime
        self.harmonic_catalog: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.motif_library: List[Dict[str, Any]] = []
        self.bass_patterns: Dict[str, Dict[str, Any]] = []
        self.all_progressions: List[Dict[str, Any]] = []
        self.loaded_databases: Dict[str, Dict[str, Any]] = {}
        self.db: Dict[str, Any] = {}

        self._load_all_databases()
        self._initialized = True

    def _load_database(self) -> None:
        """Backward-compatible alias for _load_all_databases."""
        self._load_all_databases()

    @classmethod
    def get_instance(cls, db_dir: Optional[str] = None) -> 'StudioBrain':
        """Convenience accessor for singleton StudioBrain."""
        if cls._instance is None:
            cls._instance = cls(db_dir)
        return cls._instance

    def _init_fallback_catalogs(self) -> None:
        """Initializes built-in masterclass harmonic progressions, motifs, and grooves."""
        self.harmonic_catalog = {
            "synthwave": {
                "verse": [
                    {"name": "Nightcall Driving Minor", "roots": ["D", "Bb", "F", "C"], "types": ["min", "maj", "maj", "dom7"]},
                    {"name": "Pacific Coast Subdominant", "roots": ["D", "A", "Bb", "G"], "types": ["min", "min", "maj", "min"]},
                    {"name": "Suspended Nostalgia", "roots": ["D", "G", "A", "D"], "types": ["sus2", "sus4", "sus2", "min7"]}
                ],
                "chorus": [
                    {"name": "The Epic Outrun Anthem", "roots": ["Bb", "C", "D", "F"], "types": ["maj7", "dom7", "min7", "maj7"]},
                    {"name": "Sunset Heroic Resolution", "roots": ["Bb", "F", "C", "D"], "types": ["maj9", "maj", "dom7", "min9"]},
                    {"name": "Phrygian Menace Crunch", "roots": ["D", "Eb", "Bb", "A"], "types": ["min", "maj", "maj", "dom7"]}
                ],
                "breakdown": [
                    {"name": "Dorian Floating Suspension", "roots": ["D", "G", "C", "A"], "types": ["min9", "maj7", "sus2", "min7"]},
                    {"name": "Minor iv Nostalgic Weep", "roots": ["F", "Bb", "Bb", "F"], "types": ["maj7", "min", "maj7", "maj"]}
                ]
            },
            "darksynth": {
                "verse": [
                    {"name": "Turbo Killer bII Crunch", "roots": ["D", "Eb", "D", "C"], "types": ["min", "maj", "min", "min"]},
                    {"name": "Roller Mobster Tension", "roots": ["D", "Eb", "G", "A"], "types": ["min", "maj", "min", "dim"]}
                ],
                "chorus": [
                    {"name": "Apocalyptic Staccato Charge", "roots": ["D", "Bb", "F", "A"], "types": ["min", "maj", "maj", "dom7"]},
                    {"name": "Cyberpunk Heavy Ascent", "roots": ["D", "F", "G", "Bb"], "types": ["min", "maj", "min", "maj"]}
                ],
                "breakdown": [
                    {"name": "Haunted Cathedral Drone", "roots": ["D", "D", "Eb", "D"], "types": ["min", "sus2", "maj", "min"]}
                ]
            },
            "lofi": {
                "verse": [
                    {"name": "Dilla Offset ii-V-I-vi", "roots": ["D", "G", "C", "A"], "types": ["min9", "dom7", "maj9", "min9"]},
                    {"name": "Nujabes Nostalgic Drift", "roots": ["F", "E", "D", "G"], "types": ["maj7", "min7", "min9", "dom7"]}
                ],
                "chorus": [
                    {"name": "Lush Soul Golden Ratio", "roots": ["C", "F", "E", "A"], "types": ["maj9", "min7", "min7", "min9"]}
                ],
                "breakdown": [
                    {"name": "Rhodes Cloud Walk", "roots": ["D", "C", "Bb", "A"], "types": ["min9", "maj7", "maj7", "dom7"]}
                ]
            }
        }

        self.motif_library = [
            {"id": "anthem_hook_1", "notes": [0, 3, 5, 7, 10, 7, 5, 3], "rhythm": [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]},
            {"id": "soaring_5th_leap", "notes": [0, 7, 8, 7, 5, 3, 2, 0], "rhythm": [0.5, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]},
            {"id": "syncopated_pluck", "notes": [12, 10, 7, 5, 7, 10, 12, 15], "rhythm": [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]},
            {"id": "kavinsky_minimal", "notes": [7, 8, 7, 5, 7, 8, 10, 7], "rhythm": [0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]}
        ]

        self.bass_patterns = {
            "carpenter_brut_staccato": {
                "steps": [
                    (0, 0.35, 115), (1, 0.30, 85), (2, 0.35, 95), (3, 0.25, 70),
                    (4, 0.35, 110), (5, 0.30, 80), (6, 0.35, 100), (7, 0.0, 0),
                    (8, 0.35, 120), (9, 0.30, 85), (10, 0.35, 95), (11, 0.25, 70),
                    (12, 0.35, 110), (13, 0.30, 80), (14, 0.35, 100), (15, 0.85, 110)
                ]
            },
            "italo_rolling_octave": {
                "steps": [
                    (0, 0.75, 90), (1, 0.60, 110), (2, 0.75, 95), (3, 0.60, 115),
                    (4, 0.75, 90), (5, 0.60, 110), (6, 0.75, 95), (7, 0.60, 115),
                    (8, 0.75, 90), (9, 0.60, 110), (10, 0.75, 95), (11, 0.60, 115),
                    (12, 0.75, 90), (13, 0.60, 110), (14, 0.75, 95), (15, 0.60, 120)
                ]
            }
        }
        self.all_progressions = []

    def _normalize_section(self, section: str) -> str:
        s = section.lower().strip().replace("-", "_").replace(" ", "_")
        if "verse" in s:
            return "verse"
        if "chorus" in s or "drop" in s or "hook" in s:
            return "chorus"
        if "breakdown" in s or "bridge" in s:
            return "breakdown"
        if "build" in s or "pre" in s:
            return "buildup"
        if "climax" in s or "solo" in s:
            return "climax"
        if "intro" in s:
            return "intro"
        if "outro" in s:
            return "outro"
        return s or "chorus"

    def _index_progression_item(self, item: Dict[str, Any], default_genre: str = "general") -> None:
        """Indexes a single progression into harmonic_catalog and all_progressions."""
        genre = str(item.get("genre", default_genre)).lower().strip().replace("-", "_").replace(" ", "_")
        section = self._normalize_section(str(item.get("section", "chorus")))

        roots = item.get("roots", [])
        types = item.get("types", [])

        # Infer roots and types from chords if missing
        if (not roots or not types) and "chords" in item:
            extracted_roots = []
            extracted_types = []
            for c in item["chords"]:
                if isinstance(c, dict):
                    extracted_roots.append(c.get("root", "C"))
                    extracted_types.append(c.get("type", "maj"))
                elif isinstance(c, str):
                    extracted_roots.append(c[0])
                    extracted_types.append("maj" if "m" not in c else "min")
            if not roots:
                roots = extracted_roots
            if not types:
                types = extracted_types

        # Ensure roots and types are valid lists
        if not roots:
            roots = ["C", "G", "A", "F"]
        if not types:
            types = ["maj", "maj", "min", "maj"]

        name = item.get("name") or item.get("title") or item.get("id") or "Untitled Progression"
        entry = dict(item)
        entry["name"] = name
        entry["title"] = name
        entry["genre"] = genre
        entry["section"] = section
        entry["roots"] = roots
        entry["types"] = types

        if genre not in self.harmonic_catalog:
            self.harmonic_catalog[genre] = {}
        if section not in self.harmonic_catalog[genre]:
            self.harmonic_catalog[genre][section] = []

        self.harmonic_catalog[genre][section].append(entry)
        self.all_progressions.append(entry)

        # Also register under any style_tags
        for tag in item.get("style_tags", []):
            norm_tag = str(tag).lower().strip().replace("-", "_")
            if norm_tag and norm_tag != genre:
                if norm_tag not in self.harmonic_catalog:
                    self.harmonic_catalog[norm_tag] = {}
                if section not in self.harmonic_catalog[norm_tag]:
                    self.harmonic_catalog[norm_tag][section] = []
                self.harmonic_catalog[norm_tag][section].append(entry)

    def _absorb_json_content(self, data: Union[Dict[str, Any], List[Any]], source_name: str) -> None:
        """Parses any JSON data structure into StudioBrain's indices."""
        prog_count = 0
        motif_count = 0
        groove_count = 0

        # Case 1: Standard dictionary with "progressions" array
        if isinstance(data, dict):
            metadata = data.get("metadata", {})
            default_genre = metadata.get("genre", "general")

            # Ingest Progressions
            if "progressions" in data and isinstance(data["progressions"], list):
                for p in data["progressions"]:
                    if isinstance(p, dict):
                        # Handle music_knowledge_base.json style: {"source": ..., "data": {"genre": ..., "chord_dictionary": ...}}
                        if "data" in p and isinstance(p["data"], dict) and "chord_dictionary" in p["data"]:
                            sub_genre = p["data"].get("genre", default_genre)
                            cdict = p["data"]["chord_dictionary"]
                            roots = [k[0] for k in list(cdict.keys())[:4]]
                            types = [v.get("type", "maj") if isinstance(v, dict) else "maj" for v in list(cdict.values())[:4]]
                            synthetic_entry = {
                                "name": f"{sub_genre} Progression",
                                "genre": sub_genre,
                                "section": "chorus",
                                "roots": roots or ["C", "F", "G", "Am"],
                                "types": types or ["maj", "maj", "maj", "min"],
                                "source": p.get("source", source_name)
                            }
                            self._index_progression_item(synthetic_entry, default_genre=sub_genre)
                            prog_count += 1
                        else:
                            self._index_progression_item(p, default_genre=default_genre)
                            prog_count += 1

            # Ingest Melodic Motifs
            if "melodic_motifs" in data and isinstance(data["melodic_motifs"], list):
                for m in data["melodic_motifs"]:
                    if isinstance(m, dict):
                        m_entry = dict(m)
                        if "notes" not in m_entry or "rhythm" not in m_entry:
                            if "midi_sequence" in m_entry and m_entry["midi_sequence"]:
                                seq = m_entry["midi_sequence"]
                                root_midi = seq[0].get("midi", 60)
                                m_entry["notes"] = [(ev.get("midi", 60) - root_midi) % 12 for ev in seq]
                                m_entry["rhythm"] = [float(ev.get("start_beat", idx * 0.5)) for idx, ev in enumerate(seq)]
                            elif "intervals" in m_entry and m_entry["intervals"]:
                                m_entry["notes"] = list(m_entry["intervals"])
                                m_entry["rhythm"] = [i * 0.5 for i in range(len(m_entry["notes"]))]
                            else:
                                m_entry["notes"] = [0, 3, 5, 7, 10, 7, 5, 3]
                                m_entry["rhythm"] = [0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
                        self.motif_library.append(m_entry)
                        motif_count += 1

            # Ingest Bass Grooves / Bass Patterns
            if "bass_grooves" in data and isinstance(data["bass_grooves"], list):
                for b in data["bass_grooves"]:
                    if isinstance(b, dict):
                        b_entry = dict(b)
                        style_id = b_entry.get("style", b_entry.get("id", f"groove_{len(self.bass_patterns)}"))
                        if "steps" in b_entry and isinstance(b_entry["steps"], list):
                            normalized_steps = []
                            for idx, s in enumerate(b_entry["steps"]):
                                if isinstance(s, (list, tuple)) and len(s) >= 3:
                                    normalized_steps.append((s[0], s[1], s[2]))
                                elif isinstance(s, dict):
                                    step_num = s.get("step", idx) - 1 if s.get("step", idx) >= 1 else idx
                                    gate = s.get("gate_ratio", s.get("gate_length", 0.5))
                                    vel = s.get("velocity", 100)
                                    normalized_steps.append((step_num, gate, vel))
                            b_entry["steps"] = normalized_steps
                        self.bass_patterns[style_id] = b_entry
                        groove_count += 1

            # Case 2: Direct genre mapping dict e.g. {"synthwave": {"verse": [...], "chorus": [...]}}
            for key, val in data.items():
                if key in ("metadata", "progressions", "melodic_motifs", "bass_grooves"):
                    continue
                if isinstance(val, dict):
                    for sec_name, prog_list in val.items():
                        if isinstance(prog_list, list):
                            for p in prog_list:
                                if isinstance(p, dict):
                                    item = dict(p)
                                    item["genre"] = key
                                    item["section"] = sec_name
                                    self._index_progression_item(item, default_genre=key)
                                    prog_count += 1

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._index_progression_item(item)
                    prog_count += 1

        self.loaded_databases[source_name] = {
            "source": source_name,
            "progressions_added": prog_count,
            "motifs_added": motif_count,
            "grooves_added": groove_count,
            "loaded_at": time.time()
        }

    def _check_freshness(self) -> bool:
        """
        Scans self.db_dir for new or modified JSON files.
        Returns True if changes were detected and loaded.
        """
        if not os.path.exists(self.db_dir):
            return False

        json_files = glob.glob(os.path.join(self.db_dir, "*.json"))
        current_stats = {}
        for f in json_files:
            try:
                current_stats[f] = os.path.getmtime(f)
            except OSError:
                pass

        # Check if files were added, modified, or removed
        if current_stats != self.loaded_file_stats:
            self._load_all_databases()
            return True
        return False

    def _load_all_databases(self) -> None:
        """Discovers and parses all JSON files in the database directory."""
        self._init_fallback_catalogs()
        self.loaded_file_stats = {}
        self.loaded_databases = {}

        if not os.path.exists(self.db_dir):
            return

        json_files = sorted(glob.glob(os.path.join(self.db_dir, "*.json")))
        for fpath in json_files:
            try:
                mtime = os.path.getmtime(fpath)
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                fname = os.path.basename(fpath)
                self._absorb_json_content(data, fname)
                self.loaded_file_stats[fpath] = mtime
                if fname == "music_knowledge_base.json":
                    self.db = data
            except Exception as e:
                print(f"[StudioBrain] Warning: Failed to load {fpath}: {e}")

    def refresh(self, force: bool = False) -> bool:
        """Forces or checks for database updates on the fly."""
        if force:
            self._load_all_databases()
            return True
        return self._check_freshness()

    def absorb_dataset(self, data_or_path: Union[str, Dict[str, Any], List[Any]], name: Optional[str] = None) -> Dict[str, Any]:
        """
        Dynamically absorbs an in-memory or on-disk dataset into StudioBrain's live index
        without requiring application restart.
        """
        if isinstance(data_or_path, str):
            if os.path.exists(data_or_path):
                source_name = name or os.path.basename(data_or_path)
                with open(data_or_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.loaded_file_stats[data_or_path] = os.path.getmtime(data_or_path)
            else:
                try:
                    data = json.loads(data_or_path)
                    source_name = name or "inline_json"
                except Exception as e:
                    raise ValueError(f"Cannot parse string as JSON or find file: {data_or_path}") from e
        else:
            data = data_or_path
            source_name = name or f"in_memory_dataset_{len(self.loaded_databases)}"

        self._absorb_json_content(data, source_name)
        return self.loaded_databases.get(source_name, {})

    def get_progression(
        self,
        genre: str = "synthwave",
        section: str = "chorus",
        mood: Optional[str] = None,
        style: Optional[str] = None,
        artist: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dynamic harmonic progression query engine.
        Supports fuzzy matching on genre, section, mood, style, and artist.
        Always verifies freshness to hot-absorb any newly dropped database files.
        """
        self._check_freshness()

        target_genre = genre.lower().strip().replace("-", "_").replace(" ", "_")
        target_sec = self._normalize_section(section)

        # 1. Direct query in harmonic catalog
        genre_data = self.harmonic_catalog.get(target_genre)

        # If not found directly, try style or artist match in all_progressions
        if not genre_data:
            matched = [
                p for p in self.all_progressions
                if (target_genre in p.get("genre", "").lower())
                or (style and any(style.lower() in str(st).lower() for st in p.get("style_tags", [])))
                or (artist and artist.lower() in p.get("artist", "").lower())
            ]
            if matched:
                sec_matched = [p for p in matched if self._normalize_section(p.get("section", "")) == target_sec]
                chosen = random.choice(sec_matched if sec_matched else matched)
                return chosen

            # Fallback to synthwave
            genre_data = self.harmonic_catalog.get("synthwave", list(self.harmonic_catalog.values())[0])

        section_list = genre_data.get(target_sec)
        if not section_list:
            # Fallback to chorus or any available section
            section_list = genre_data.get("chorus")
            if not section_list:
                for sec_candidates in genre_data.values():
                    if sec_candidates:
                        section_list = sec_candidates
                        break

        if not section_list:
            section_list = self.harmonic_catalog.get("synthwave", {}).get("chorus", [
                {"name": "Fallback Major", "roots": ["C", "G", "Am", "F"], "types": ["maj", "maj", "min", "maj"]}
            ])

        # Mood filtering if requested
        if mood:
            mood_lower = mood.lower()
            mood_candidates = [
                p for p in section_list
                if any(mood_lower in str(ep).lower() for ep in p.get("emotional_profile", []))
                or mood_lower in p.get("name", "").lower()
            ]
            if mood_candidates:
                return random.choice(mood_candidates)

        return random.choice(section_list)

    def get_motif(
        self,
        genre: Optional[str] = None,
        artist: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieves a melodic hook or thematic motif."""
        self._check_freshness()
        candidates = list(self.motif_library)

        if genre:
            g_clean = genre.lower().replace("-", "_")
            c = [m for m in candidates if g_clean in m.get("genre", "").lower()]
            if c: candidates = c
        if artist:
            a_clean = artist.lower()
            c = [m for m in candidates if a_clean in m.get("artist", "").lower()]
            if c: candidates = c
        if style:
            s_clean = style.lower().replace("-", "_")
            c = [m for m in candidates if any(s_clean in st.lower() for st in m.get("style_tags", []))]
            if c: candidates = c
        if title:
            t_clean = title.lower()
            c = [m for m in candidates if t_clean in m.get("title", "").lower() or t_clean in m.get("name", "").lower()]
            if c: candidates = c

        return random.choice(candidates if candidates else self.motif_library)

    def get_bass_pattern(
        self,
        style: str = "carpenter_brut_staccato",
        genre: Optional[str] = None,
        artist: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieves a bassline groove pattern."""
        self._check_freshness()

        if style in self.bass_patterns:
            return self.bass_patterns[style]

        candidates = list(self.bass_patterns.values())
        if genre:
            g_clean = genre.lower().replace("-", "_")
            c = [b for b in candidates if g_clean in b.get("genre", "").lower()]
            if c: return random.choice(c)
        if artist:
            a_clean = artist.lower()
            c = [b for b in candidates if a_clean in b.get("artist", "").lower()]
            if c: return random.choice(c)

        return self.bass_patterns.get("carpenter_brut_staccato", list(self.bass_patterns.values())[0])

    def list_genres(self) -> List[str]:
        """Returns all recognized musical genres across loaded databases."""
        self._check_freshness()
        return sorted(list(self.harmonic_catalog.keys()))

    def list_databases(self) -> List[Dict[str, Any]]:
        """Returns summary of all loaded databases."""
        self._check_freshness()
        return list(self.loaded_databases.values())

    def summary(self) -> Dict[str, Any]:
        """Returns statistics of StudioBrain's current live knowledge state."""
        self._check_freshness()
        total_progs = sum(
            len(progs) for sec in self.harmonic_catalog.values() for progs in sec.values()
        )
        return {
            "genres_count": len(self.harmonic_catalog),
            "genres": self.list_genres(),
            "databases_count": len(self.loaded_databases),
            "total_indexed_progressions": total_progs,
            "motifs_count": len(self.motif_library),
            "bass_patterns_count": len(self.bass_patterns),
            "databases": [db["source"] for db in self.loaded_databases.values()]
        }


# ==============================================================================
# Backward Compatibility: MusicKnowledgeBase alias & singleton provider
# ==============================================================================

class MusicKnowledgeBase(StudioBrain):
    """
    Subclass of StudioBrain to provide seamless 100% backward compatibility
    with existing callers in arranger.py, tests, and scripts.
    """
    pass


def get_studio_brain(db_dir: Optional[str] = None) -> StudioBrain:
    """Convenience factory returning the singleton StudioBrain instance."""
    return StudioBrain.get_instance(db_dir)


def get_knowledge_base(db_dir: Optional[str] = None) -> MusicKnowledgeBase:
    """Convenience factory returning the singleton MusicKnowledgeBase instance."""
    return MusicKnowledgeBase.get_instance(db_dir)


if __name__ == "__main__":
    print("=" * 70)
    print("STUDIO BRAIN VERIFICATION & DYNAMIC DATABASE TEST")
    print("=" * 70)
    brain = StudioBrain()
    stats = brain.summary()
    print(f"[*] StudioBrain initialized with {stats['genres_count']} genres across {stats['databases_count']} databases.")
    print(f"[*] Total indexed progressions: {stats['total_indexed_progressions']}")
    print(f"[*] Motifs: {stats['motifs_count']} | Bass patterns: {stats['bass_patterns_count']}")
    print(f"[*] Genres: {', '.join(stats['genres'][:10])}...")
    
    # Test queries
    prog = brain.get_progression("synthwave", "chorus")
    print(f"\n[Test Query - synthwave chorus]: {prog['name']} -> Roots: {prog['roots']}")
    assert prog is not None and "roots" in prog
    print("[SUCCESS] StudioBrain baseline verification passed.")

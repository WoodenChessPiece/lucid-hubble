"""
src/composer/album.py - 1-Hour Long-Form Album Generator
Composes a continuous multi-track suite of 14-16 tracks with varied keys, moods, and drop structures.
"""

from dataclasses import dataclass
from src.composer.arranger import create_arrangement, Arrangement

TRACK_TITLES = [
    "Neon Sunrise",
    "Digital Highway",
    "Cyber Mirage",
    "Midnight Transmission",
    "Retro Matrix",
    "Chrome Heartbeat",
    "Synthetic Skyline",
    "Tokyo Drift Protocol",
    "Zero Gravity",
    "Night Drive 2088",
    "Suborbital Glow",
    "Quantum Circuit",
    "Electric Rain",
    "Vapor Afterglow",
    "Solaris Horizon",
]

KEY_MODES = [
    "D Minor",
    "A Minor",
    "G Minor",
    "C Minor",
    "F Minor",
    "Bb Minor",
    "E Minor",
    "D Minor",
    "A Minor",
    "G Minor",
    "C Minor",
    "F Minor",
    "Bb Minor",
    "E Minor",
    "D Minor"
]

@dataclass
class TrackMeta:
    index: int
    title: str
    key: str
    bpm: float
    bars: int
    start_seconds: float
    duration_seconds: float
    arrangement: Arrangement

@dataclass
class Album:
    title: str
    genre: str
    total_duration_seconds: float
    tracks: list[TrackMeta]

def create_1hour_album(
    album_title: str = "NEON_NIGHT_DRIVE",
    genre: str = "synthwave",
    base_bpm: float = 118.0,
    target_duration_minutes: float = 60.0
) -> Album:
    tracks: list[TrackMeta] = []
    current_time = 0.0

    # Calculate bars per track so 14-15 tracks total ~60 minutes (~4 mins per track)
    # At 118 BPM, 4 beats = 2.03s per bar. 118 bars = ~4 mins.
    bars_per_track = 116 # ~3.93 minutes per track
    crossfade_overlap = 3.0 # 3 second crossfade between tracks

    target_seconds = target_duration_minutes * 60.0

    track_idx = 0
    while current_time < target_seconds and track_idx < len(TRACK_TITLES):
        title = TRACK_TITLES[track_idx]
        key = KEY_MODES[track_idx % len(KEY_MODES)]
        # Subtle tempo drift between tracks (+/- 2 BPM)
        bpm = base_bpm + ((track_idx % 3) - 1) * 1.5

        arr = create_arrangement(
            genre=genre,
            bpm=bpm,
            bars=bars_per_track,
            swing_ratio=0.52 if genre == "synthwave" else 0.62
        )

        track_dur = arr.total_duration

        t_meta = TrackMeta(
            index=track_idx + 1,
            title=title,
            key=key,
            bpm=bpm,
            bars=bars_per_track,
            start_seconds=current_time,
            duration_seconds=track_dur,
            arrangement=arr
        )
        tracks.append(t_meta)

        # Increment current time minus crossfade overlap
        current_time += (track_dur - crossfade_overlap)
        track_idx += 1

    total_dur = current_time + crossfade_overlap
    return Album(title=album_title, genre=genre, total_duration_seconds=total_dur, tracks=tracks)

def format_chapters(album: Album) -> list[tuple[str, str]]:
    chapters = []
    for t in album.tracks:
        mins = int(t.start_seconds // 60)
        secs = int(t.start_seconds % 60)
        timestamp = f"{mins:02d}:{secs:02d}"
        chapter_label = f"{t.index}. {t.title} [{t.key}]"
        chapters.append((timestamp, chapter_label))
    return chapters

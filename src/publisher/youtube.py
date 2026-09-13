"""
src/publisher/youtube.py - YouTube Metadata Generator & Publishing Automation
"""

def generate_youtube_metadata(
    track_title: str,
    genre: str,
    bpm: int,
    key: str,
    duration_sec: float
) -> dict:
    chapters = [
        ("00:00", "Intro & Atmospheric Build"),
        ("00:08", "Drop: Rolling Darksynth Bass"),
        ("00:16", "Cyberpunk Arpeggio & Lead Melodies"),
        ("00:24", "Full Intensity Climax"),
        (f"00:{int(duration_sec - 4):02d}", "Outro & Reverb Tail")
    ]

    chapter_text = "\n".join([f"{ts} - {name}" for ts, name in chapters])

    description = f"""⚡ {track_title.upper()} // {genre.upper()}
100% Autonomous Headless Production.

🎧 TRACK SPECS:
- Tempo: {bpm} BPM
- Musical Key: {key}
- Mastering: EBU R128 Integrated -14.0 LUFS (-1.5 dBTP Ceiling)
- Audio Engine: Python Sound Synthesis & FFmpeg Visualizer

⏱️ CHAPTERS:
{chapter_text}

✨ Perfect for coding, night drives, gaming, and deep focus flow.
All audio stems and master outputs stored directly on Google Drive.

#synthwave #cyberpunk #darksynth #codingmusic #retrowave #studymusic
"""

    tags = [
        "dark synthwave", "cyberpunk music", "synthwave beats",
        "retrowave", "gaming music", "coding soundtrack",
        "study music", "118 bpm", "d minor", "ai music", "royalty free synthwave"
    ]

    title = f"{track_title.upper()} // {genre.title()} [1080p 60fps] ⚡ Focus Flow"

    return {
        "title": title[:100],
        "description": description,
        "tags": tags,
        "categoryId": "10", # 10 = Music
        "privacyStatus": "unlisted"
    }

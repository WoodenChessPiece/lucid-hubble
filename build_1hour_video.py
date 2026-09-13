"""
build_1hour_video.py - 1-Hour Long-Form YouTube Music Video & Publisher Orchestrator
Renders complete 60+ minute continuous music videos with chapters, thumbnails, and automated YouTube publishing.
All output deliverables are saved directly to Google Drive via storage/ symlink.
"""

import argparse
import json
import os
import time
import subprocess
from src.composer.album import create_1hour_album, format_chapters
from src.engine.stitcher import render_and_stitch_album
from src.visualizer.video import generate_background_graphic, render_video_with_visualizer
from src.visualizer.thumbnail import create_youtube_thumbnail
from src.publisher.youtube_uploader import upload_video_to_youtube

def build_1hour_video(
    album_title: str = "NEON_NIGHT_DRIVE_1HOUR",
    genre: str = "synthwave",
    bpm: float = 118.0,
    duration_minutes: float = 60.0,
    upload: bool = False
):
    print("=" * 65)
    print(f"🎬 1-HOUR LONG-FORM AUTONOMOUS VIDEO STUDIO")
    print(f"🎵 Album: {album_title} | Genre: {genre.upper()} | Target: {duration_minutes:.1f} Mins")
    print(f"☁️ Cloud Storage: Google Drive (storage/ -> My Drive/HeadlessMusicStudio)")
    print(f"⚡ Hardware Video Encoder: Apple Silicon VideoToolbox (h264_videotoolbox)")
    print("=" * 65)

    start_time = time.time()

    # Paths (all stored in Google Drive)
    wav_path = f"storage/renders/{album_title}_master.wav"
    mp3_path = f"storage/renders/{album_title}_master.mp3"
    bg_path = f"storage/renders/{album_title}_bg.png"
    thumb_path = f"storage/videos/{album_title}_thumb.png"
    mp4_path = f"storage/videos/{album_title}.mp4"
    meta_path = f"storage/videos/{album_title}_youtube.json"

    # Step 1: Compose Album
    print(f"\n[1/5] Composing multi-track continuous album (~{duration_minutes:.0f} mins)...")
    album = create_1hour_album(
        album_title=album_title,
        genre=genre,
        base_bpm=bpm,
        target_duration_minutes=duration_minutes
    )
    chapters = format_chapters(album)
    print(f"  ✓ Composed {len(album.tracks)} distinct tracks. Total duration: {album.total_duration_seconds / 60.0:.1f} minutes.")

    # Step 2: Render & Stitch Audio
    print(f"\n[2/5] Synthesizing, crossfading, and mastering album directly to disk...")
    render_and_stitch_album(album, wav_path, crossfade_seconds=3.0)

    # Encode MP3 master
    print(f"  -> Compressing 320kbps MP3 streaming master...")
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-b:a", "320k", mp3_path], capture_output=True, check=True)
    print(f"  ✓ Exported MP3: {mp3_path}")

    # Step 3: Visual Backdrop & Thumbnail
    print(f"\n[3/5] Generating procedural art & High-CTR 1-Hour YouTube thumbnail...")
    display_title = album_title.replace("_", " ")
    generate_background_graphic(
        title=display_title,
        subtitle=f"1 HOUR {genre.upper()} RETRO MIX",
        bpm=int(bpm),
        key="VARIOUS (15 TRACKS)",
        output_png=bg_path
    )
    create_youtube_thumbnail(
        bg_image_path=bg_path,
        main_title=display_title,
        subtitle=f"1 HOUR {genre.upper()} CODING FLOW",
        badge_text=f"1 HOUR MIX // 1080P",
        output_path=thumb_path
    )

    # Step 4: Render Long-Form Video with Hardware Acceleration
    print(f"\n[4/5] Rendering 1-hour 1080p MP4 via Apple Silicon Hardware Encoder...")
    render_video_with_visualizer(
        bg_image_path=bg_path,
        audio_wav_path=wav_path,
        output_mp4_path=mp4_path,
        use_hardware_accel=True
    )

    # Step 5: Format Scrubber Chapters & YouTube Metadata
    print(f"\n[5/5] Building YouTube description with clickable scrubber chapters...")
    chapter_text = "\n".join([f"{ts} - {title}" for ts, title in chapters])

    description = f"""⚡ {display_title} [1 HOUR CONTINUOUS {genre.upper()} MIX]
100% Autonomous Headless Production.

🎧 ALBUM SPECS:
- Total Runtime: {album.total_duration_seconds / 60.0:.1f} Minutes
- Total Tracks: {len(album.tracks)} Unique Compositions
- Mastering: EBU R128 YouTube Integrated -14.0 LUFS (-1.5 dBTP True Peak)
- Audio Engine: Python Analog DSP Modeling & Apple Silicon Video Engine
- Storage: High-Resolution Google Drive Cloud Archive

⏱️ TRACKLIST & CHAPTERS:
{chapter_text}

✨ Perfect for programming, gaming, late-night driving, studying, and deep focus flow.
Leave a like, subscribe, and share for more continuous 1-hour focus albums!

#synthwave #1hourmix #darksynth #codingmusic #retrowave #focusmusic #studymusic
"""

    tags = [
        "1 hour synthwave", "synthwave mix", "dark synthwave",
        "coding music 1 hour", "study beats", "retrowave",
        "cyberpunk 1 hour", "gaming music", "1 hour focus music",
        "electronic music mix", "royalty free synthwave"
    ]

    metadata = {
        "title": f"{display_title} // 1 HOUR Continuous Mix [1080p 60fps] ⚡ Focus Flow"[:100],
        "description": description,
        "tags": tags,
        "categoryId": "10",
        "privacyStatus": "unlisted"
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Saved YouTube metadata: {meta_path}")

    # Optional YouTube Upload
    if upload:
        print(f"\n[YouTube Publisher] Initiating automated YouTube upload...")
        upload_video_to_youtube(
            video_file_path=mp4_path,
            thumbnail_file_path=thumb_path,
            metadata=metadata,
            interactive_auth=False
        )

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"🎉 1-HOUR VIDEO PRODUCTION COMPLETE IN {elapsed / 60.0:.1f} MINUTES ({elapsed:.1f}s)!")
    print(f"📦 Master WAV:  {wav_path}")
    print(f"📦 Master MP3:  {mp3_path}")
    print(f"🎬 Full Video:  {mp4_path}")
    print(f"🖼️ Thumbnail:   {thumb_path}")
    print(f"📄 Chapters:    {meta_path}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1-Hour Long-Form YouTube Video Generator")
    parser.add_argument("--title", default="NEON_NIGHT_DRIVE_1HOUR", help="Album/Video title")
    parser.add_argument("--genre", default="synthwave", choices=["synthwave", "lofi", "ambient", "neoclassical"], help="Genre")
    parser.add_argument("--bpm", type=float, default=118.0, help="Base BPM")
    parser.add_argument("--duration_mins", type=float, default=60.0, help="Target duration in minutes")
    parser.add_argument("--upload", action="store_true", help="Upload directly to YouTube upon completion")

    args = parser.parse_args()
    build_1hour_video(
        album_title=args.title,
        genre=args.genre,
        bpm=args.bpm,
        duration_minutes=args.duration_mins,
        upload=args.upload
    )

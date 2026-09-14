"""
pipeline.py - Master Headless Studio Orchestrator
Executes composition, synthesis, mastering, video generation, and YouTube packaging.
All output deliverables are stored directly into Google Drive via storage/ symlink.
"""

import argparse
import json
import os
import time
import subprocess
from src.composer.arranger import create_arrangement
from src.engine.synth import MultiTrackEngine
from src.mastering.chain import YouTubeMasteringChain
from src.visualizer.video import generate_background_graphic, render_video_with_visualizer
from src.visualizer.thumbnail import create_youtube_thumbnail
from src.publisher.youtube import generate_youtube_metadata

def run_pipeline(
    title: str = "Neon_Horizon",
    genre: str = "synthwave",
    bpm: float = 118.0,
    bars: int = 16,
    key_name: str = "D Minor",
    engine: str = "neural",
    model_name: str = "facebook/musicgen-stereo-large"
):
    print("=" * 60)
    print(f"🚀 LAUNCHING AUTONOMOUS HEADLESS MUSIC & VIDEO FACTORY")
    print(f"🎵 Title: {title} | Genre: {genre.upper()} | BPM: {bpm} | Key: {key_name}")
    print(f"🧠 Engine: {engine.upper()} ({model_name} on {'RunPod Cloud GPU' if os.getenv('RUNPOD_API_KEY') else 'Local Apple Silicon M3 MPS' if engine == 'neural' else 'SoundFont GM'})")
    print(f"☁️ Storage: Google Drive (storage/ -> My Drive/HeadlessMusicStudio)")
    print("=" * 60)

    start_time = time.time()

    # Paths (all stored in Google Drive)
    wav_path = f"storage/renders/{title}_master.wav"
    mp3_path = f"storage/renders/{title}_master.mp3"
    bg_path = f"storage/renders/{title}_bg.png"
    thumb_path = f"storage/videos/{title}_thumb.png"
    mp4_path = f"storage/videos/{title}.mp4"
    meta_path = f"storage/videos/{title}_youtube.json"

    # Step 1: Composition
    print("\n[1/6] Composing arrangement with Parsimonious Voice Leading & Drop-2 Voicings...")
    arr = create_arrangement(genre=genre, bpm=bpm, bars=bars)
    print(f"  ✓ Created {bars} bars ({arr.total_duration:.1f}s) across 6 tracks (kick, snare, hats, bass, pads, lead).")

    # Step 2: Synthesis
    if engine == "neural":
        model_name = getattr(args, "model", "facebook/musicgen-stereo-large")
        print(f"\n[2/6] Generative Neural Synthesis via Meta MusicGen ({model_name} on {'RunPod Cloud GPU' if os.getenv('RUNPOD_API_KEY') else 'Local Apple Silicon M3 MPS'})...")
        from src.engine.runpod_neural_engine import RunPodNeuralEngine
        neural = RunPodNeuralEngine(backend="auto", model_name=model_name)
        duration = min(20.0, arr.total_duration)
        prompt = f"festival {genre} anthem, driving bassline, euphoric supersaw leads, crisp punchy drums, stadium acoustics, in {key_name}, {int(bpm)} bpm"
        raw_audio = neural.generate_full_track(prompt=prompt, duration_seconds=duration, bpm=bpm, key=key_name, model_name=model_name)
        print(f"  ✓ Neural Audio Generated: {raw_audio.shape[0]} samples ({raw_audio.shape[1] if raw_audio.ndim > 1 else 1} channels) at {neural.target_sr} Hz.")
    else:
        print("\n[2/6] Headlessly synthesizing audio stems & analog modeling...")
        synth_engine = MultiTrackEngine()
        raw_audio = synth_engine.render_arrangement(arr)
        print(f"  ✓ Synthesized {raw_audio.shape[0]} samples with active sidechain compression.")

    # Step 3: Mastering
    print("\n[3/6] Applying YouTube -14.0 LUFS & -1.5 dBTP mastering chain...")
    mastering = YouTubeMasteringChain()
    mastering.master_and_save(raw_audio, wav_path)

    # Convert to MP3
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-b:a", "320k", mp3_path], capture_output=True, check=True)
    print(f"  ✓ Exported MP3 master: {mp3_path}")

    # Step 4: Background Art & Thumbnail
    print("\n[4/6] Generating procedural visual backdrop & High-CTR YouTube thumbnail...")
    generate_background_graphic(
        title=title.replace("_", " "),
        subtitle=f"{genre.upper()} // CYBERFLOW",
        bpm=int(bpm),
        key=key_name,
        output_png=bg_path
    )
    create_youtube_thumbnail(
        bg_image_path=bg_path,
        main_title=title.replace("_", " ").upper(),
        subtitle=f"{genre.upper()} // CYBERPUNK FLOW",
        badge_text=f"{int(bpm)} BPM 24-BIT",
        output_path=thumb_path
    )

    # Step 5: Video Render
    print("\n[5/6] Rendering 1080p MP4 video with live frequency spectrum visualizer...")
    render_video_with_visualizer(
        bg_image_path=bg_path,
        audio_wav_path=wav_path,
        output_mp4_path=mp4_path
    )

    # Step 6: YouTube Metadata
    print("\n[6/6] Generating SEO YouTube metadata and scrubber chapters...")
    meta = generate_youtube_metadata(
        track_title=title.replace("_", " "),
        genre=genre,
        bpm=int(bpm),
        key=key_name,
        duration_sec=arr.total_duration
    )
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  ✓ Saved YouTube metadata: {meta_path}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"🎉 PRODUCTION COMPLETE IN {elapsed:.1f} SECONDS!")
    print(f"📦 Master Audio: {wav_path}")
    print(f"📦 Streaming MP3: {mp3_path}")
    print(f"🎬 Full Video:   {mp4_path}")
    print(f"🖼️ Thumbnail:    {thumb_path}")
    print(f"📄 Metadata:     {meta_path}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Headless Music & Video Studio")
    parser.add_argument("--title", default="Neon_Horizon", help="Track title")
    parser.add_argument("--genre", default="synthwave", choices=["synthwave", "lofi", "ambient", "neoclassical"], help="Music genre")
    parser.add_argument("--bpm", type=float, default=118.0, help="Tempo in BPM")
    parser.add_argument("--bars", type=int, default=16, help="Number of bars")
    parser.add_argument("--key", default="D Minor", help="Musical key")
    parser.add_argument("--engine", default="neural", choices=["neural", "soundfont"], help="Audio synthesis engine (neural via MusicGen or SoundFont GM)")
    parser.add_argument("--model", default="facebook/musicgen-stereo-large", help="MusicGen model repository (e.g. facebook/musicgen-stereo-large, facebook/musicgen-large, facebook/musicgen-stereo-medium)")

    args = parser.parse_args()
    run_pipeline(
        title=args.title,
        genre=args.genre,
        bpm=args.bpm,
        bars=args.bars,
        key_name=args.key,
        engine=args.engine,
        model_name=args.model
    )

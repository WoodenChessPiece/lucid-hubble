"""
render_top100_edm_showcase.py - Autonomous Masterclass StudioBrain Showcase Orchestrator
Synthesizes the Top 100 EDM Artists Billboard Database and Billboard Hot 100 with StudioBrain:
- Dynamic Prompt & Artist Ingestion: deadmau5, Daft Punk, Skrillex, Rüfüs Du Sol, Martin Garrix, Billie Eilish, etc.
- Harmonic Brain: Section-distinct progressions (verse != chorus != breakdown), Drop-2/4 voicings, modal borrowing.
- Melodic Brain: 7-stage motif mutation, Beat 4.5 pickup, golden-ratio climax, conversational polyphony.
- Groove Brain: 5 genre drum pockets, 30% staccato gate bass physics, 4-tier velocity humanization.
- Structural Brain: Archetype selection, Bar 32 Beat 4 Zero-Drop silence, dynamic risers.
- Timbral & Mixing Brain: SoundFont/keys sampling, Moog ladder filter, Abbey Road aux reverb, Console8 summing.
- Mastering: EBU R128 (-14.0 LUFS / -1.5 dBTP).
"""

import time
import os
import sys
import shutil
import argparse
import random
import subprocess
import numpy as np
import scipy.io.wavfile as wav

from src.composer.studio_brain import get_studio_brain
from src.engine.synth import MultiTrackEngine
from src.mastering.chain import YouTubeMasteringChain


def slugify(text: str) -> str:
    """Creates a clean filesystem slug from string."""
    return "".join(c if c.isalnum() else "_" for c in str(text)).strip("_")


def main():
    parser = argparse.ArgumentParser(
        description="StudioBrain Autonomous Multi-Artist Showcase CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 render_top100_edm_showcase.py --artist "deadmau5"
  python3 render_top100_edm_showcase.py --prompt "Daft Punk disco funk with vocoder lead and swinging bass"
  python3 render_top100_edm_showcase.py --prompt "Skrillex heavy dubstep drop with halftime drums"
  python3 render_top100_edm_showcase.py --artist "Rufus Du Sol" --genre "melodic_house"
  python3 render_top100_edm_showcase.py --artist "Billie Eilish" --prompt "dark pop bedroom aesthetic"
  python3 render_top100_edm_showcase.py --random
  python3 render_top100_edm_showcase.py --list-artists
        """
    )
    parser.add_argument("-p", "--prompt", type=str, help="Natural language prompt describing desired artist, genre, or mood")
    parser.add_argument("-a", "--artist", type=str, default=None, help="Explicit artist name (from 100 EDM or Billboard hits)")
    parser.add_argument("-g", "--genre", type=str, default=None, help="Genre/subgenre (e.g. progressive_house, melodic_techno, french_touch, dubstep, dark_pop)")
    parser.add_argument("--bpm", type=float, default=None, help="Tempo in BPM")
    parser.add_argument("--bars", type=int, default=96, help="Total bar count (default: 96)")
    parser.add_argument("--archetype", type=str, default=None, help="Structural archetype (narrative_7part, slow_burn_progressive, in_medias_res, continuous_drive, aaba_classic)")
    parser.add_argument("--list-artists", action="store_true", help="List all 100 EDM artists across 5 disciplines + Billboard hits")
    parser.add_argument("--random", action="store_true", help="Pick a random artist from the Top 100 EDM database")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive prompt loop")

    args = parser.parse_args()

    brain = get_studio_brain(force_reload=True)

    # 1. Handle --list-artists
    if args.list_artists:
        print("=" * 75)
        print("🎧 TOP 100 EDM BILLBOARD ARTISTS DATABASE & BILLBOARD HITS")
        print("=" * 75)
        if brain.edm_loader:
            disciplines = brain.edm_loader.data.get("metadata", {}).get("disciplines", [])
            for disc in disciplines:
                print(f"\n📂 {disc}:")
                progs = brain.edm_loader.get_progressions_by_discipline(disc.split()[0].lower())
                artists_in_disc = sorted(list(set(p.get("artist") for p in progs if p.get("artist"))))
                for idx, a_name in enumerate(artists_in_disc, 1):
                    art = brain.get_edm_artist(a_name)
                    subg = art.get("subgenre") if art else "EDM"
                    print(f"   {idx:2d}. {a_name:<26} ({subg})")
        if brain.billboard_loader:
            print("\n📂 Modern Billboard Hot 100 Artists:")
            bb_artists = sorted(list(set(p.artist for p in brain.billboard_loader.progressions)))
            for idx, b_name in enumerate(bb_artists, 1):
                print(f"   {idx:2d}. {b_name}")
        print("=" * 75)
        return

    # 2. Interactive or Random Selection
    prompt = args.prompt
    artist_choice = args.artist
    genre_choice = args.genre
    bpm_choice = args.bpm
    archetype_choice = args.archetype
    bars_choice = args.bars

    if args.random:
        all_artists = brain.get_all_edm_artists()
        artist_choice = random.choice(all_artists)
        print(f"🎲 Randomly selected artist: {artist_choice}")

    elif args.interactive:
        print("\n🎹 StudioBrain Interactive Session")
        user_in = input("Enter prompt or artist name (e.g. 'deadmau5 Strobe', 'Daft Punk disco funk', 'Skrillex'): ").strip()
        if user_in:
            prompt = user_in

    # Default fallback if no arguments provided: Avicii (with notice on full capabilities)
    if not prompt and not artist_choice:
        artist_choice = "Avicii"
        print("\n💡 [Notice] No prompt/artist specified; defaulting to Avicii.")
        print("   Run with '--prompt \"deadmau5 Strobe\"' or '--prompt \"Daft Punk disco funk\"' or '--list-artists' to render any of 100+ artists!")

    print("=" * 75)
    print("🚀 STUDIOBRAIN INTERCONNECTED MASTERCLASS ORCHESTRATION")
    print("=" * 75)

    start_time = time.time()

    # 3. Autonomous Orchestration pass
    print("\n[1/4] Orchestrating Composition across 5 Intelligence Layers...")
    arr = brain.orchestrate(
        prompt=prompt,
        artist=artist_choice,
        genre=genre_choice,
        bpm=bpm_choice,
        bars=bars_choice,
        archetype=archetype_choice
    )

    resolved_artist = arr.artist or "Masterclass Artist"
    print(f"  ✓ Artist Model:       {resolved_artist}")
    print(f"  ✓ Genre / Archetype:  {arr.genre} / {arr.archetype}")
    print(f"  ✓ Tempo / Duration:   {arr.bpm:.1f} BPM / {arr.bars} bars ({arr.total_duration:.1f}s / {arr.total_duration / 60.0:.2f} mins)")
    if arr.progression:
        print(f"  ✓ Anthem Harmony:     {arr.progression.get('roman_numerals', 'Dynamic')} (Key: {arr.progression.get('key', 'D')})")
    if arr.motif:
        print(f"  ✓ Melodic Topline:    {arr.motif.get('title', 'Dynamic Motif')} (Pickup: Beat {arr.motif.get('pickup_beat', 4.5)})")
    if arr.bass_groove:
        print(f"  ✓ Bass Pocket:        {arr.bass_groove.get('style', '30% Gate Staccato')}")

    print("\n[2/4] Stem Channel Distribution:")
    for track_name in ["kick", "snare", "hihat", "bass", "chords", "lead", "counter", "pad", "fx"]:
        count = len(arr.tracks.get(track_name, []))
        print(f"  - {track_name.capitalize():<8} events: {count}")

    # 4. Multi-Track Stem Synthesis with DSP Engine
    print("\n[3/4] Synthesizing multi-track stems with Moog ladder filter & Console8 summing...")
    engine = MultiTrackEngine()
    raw_audio = engine.render_arrangement(arr)

    # 5. YouTube EBU R128 Mastering
    print("\n[4/4] Mastering to YouTube EBU R128 (-14.0 LUFS / -1.5 dBTP)...")
    masterer = YouTubeMasteringChain()
    mastered = masterer.master(raw_audio)

    os.makedirs("storage/renders", exist_ok=True)
    slug_artist = slugify(resolved_artist)
    slug_arch = slugify(arr.archetype)

    wav_out = f"storage/renders/SHOWCASE_{slug_artist}_{slug_arch}.wav"
    mp3_out = f"storage/renders/SHOWCASE_{slug_artist}_{slug_arch}.mp3"
    legacy_mp3 = "storage/renders/TOP100_EDM_BILLBOARD_SHOWCASE.mp3"

    int16_audio = np.int16(np.clip(mastered * 32767, -32767, 32767))
    wav.write(wav_out, masterer.sr, int16_audio)
    print(f"  ✓ Exported WAV: {wav_out} ({os.path.getsize(wav_out)/(1024*1024):.1f} MB)")

    # Encode MP3
    subprocess.run(["ffmpeg", "-y", "-i", wav_out, "-b:a", "320k", mp3_out], capture_output=True, check=True)
    print(f"  ✓ Exported MP3: {mp3_out} ({os.path.getsize(mp3_out)/(1024*1024):.1f} MB)")

    # Keep legacy MP3 updated as well
    shutil.copy2(mp3_out, legacy_mp3)

    # Copy to artifacts directories for instant user listening
    artifact_dirs = [
        "/Users/x17hubris/.gemini/antigravity/brain/b6fe3629-0cf8-4957-893e-ef9af8289970",
        "/Users/x17hubris/.gemini/antigravity/brain/2baed02c-ab43-4d91-ac2f-98fb034dc090"
    ]
    copied_artifacts = []
    for adir in artifact_dirs:
        if os.path.exists(adir):
            art_dest = os.path.join(adir, os.path.basename(mp3_out))
            shutil.copy2(mp3_out, art_dest)
            shutil.copy2(mp3_out, os.path.join(adir, "TOP100_EDM_BILLBOARD_SHOWCASE.mp3"))
            copied_artifacts.append(art_dest)

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"🎉 MASTERCLASS RENDER COMPLETE IN {elapsed:.1f} SECONDS!")
    print(f"🎧 Local Render:  {mp3_out}")
    for ca in copied_artifacts:
        print(f"🎧 Artifact:      {ca}")
    print("=" * 75)


if __name__ == "__main__":
    main()

"""
render_top100_edm_showcase.py - Renders a Masterclass Showcase Track
Synthesizing the Top 100 EDM Artists Billboard Database with StudioBrain:
- Harmonic Intelligence: Ingested from Avicii / Swedish House Mafia / deadmau5 Billboard hits
- Melodic Intelligence: Beat 4.5 pickup, 7-stage motif mutation, golden-ratio climax
- Groove Intelligence: 30% gate staccato bass pocket, velocity tier dynamics
- Timbral Intelligence: Moog 24dB ladder filter, Reese bass, analog summing
- Structural Intelligence: 7-part narrative arc with Bar 32 Beat 4 Zero-Drop silence
- Mastering: EBU R128 (-14.0 LUFS)
"""

import time
import os
import shutil
import subprocess
import numpy as np
import scipy.io.wavfile as wav

from src.composer.studio_brain import get_studio_brain
from src.engine.synth import MultiTrackEngine
from src.mastering.chain import YouTubeMasteringChain

def main():
    print("=" * 70)
    print("🚀 RENDERING TOP 100 EDM BILLBOARD MASTERCLASS SHOWCASE")
    print("=" * 70)

    start_time = time.time()
    brain = get_studio_brain(force_reload=True)

    # 1. Inspect EDM Database Status
    artists = brain.get_all_edm_artists()
    print(f"\n[1/4] StudioBrain Online: {len(artists)} EDM Artists indexed.")
    
    # 2. Query Avicii / Swedish House Mafia composition from Top 100 database
    artist_choice = "Avicii"
    edm_art = brain.get_edm_artist(artist_choice)
    edm_prog = brain.get_edm_progression(artist_choice)
    print(f"  ✓ Ingested Artist Model: {edm_art.get('name')} ({edm_art.get('subgenre')})")
    print(f"  ✓ Progression: {edm_prog.get('roman_numerals')} (Key: {edm_prog.get('key')})")

    # 3. Generate Arrangement via StudioBrain
    print("\n[2/4] Composing 96-bar Masterclass Arrangement via StudioBrain...")
    arr = brain.generate_arrangement(
        genre="progressive_house",
        bpm=126.0,
        bars=96,
        archetype="narrative_7part",
        artist=artist_choice
    )
    print(f"  ✓ Arranged {len(arr.tracks)} stems over {arr.total_duration:.1f}s ({arr.total_duration / 60.0:.2f} mins)")
    print(f"  - Kick events:   {len(arr.tracks['kick'])}")
    print(f"  - Bass events:   {len(arr.tracks['bass'])}")
    print(f"  - Lead events:   {len(arr.tracks['lead'])}")
    print(f"  - Chords events: {len(arr.tracks['chords'])}")
    print(f"  - Pad events:    {len(arr.tracks['pads'])}")
    print(f"  - FX events:     {len(arr.tracks['fx'])}")

    # 4. Synthesize with upgraded DSP
    print("\n[3/4] Synthesizing multi-track stems with Moog ladder filter & Console8 summing...")
    engine = MultiTrackEngine()
    raw_audio = engine.render_arrangement(arr)

    # 5. Master to -14 LUFS
    print("\n[4/4] Mastering to YouTube EBU R128 (-14.0 LUFS / -1.5 dBTP)...")
    masterer = YouTubeMasteringChain()
    mastered = masterer.master(raw_audio)

    os.makedirs("storage/renders", exist_ok=True)
    wav_out = "storage/renders/TOP100_EDM_BILLBOARD_SHOWCASE.wav"
    mp3_out = "storage/renders/TOP100_EDM_BILLBOARD_SHOWCASE.mp3"

    int16_audio = np.int16(np.clip(mastered * 32767, -32767, 32767))
    wav.write(wav_out, masterer.sr, int16_audio)
    print(f"  ✓ Exported WAV: {wav_out} ({os.path.getsize(wav_out)/(1024*1024):.1f} MB)")

    # Encode MP3
    subprocess.run(["ffmpeg", "-y", "-i", wav_out, "-b:a", "320k", mp3_out], capture_output=True, check=True)
    print(f"  ✓ Exported MP3: {mp3_out} ({os.path.getsize(mp3_out)/(1024*1024):.1f} MB)")

    # Copy to artifacts directory so user can listen directly
    artifact_dir = "/Users/x17hubris/.gemini/antigravity/brain/2baed02c-ab43-4d91-ac2f-98fb034dc090"
    artifact_mp3 = os.path.join(artifact_dir, "TOP100_EDM_BILLBOARD_SHOWCASE.mp3")
    shutil.copy2(mp3_out, artifact_mp3)
    print(f"  ✓ Copied to Artifacts: {artifact_mp3}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"🎉 RENDER COMPLETE IN {elapsed:.1f} SECONDS!")
    print(f"🎧 Google Drive: storage/renders/TOP100_EDM_BILLBOARD_SHOWCASE.mp3")
    print(f"🎧 Artifact: {artifact_mp3}")
    print("=" * 70)

if __name__ == "__main__":
    main()

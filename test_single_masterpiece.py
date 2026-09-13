"""
test_single_masterpiece.py - Renders a single 3.5-minute masterclass track
using the newly integrated Knowledge Base, 7-part song structure, and thematic motif generator.
"""

import time
import os
import subprocess
import numpy as np
import scipy.io.wavfile as wav
from src.composer.arranger import create_arrangement
from src.engine.synth import MultiTrackEngine
from src.mastering.chain import YouTubeMasteringChain

print("=" * 65)
print("🎵 MASTERCLASS COMPOSITION BENCHMARK (3.5 MIN TRACK)")
print("Narrative Arc: Intro -> Verse -> Build-up -> Zero-Drop -> Chorus -> Breakdown -> Climax -> Outro")
print("=" * 65)

start_time = time.time()

# 1. Arrange 96 bars (full commercial narrative arc)
print("\n[1/3] Composing 96-bar masterclass arrangement from KnowledgeBase...")
arr = create_arrangement(genre="synthwave", bpm=118.0, bars=96)
print(f"  ✓ Arranged {len(arr.tracks)} stems. Duration: {arr.total_duration / 60.0:.2f} mins ({arr.total_duration:.1f}s)")
print(f"  - Kick events:  {len(arr.tracks['kick'])}")
print(f"  - Snare events: {len(arr.tracks['snare'])}")
print(f"  - Lead events:  {len(arr.tracks['lead'])}")
print(f"  - Bass events:  {len(arr.tracks['bass'])}")

# 2. Synthesize with upgraded DSP
print("\n[2/3] Synthesizing multi-track stems with Moog ladder filter & Console8 summing...")
engine = MultiTrackEngine()
raw_audio = engine.render_arrangement(arr)

# 3. Master to -14 LUFS
print("\n[3/3] Mastering to YouTube EBU R128 (-14.0 LUFS / -1.5 dBTP)...")
masterer = YouTubeMasteringChain()
mastered = masterer.master(raw_audio)

wav_out = "storage/renders/MASTERCLASS_SHOWCASE.wav"
mp3_out = "storage/renders/MASTERCLASS_SHOWCASE.mp3"

int16_audio = np.int16(np.clip(mastered * 32767, -32767, 32767))
wav.write(wav_out, masterer.sr, int16_audio)
print(f"  ✓ Exported WAV: {wav_out} ({os.path.getsize(wav_out)/(1024*1024):.1f} MB)")

# Encode MP3
subprocess.run(["ffmpeg", "-y", "-i", wav_out, "-b:a", "320k", mp3_out], capture_output=True, check=True)
print(f"  ✓ Exported MP3: {mp3_out} ({os.path.getsize(mp3_out)/(1024*1024):.1f} MB)")

elapsed = time.time() - start_time
print("\n" + "=" * 65)
print(f"🎉 RENDER COMPLETE IN {elapsed:.1f} SECONDS!")
print(f"🎧 Listen in Google Drive: storage/renders/MASTERCLASS_SHOWCASE.mp3")
print("=" * 65)

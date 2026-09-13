"""
src/engine/stitcher.py - Stream-based Album Synthesizer and Equal-Power Crossfader
Generates 60+ minute audio streams with low RAM footprint and seamless track transitions.
"""

import os
import math
import wave
import numpy as np
import scipy.signal as signal
from src.composer.album import Album
from src.engine.synth import MultiTrackEngine
from src.mastering.chain import YouTubeMasteringChain

SAMPLE_RATE = 44100

def equal_power_crossfade(tail_audio: np.ndarray, head_audio: np.ndarray) -> np.ndarray:
    """
    Applies equal-power crossfade (cos/sin gain law) to prevent volume dip during transitions.
    cos^2(x) + sin^2(x) = 1.0 (constant acoustic power)
    """
    overlap_samples = min(len(tail_audio), len(head_audio))
    t = np.linspace(0, np.pi / 2.0, overlap_samples)
    fade_out = np.cos(t)[:, np.newaxis]
    fade_in = np.sin(t)[:, np.newaxis]

    blended = tail_audio[:overlap_samples] * fade_out + head_audio[:overlap_samples] * fade_in
    return blended

def render_and_stitch_album(
    album: Album,
    output_wav_path: str,
    crossfade_seconds: float = 3.0
) -> str:
    """
    Renders an entire album track-by-track and stitches them into a continuous master WAV.
    Streams directly to disk to preserve system memory.
    """
    os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)
    engine = MultiTrackEngine(sample_rate=SAMPLE_RATE)
    mastering = YouTubeMasteringChain(sample_rate=SAMPLE_RATE)

    crossfade_samples = int(crossfade_seconds * SAMPLE_RATE)

    # Open standard 16-bit stereo wave writer
    wav_out = wave.open(output_wav_path, "wb")
    wav_out.setnchannels(2)
    wav_out.setsampwidth(2)
    wav_out.setframerate(SAMPLE_RATE)

    overlap_buffer = None

    print(f"[Stitcher] Rendering {len(album.tracks)} tracks to {output_wav_path}...")

    for i, track in enumerate(album.tracks):
        print(f"  -> Rendering [{track.index}/{len(album.tracks)}] {track.title} ({track.key}, {track.bpm:.0f} BPM)...")

        # 1. Synthesize track stems
        raw_track = engine.render_arrangement(track.arrangement)

        # 2. Master track to YouTube -14 LUFS
        mastered_track = mastering.master(raw_track)

        if overlap_buffer is None:
            # First track
            body = mastered_track[:-crossfade_samples]
            overlap_buffer = mastered_track[-crossfade_samples:]

            # Write body
            pcm_body = np.int16(np.clip(body * 32767, -32767, 32767)).tobytes()
            wav_out.writeframes(pcm_body)
        else:
            # Crossfade previous tail with current track head
            head = mastered_track[:crossfade_samples]
            crossfaded = equal_power_crossfade(overlap_buffer, head)

            if i == len(album.tracks) - 1:
                # Last track: write crossfade and entire rest of track
                rest = mastered_track[crossfade_samples:]
                final_block = np.vstack([crossfaded, rest])
                pcm_final = np.int16(np.clip(final_block * 32767, -32767, 32767)).tobytes()
                wav_out.writeframes(pcm_final)
                overlap_buffer = None
            else:
                body = mastered_track[crossfade_samples:-crossfade_samples]
                overlap_buffer = mastered_track[-crossfade_samples:]
                block = np.vstack([crossfaded, body])
                pcm_block = np.int16(np.clip(block * 32767, -32767, 32767)).tobytes()
                wav_out.writeframes(pcm_block)

    wav_out.close()
    print(f"[Stitcher] Successfully rendered continuous album to: {output_wav_path}")
    return output_wav_path

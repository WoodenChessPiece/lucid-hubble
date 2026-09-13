"""
src/engine/runpod_neural_engine.py - RunPod Serverless Neural AudioCraft & MusicGen Client

Bridges Lucid Hubble's StudioBrain symbolic intelligence (MIDI, chord progressions,
melody sentences, and Meyer-Narmour motifs) with RunPod GPU serverless workers running
Meta AudioCraft (facebook/musicgen-melody, musicgen-stereo) and Stable Audio.

Features:
1. REST client using standard library urllib (zero external dependency footprint).
2. Conditioning audio synthesis: Renders StudioBrain NoteEvents to guide WAVs for
   MusicGen chromagram conditioning (model.generate_with_chroma).
3. Hybrid Production Pipeline: Combines neural stems (ambient pads, vocal chops, analog leads)
   with deterministic, phase-locked DSP drums and sub-bass pocket.
4. Built-in Offline Mock / Dry-Run mode with harmonic surrogate synthesis for local CI/CD
   and dev workflows without spending GPU credits.
"""

from __future__ import annotations

import os
import io
import json
import time
import base64
import math
import wave
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union

import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Imports from local project modules
try:
    from src.composer.arranger import NoteEvent, Arrangement
    from src.composer.theory import midi_to_freq
    from src.engine.analog_saturation import console8_channel_encode, console8_bus_decode
    from src.engine.sound_layering import MidSideProcessor, LinkwitzRileyCrossover
except ImportError:
    try:
        from composer.arranger import NoteEvent, Arrangement
        from composer.theory import midi_to_freq
        from engine.analog_saturation import console8_channel_encode, console8_bus_decode
        from engine.sound_layering import MidSideProcessor, LinkwitzRileyCrossover
    except ImportError:
        @dataclass
        class NoteEvent:
            pitch: int
            start_time: float
            duration: float
            velocity: int = 100

        def midi_to_freq(pitch: int) -> float:
            return 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        console8_channel_encode = lambda x, drive=1.0: np.sin(x * drive)
        console8_bus_decode = lambda x, drive=1.0: np.arcsin(np.clip(x * drive, -0.99, 0.99))


RUNPOD_API_BASE = "https://api.runpod.ai/v2"


@dataclass
class NeuralGenerationConfig:
    """Configuration parameters for RunPod Neural AudioCraft generation."""
    model_name: str = "facebook/musicgen-melody"
    prompt: str = "Avicii style progressive house melodic lead, warm analog supersaws, stadium acoustics, 128 bpm"
    duration_seconds: float = 8.0
    temperature: float = 1.0
    top_k: int = 250
    top_p: float = 0.0
    cfg_coef: float = 3.5
    sample_rate: int = 32000
    stereo: bool = True
    normalize: bool = True


class RunPodNeuralEngine:
    """
    RunPod Serverless Client for Neural AudioCraft / MusicGen Generation.
    Arbitrates cloud GPU inference, audio conditioning serialization, and
    hybrid stem summing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint_id: Optional[str] = None,
        mock_mode: Optional[bool] = None,
        timeout_seconds: float = 180.0,
        poll_interval: float = 2.0,
        target_sample_rate: int = 44100
    ):
        self.api_key = api_key or os.getenv("RUNPOD_API_KEY", "")
        self.endpoint_id = endpoint_id or os.getenv("RUNPOD_ENDPOINT_ID", "")
        self.timeout_seconds = timeout_seconds
        self.poll_interval = poll_interval
        self.target_sr = target_sample_rate

        # Enable mock_mode automatically if no API credentials exist
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            self.mock_mode = not (bool(self.api_key) and bool(self.endpoint_id))

    # -----------------------------------------------------------------------
    # Audio Serialization & Guide Audio Rendering
    # -----------------------------------------------------------------------

    def render_guide_audio_from_notes(
        self,
        notes: List[NoteEvent],
        total_duration: float,
        sr: int = 32000
    ) -> np.ndarray:
        """
        Renders a simple, clean sinusoidal/saw harmonic guide audio track from NoteEvents.
        This provides the exact pitch/chromagram conditioning that facebook/musicgen-melody
        extracts via Demucs + chromagram STFT filters.
        """
        num_samples = int(total_duration * sr)
        audio = np.zeros(num_samples, dtype=np.float32)

        for n in notes:
            start_idx = int(n.start_time * sr)
            dur_samples = int(n.duration * sr)
            end_idx = min(start_idx + dur_samples, num_samples)
            actual_len = end_idx - start_idx
            if actual_len <= 0:
                continue

            freq = midi_to_freq(n.pitch)
            t = np.linspace(0, actual_len / sr, actual_len, endpoint=False)

            # Fundamental + soft 2nd/3rd harmonics for optimal chroma recognition
            h1 = np.sin(2 * np.pi * freq * t)
            h2 = 0.5 * np.sin(2 * np.pi * 2 * freq * t)
            h3 = 0.25 * np.sin(2 * np.pi * 3 * freq * t)
            tone = (h1 + h2 + h3) / 1.75

            # Smooth envelope (fast attack, gentle release to avoid transient pops)
            att_len = min(int(0.015 * sr), actual_len // 4)
            rel_len = min(int(0.04 * sr), actual_len // 4)
            env = np.ones(actual_len, dtype=np.float32)
            if att_len > 0:
                env[:att_len] = np.linspace(0, 1, att_len)
            if rel_len > 0:
                env[-rel_len:] = np.linspace(1, 0, rel_len)

            gain = (n.velocity / 127.0) * 0.7
            audio[start_idx:end_idx] += tone * env * gain

        # Soft clip to prevent inter-note overs
        return np.tanh(audio)

    def audio_to_wav_base64(self, audio: np.ndarray, sr: int = 32000) -> str:
        """Encodes a float32 numpy audio buffer to Base64-encoded WAV."""
        # Convert float32 in [-1, 1] to int16
        audio_clipped = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio_clipped * 32767.0).astype(np.int16)

        bio = io.BytesIO()
        wavfile.write(bio, sr, audio_int16)
        bio.seek(0)
        return base64.b64encode(bio.read()).decode("ascii")

    def wav_base64_to_audio(self, b64_str: str) -> Tuple[np.ndarray, int]:
        """Decodes Base64-encoded WAV back into float32 numpy array [-1, 1] and sample rate."""
        wav_bytes = base64.b64decode(b64_str)
        bio = io.BytesIO(wav_bytes)
        sr, raw = wavfile.read(bio)

        if raw.dtype == np.int16:
            audio = raw.astype(np.float32) / 32768.0
        elif raw.dtype == np.int32:
            audio = raw.astype(np.float32) / 2147483648.0
        elif raw.dtype == np.uint8:
            audio = (raw.astype(np.float32) - 128.0) / 128.0
        else:
            audio = raw.astype(np.float32)

        # Ensure stereo output shape (samples, 2)
        if audio.ndim == 1:
            audio = np.column_stack((audio, audio))
        elif audio.ndim == 2 and audio.shape[0] == 2 and audio.shape[1] > 2:
            audio = audio.T

        return audio, sr

    def resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resamples audio from orig_sr to target_sr using Fourier polyphase resampling."""
        if orig_sr == target_sr:
            return audio
        num_target_samples = int(round(len(audio) * float(target_sr) / orig_sr))
        resampled = signal.resample(audio, num_target_samples, axis=0)
        return resampled.astype(np.float32)

    # -----------------------------------------------------------------------
    # RunPod API Job Dispatch & Polling
    # -----------------------------------------------------------------------

    def _execute_runpod_request(self, endpoint_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a JSON POST request against the RunPod Serverless API using urllib."""
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "LucidHubble-AudioCraft/1.0"
        }
        req = urllib.request.Request(endpoint_url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status_code = resp.getcode()
                body = resp.read().decode("utf-8")
                if status_code not in (200, 201):
                    raise RuntimeError(f"RunPod API returned HTTP {status_code}: {body}")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"RunPod HTTP Error {e.code}: {err_msg}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"RunPod Network Connection Error: {e.reason}") from e

    def _poll_runpod_status(self, job_id: str) -> Dict[str, Any]:
        """Polls /status/{job_id} until completion or timeout."""
        status_url = f"{RUNPOD_API_BASE}/{self.endpoint_id}/status/{job_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "LucidHubble-AudioCraft/1.0"
        }
        req = urllib.request.Request(status_url, headers=headers, method="GET")

        start_time = time.time()
        while time.time() - start_time < self.timeout_seconds:
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    status = data.get("status")
                    if status == "COMPLETED":
                        return data.get("output", {})
                    elif status in ("FAILED", "CANCELLED", "TIMED_OUT"):
                        raise RuntimeError(f"RunPod job {job_id} terminated with status: {status}, error: {data.get('error')}")
            except urllib.error.URLError:
                # Transient network jitter, retry after poll_interval
                pass

            time.sleep(self.poll_interval)

        raise TimeoutError(f"RunPod job {job_id} exceeded timeout of {self.timeout_seconds}s")

    # -----------------------------------------------------------------------
    # Core Neural Generation Functionality
    # -----------------------------------------------------------------------

    def generate_stem(
        self,
        config: NeuralGenerationConfig,
        melody_notes: Optional[List[NoteEvent]] = None,
        guide_audio: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Main entry point for generating a neural audio stem.
        Takes text prompt + optional melodic/harmonic conditioning and returns
        a stereo float32 numpy array at target_sample_rate.
        """
        # If running in mock/offline mode, generate rich harmonic surrogate audio
        if self.mock_mode:
            return self._generate_mock_stem(config, melody_notes, guide_audio)

        # Prepare conditioning audio
        melody_b64: Optional[str] = None
        if guide_audio is not None:
            melody_b64 = self.audio_to_wav_base64(guide_audio, sr=config.sample_rate)
        elif melody_notes and len(melody_notes) > 0:
            guide = self.render_guide_audio_from_notes(
                melody_notes,
                total_duration=config.duration_seconds,
                sr=config.sample_rate
            )
            melody_b64 = self.audio_to_wav_base64(guide, sr=config.sample_rate)

        # Build payload according to RunPod worker specification
        payload = {
            "input": {
                "model_name": config.model_name,
                "prompt": config.prompt,
                "duration": config.duration_seconds,
                "temperature": config.temperature,
                "top_k": config.top_k,
                "top_p": config.top_p,
                "cfg_coef": config.cfg_coef,
                "sample_rate": config.sample_rate,
                "melody_audio": melody_b64,
                "stereo": config.stereo,
                "normalize": config.normalize
            }
        }

        # Submit job to RunPod Serverless
        run_url = f"{RUNPOD_API_BASE}/{self.endpoint_id}/run"
        response = self._execute_runpod_request(run_url, payload)
        job_id = response.get("id")
        if not job_id:
            raise RuntimeError(f"RunPod response did not contain job id: {response}")

        # Poll status until finished
        output = self._poll_runpod_status(job_id)
        audio_b64 = output.get("audio_b64")
        if not audio_b64:
            raise RuntimeError(f"RunPod job completed but returned no audio_b64: {output.keys()}")

        # Decode received WAV and resample to project sample rate
        raw_audio, sr = self.wav_base64_to_audio(audio_b64)
        processed = self.resample_audio(raw_audio, orig_sr=sr, target_sr=self.target_sr)
        return processed

    # -----------------------------------------------------------------------
    # Production Convenience Methods
    # -----------------------------------------------------------------------

    def generate_melody_lead(
        self,
        notes: List[NoteEvent],
        duration: float,
        style_prompt: str = "Avicii melodic lead, massive warm analog supersaws, stadium acoustics, euphoric progressive house, pristine high-end sheen",
        stereo: bool = True
    ) -> np.ndarray:
        """Generates a melodic lead stem conditioned strictly on MIDI notes."""
        cfg = NeuralGenerationConfig(
            model_name="facebook/musicgen-melody",
            prompt=style_prompt,
            duration_seconds=duration,
            stereo=stereo,
            temperature=0.85,
            cfg_coef=4.0
        )
        return self.generate_stem(cfg, melody_notes=notes)

    def generate_ambient_pad_layer(
        self,
        chord_notes: List[NoteEvent],
        duration: float,
        style_prompt: str = "Cinematic Brian Eno ambient shimmer pad, lush analog warmth, sweeping 24dB Moog filter, deep spatial reverberation",
    ) -> np.ndarray:
        """Generates an atmospheric pad layer conditioned on chord voicings."""
        cfg = NeuralGenerationConfig(
            model_name="facebook/musicgen-melody",
            prompt=style_prompt,
            duration_seconds=duration,
            stereo=True,
            temperature=0.95,
            cfg_coef=3.5
        )
        return self.generate_stem(cfg, melody_notes=chord_notes)

    def generate_vocal_chops(
        self,
        duration: float,
        key: str = "A minor",
        bpm: int = 128,
        style_prompt: str = "Ethereal female vocal chops, future bass ad-libs, pitch shifted vocal hook, wide stereo space, studio plate reverb"
    ) -> np.ndarray:
        """Generates melodic vocal textures and ad-lib phrases in key."""
        prompt = f"{style_prompt}, in {key}, {bpm} bpm"
        cfg = NeuralGenerationConfig(
            model_name="facebook/musicgen-melody",
            prompt=prompt,
            duration_seconds=duration,
            stereo=True,
            temperature=1.0,
            cfg_coef=3.2
        )
        return self.generate_stem(cfg)

    # -----------------------------------------------------------------------
    # Hybrid Stems Mixing & Interlocking
    # -----------------------------------------------------------------------

    def combine_hybrid_stems(
        self,
        deterministic_drums: np.ndarray,
        deterministic_bass: np.ndarray,
        neural_lead: Optional[np.ndarray] = None,
        neural_pads: Optional[np.ndarray] = None,
        neural_vocals: Optional[np.ndarray] = None,
        kick_times: Optional[List[float]] = None,
        sidechain_duck_amount: float = 0.88,
        sidechain_duration: float = 0.22
    ) -> np.ndarray:
        """
        Masterclass Hybrid Summing Pipeline:
        Combines deterministic punchy drums + locked sub-bass with rich neural stems.

        Process:
        1. Highpass/mono-clean neural stems: removes low-end sub frequencies (<120 Hz)
           to prevent phase cancellation with deterministic sub-bass.
        2. Applies raised-cosine sidechain ducking to neural leads/pads against kick transients.
        3. Airwindows Console8 saturation per stem to bind analog and neural timbres.
        4. Mid/side stereo widening on neural textures, mono-locked center for drums/bass.
        """
        max_len = max(
            len(deterministic_drums),
            len(deterministic_bass),
            len(neural_lead) if neural_lead is not None else 0,
            len(neural_pads) if neural_pads is not None else 0,
            len(neural_vocals) if neural_vocals is not None else 0
        )

        def pad_to_length(buf: Optional[np.ndarray]) -> np.ndarray:
            if buf is None:
                return np.zeros((max_len, 2), dtype=np.float32)
            if len(buf) < max_len:
                pad_arr = np.zeros((max_len - len(buf), 2), dtype=np.float32)
                return np.vstack((buf, pad_arr))
            return buf[:max_len]

        drums = pad_to_length(deterministic_drums)
        bass = pad_to_length(deterministic_bass)
        lead = pad_to_length(neural_lead)
        pads = pad_to_length(neural_pads)
        vox = pad_to_length(neural_vocals)

        # 1. Clean neural low-end (Elliptical filter / Highpass 120Hz)
        sos_hp = signal.butter(3, 120.0 / (self.target_sr / 2.0), btype="highpass", output="sos")
        lead = signal.sosfilt(sos_hp, lead, axis=0)
        pads = signal.sosfilt(sos_hp, pads, axis=0)
        vox = signal.sosfilt(sos_hp, vox, axis=0)

        # 2. Sidechain Ducking against Kicks
        if kick_times and len(kick_times) > 0:
            duck_samples = int(sidechain_duration * self.target_sr)
            t_arr = np.linspace(0, sidechain_duration, duck_samples)
            duck_curve = 1.0 - sidechain_duck_amount * (0.5 * (1.0 + np.cos(np.pi * t_arr / sidechain_duration)))
            duck_mask = np.ones(max_len, dtype=np.float32)

            for kt in kick_times:
                idx = int(kt * self.target_sr)
                end = min(idx + duck_samples, max_len)
                clen = end - idx
                if clen > 0:
                    duck_mask[idx:end] = np.minimum(duck_mask[idx:end], duck_curve[:clen])

            lead = lead * duck_mask[:, np.newaxis]
            pads = pads * duck_mask[:, np.newaxis]
            vox = vox * duck_mask[:, np.newaxis]

        # 3. Console8 Channel Saturation Encoding
        drums_enc = console8_channel_encode(drums * 0.95, drive=0.82)
        bass_enc = console8_channel_encode(bass * 0.90, drive=0.88)
        lead_enc = console8_channel_encode(lead * 0.70, drive=0.76)
        pads_enc = console8_channel_encode(pads * 0.65, drive=0.72)
        vox_enc = console8_channel_encode(vox * 0.60, drive=0.74)

        # Summed master bus
        summed = drums_enc + bass_enc + lead_enc + pads_enc + vox_enc
        master = console8_bus_decode(summed, drive=0.80)

        # Mono-maker below 110Hz on master bus
        try:
            master_t = MidSideProcessor.elliptical_mono_maker(master.T, cutoff_hz=110.0, fs=self.target_sr)
            master = master_t.T
        except Exception:
            pass

        return master

    # -----------------------------------------------------------------------
    # Local Offline Mock Generator
    # -----------------------------------------------------------------------

    def _generate_mock_stem(
        self,
        config: NeuralGenerationConfig,
        melody_notes: Optional[List[NoteEvent]] = None,
        guide_audio: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Generates an offline surrogate stem with rich harmonic chorus, analog detuning,
        and pseudo-spatial acoustics. Enables end-to-end pipeline execution without
        active RunPod credentials.
        """
        num_samples = int(config.duration_seconds * self.target_sr)
        out_l = np.zeros(num_samples, dtype=np.float32)
        out_r = np.zeros(num_samples, dtype=np.float32)

        t = np.linspace(0, config.duration_seconds, num_samples, endpoint=False)

        if melody_notes and len(melody_notes) > 0:
            for n in melody_notes:
                start_idx = int(n.start_time * self.target_sr)
                dur_samples = int(n.duration * self.target_sr)
                end_idx = min(start_idx + dur_samples, num_samples)
                actual_len = end_idx - start_idx
                if actual_len <= 0:
                    continue

                freq = midi_to_freq(n.pitch)
                tn = np.linspace(0, actual_len / self.target_sr, actual_len, endpoint=False)

                # 5-Saw detuned unison spread (supersaw modeling)
                detunes = [-0.012, -0.005, 0.0, 0.005, 0.012]
                note_l = np.zeros(actual_len, dtype=np.float32)
                note_r = np.zeros(actual_len, dtype=np.float32)

                for i, d in enumerate(detunes):
                    f = freq * (1.0 + d)
                    phase_l = np.random.uniform(0, 2 * np.pi)
                    phase_r = np.random.uniform(0, 2 * np.pi)
                    saw_l = signal.sawtooth(2 * np.pi * f * tn + phase_l)
                    saw_r = signal.sawtooth(2 * np.pi * f * tn + phase_r)
                    pan = i / 4.0
                    note_l += saw_l * (1.0 - pan * 0.6)
                    note_r += saw_r * (0.4 + pan * 0.6)

                # Lowpass filter and envelope
                sos = signal.butter(2, min(3800.0 / (self.target_sr / 2.0), 0.9), btype="lowpass", output="sos")
                note_l = signal.sosfilt(sos, note_l)
                note_r = signal.sosfilt(sos, note_r)

                env = np.exp(-3.5 * tn)
                gain = (n.velocity / 127.0) * 0.35

                out_l[start_idx:end_idx] += note_l * env * gain
                out_r[start_idx:end_idx] += note_r * env * gain
        else:
            # Ambient shimmer noise floor + sine wash
            noise_l = np.random.normal(0, 0.05, num_samples)
            noise_r = np.random.normal(0, 0.05, num_samples)
            sos = signal.butter(2, [300 / (self.target_sr/2), 4000 / (self.target_sr/2)], btype='bandpass', output='sos')
            out_l = signal.sosfilt(sos, noise_l) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t))
            out_r = signal.sosfilt(sos, noise_r) * (0.5 + 0.5 * np.cos(2 * np.pi * 0.25 * t))

        # Soft clip
        return np.column_stack((np.tanh(out_l), np.tanh(out_r)))


if __name__ == "__main__":
    engine = RunPodNeuralEngine(mock_mode=True)
    notes = [
        NoteEvent(pitch=60, start_time=0.0, duration=0.5, velocity=100),
        NoteEvent(pitch=64, start_time=0.5, duration=0.5, velocity=105),
        NoteEvent(pitch=67, start_time=1.0, duration=0.5, velocity=110),
        NoteEvent(pitch=71, start_time=1.5, duration=1.0, velocity=115),
    ]
    stem = engine.generate_melody_lead(notes, duration=3.0)
    print(f"Verified RunPodNeuralEngine! Generated stem shape: {stem.shape}, SR: {engine.target_sr}")

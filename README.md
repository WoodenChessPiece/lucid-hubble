# 🎛️ Headless Music Studio (lucid-hubble)

An autonomous, 100% headless AI-driven algorithmic music studio, DSP mastering chain, and hardware-accelerated video production pipeline built for macOS (Apple Silicon).

---

## 🚀 Features

- **Algorithmic Harmony & Composition Engine**: Drop-2 and parsimonious voice-leading, Meyer-Narmour gap-fill melodic contours, bebop metric downbeat anchors, and modal interchange.
- **Micro-Timing Humanization**: Distinct groove offsets (Darksynth driving grid with -2.2 ms snare push vs. Lo-Fi drunk swing with +18 ms snare drag) and sigmoidal velocity curves.
- **Analog DSP & Sound Design**: Moog 24dB 4-pole ladder filter modeling with non-linear saturation, 7-saw Roland JP-8000 stereo spread, raised-cosine sidechain ducking, and Airwindows Console8 channel/master bus summing.
- **Reference Mastering**: ITU-R BS.1770-4 K-weighted EBU R128 loudness targeting (-14.0 LUFS) with 4x oversampled true peak limiting (-1.5 dBTP) and Mid/Side mono bass management below 120 Hz.
- **Streaming Long-Form Producer**: Synthesizes 15-track continuous albums (~60 minutes) mapped across the Camelot harmonic wheel with 3-second equal-power crossfades. Memory consumption strictly capped under 300 MB RAM.
- **Hardware-Accelerated 1080p Video**: Apple Silicon VideoToolbox (`h264_videotoolbox`) rendering 1080p 60fps spectrum visualizer videos directly into cloud storage at >200 FPS.
- **Automated YouTube Publishing**: Resumable YouTube Data API v3 uploader with automatic clickable chapter generation and high-CTR thumbnail synthesis.
- **Zero Local SSD Clutter**: All master WAVs, 320k MP3s, and 1080p videos stream directly into Google Drive via symlinked storage.

---

## 📁 Repository Structure

```
├── build_1hour_video.py       # Orchestrator for 1-hour album, video, & YouTube publishing
├── src/
│   ├── composer/
│   │   ├── theory.py          # Music theory, Drop-2 voicing, Meyer-Narmour melody generator
│   │   ├── arranger.py        # Multi-track arrangement generator (kick, snare, hats, bass, pads, lead)
│   │   └── album.py           # 15-track continuous album generator across Camelot wheel
│   ├── engine/
│   │   ├── synth.py           # Multi-track synthesizer with Moog filter & JP-8000 supersaws
│   │   ├── analog_saturation.py # Airwindows Console8 summing & diode saturation
│   │   └── stitcher.py        # Streaming disk audio crossfader
│   ├── mastering/
│   │   └── chain.py           # YouTube -14 LUFS mastering limiter & M/S bass management
│   ├── visualizer/
│   │   ├── video.py           # Apple Silicon hardware video renderer with audio visualizer
│   │   └── thumbnail.py       # High-CTR YouTube thumbnail generator
│   └── publisher/
│       ├── youtube.py         # YouTube Data API v3 client
│       └── youtube_uploader.py# Resumable uploader with chapter metadata
```

---

## ⚡ Quick Start

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Render a 1-hour continuous album & video directly to Google Drive
python build_1hour_video.py --duration_mins 60.0 --genre synthwave --title "CYBERPUNK_NIGHT_DRIVE"
```

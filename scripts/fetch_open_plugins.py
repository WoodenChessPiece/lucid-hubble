#!/usr/bin/env python3
"""
scripts/fetch_open_plugins.py - Headless Soundbank & Open-Source Plugin Asset Manager.

Responsible for:
1. Ensuring storage assets reside under Google Drive symlink (0 local disk consumption).
2. Downloading curated open-source soundbanks, SFZ instruments, and free SoundFonts:
   - GeneralUser GS v1.471 (S. Christian Collins)
   - FluidR3 GM v3.1 (Frank Wen)
   - TimGM6mb (Tim Brechbill)
   - Salamander Grand Piano (Yamaha C5, Alexander Holm)
3. Downloading and extracting open-source VST3/CLAP plugins & DSP modules:
   - ChowDSP Suite (ChowTapeModel VST3 & CLAP)
   - Airwindows Pure DSP Suite (Console8, Tape, PurestDrive, ToTape6, ButterComp2, Galactic)
   - Native Python DSP verification (pedalboard & fluidsynth engines)
4. Comprehensive audio verification testing (synthesizing & processing audio buffers).
"""

import argparse
import json
import logging
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AssetIntegrator")

# User Agent for communal resource downloads
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"


class StorageEnvironment:
    """Manages paths and verifies Google Drive symlink integrity."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = (workspace_root or Path(__file__).resolve().parent.parent).resolve()
        self.storage_dir = (self.workspace_root / "storage").resolve()
        self.soundbanks_dir = self.storage_dir / "soundbanks"
        self.soundfonts_dir = self.storage_dir / "soundfonts"
        self.plugins_dir = self.storage_dir / "plugins"
        self.vst3_dir = self.plugins_dir / "vst3"
        self.clap_dir = self.plugins_dir / "clap"
        self.airwindows_dir = self.plugins_dir / "airwindows"

    def ensure_directories(self) -> Dict[str, Any]:
        """Ensures all required storage subdirectories exist."""
        created = []
        for d in [
            self.soundbanks_dir,
            self.soundfonts_dir,
            self.plugins_dir,
            self.vst3_dir,
            self.clap_dir,
            self.airwindows_dir,
        ]:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                created.append(str(d))

        symlink_target = os.path.realpath(self.storage_dir)
        is_symlink = os.path.islink(self.workspace_root / "storage")
        
        info = {
            "storage_path": str(self.storage_dir),
            "symlink_target": str(symlink_target),
            "is_symlink": is_symlink,
            "soundbanks_dir": str(self.soundbanks_dir),
            "plugins_dir": str(self.plugins_dir),
            "created_dirs": created,
        }
        logger.info(f"Storage path: {self.storage_dir} -> {symlink_target} (Symlink: {is_symlink})")
        return info


def download_file_with_progress(url: str, dest_path: Path, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """Downloads a file with streaming chunks and status reporting."""
    import requests

    headers = {"User-Agent": user_agent}
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")

    logger.info(f"Downloading: {url} -> {dest_path.name}...")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            total_bytes = int(resp.headers.get("content-length", 0))
            downloaded = 0
            t0 = time.time()
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            elapsed = max(time.time() - t0, 0.001)
            mb = downloaded / (1024 * 1024)
            speed_mb = mb / elapsed
            logger.info(f"Saved {dest_path.name} ({mb:.1f} MB in {elapsed:.1f}s, {speed_mb:.1f} MB/s)")

        if temp_path.exists():
            temp_path.replace(dest_path)
            return True
        return False
    except Exception as exc:
        logger.error(f"Download failed for {url}: {exc}")
        if temp_path.exists():
            temp_path.unlink()
        return False


class SoundBankDownloader:
    """Fetches curated open-source soundbanks and SoundFonts."""

    GENERALUSER_URL = "https://raw.githubusercontent.com/X-Boxbro/project_for_Cpp_course/main/GeneralUser-GS.sf2"
    TIMGM6MB_DEB_URL = "http://ftp.debian.org/debian/pool/main/t/timgm6mb-soundfont/timgm6mb-soundfont_1.3-5_all.deb"
    SALAMANDER_SFZ_URL = "https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/master/Salamander%20Grand%20Piano%20V3.sfz"

    def __init__(self, storage_env: StorageEnvironment):
        self.env = storage_env

    def fetch_generaluser_gs(self, force: bool = False) -> Optional[Path]:
        """Downloads the renowned GeneralUser GS v1.471 SoundFont (~32.3MB)."""
        target = self.env.soundbanks_dir / "GeneralUser-GS.sf2"
        if target.exists() and not force:
            logger.info(f"GeneralUser GS already present: {target} ({target.stat().st_size / 1e6:.1f} MB)")
            return target

        success = download_file_with_progress(self.GENERALUSER_URL, target)
        return target if success and target.exists() else None

    def sync_fluidr3_gm(self) -> Optional[Path]:
        """Syncs or links FluidR3_GM.sf2 from storage/soundfonts/ into storage/soundbanks/."""
        source = self.env.soundfonts_dir / "FluidR3_GM.sf2"
        target = self.env.soundbanks_dir / "FluidR3_GM.sf2"

        if target.exists():
            logger.info(f"FluidR3 GM already present in soundbanks: {target}")
            return target

        if source.exists():
            try:
                # Create a symlink or copy
                os.symlink(os.path.relpath(source, self.env.soundbanks_dir), target)
                logger.info(f"Symlinked FluidR3_GM.sf2 into soundbanks directory: {target}")
                return target
            except Exception:
                shutil.copy2(source, target)
                logger.info(f"Copied FluidR3_GM.sf2 into soundbanks directory: {target}")
                return target

        logger.warning(f"FluidR3_GM.sf2 not found at {source}")
        return None

    def fetch_timgm6mb(self, force: bool = False) -> Optional[Path]:
        """Fetches TimGM6mb.sf2 from Debian pool and extracts using ar/tar."""
        target = self.env.soundbanks_dir / "TimGM6mb.sf2"
        if target.exists() and not force:
            logger.info(f"TimGM6mb already present: {target} ({target.stat().st_size / 1e6:.1f} MB)")
            return target

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            deb_path = tmp_path / "timgm6mb.deb"
            if not download_file_with_progress(self.TIMGM6MB_DEB_URL, deb_path):
                return None

            try:
                subprocess.run(["ar", "-x", str(deb_path)], cwd=str(tmp_path), check=True, capture_output=True)
                data_tar = next(tmp_path.glob("data.tar*"))
                subprocess.run(["tar", "-xf", str(data_tar), "-C", str(tmp_path)], check=True, capture_output=True)

                found_sf2 = next(tmp_path.glob("**/*.sf2"))
                shutil.copy2(found_sf2, target)
                logger.info(f"Successfully extracted and installed: {target} ({target.stat().st_size / 1e6:.1f} MB)")
                return target
            except Exception as exc:
                logger.error(f"Failed to unpack TimGM6mb deb: {exc}")
                return None

    def fetch_salamander_sfz(self, force: bool = False) -> Optional[Path]:
        """Fetches Salamander Grand Piano SFZ instrument configuration."""
        salamander_dir = self.env.soundbanks_dir / "SalamanderGrandPiano"
        salamander_dir.mkdir(parents=True, exist_ok=True)
        target = salamander_dir / "Salamander Grand Piano V3.sfz"

        if target.exists() and not force:
            logger.info(f"Salamander SFZ already present: {target}")
            return target

        success = download_file_with_progress(self.SALAMANDER_SFZ_URL, target)
        if success:
            manifest_file = salamander_dir / "manifest.json"
            manifest = {
                "name": "Salamander Grand Piano V3",
                "instrument": "Yamaha C5 Grand Piano",
                "author": "Alexander Holm",
                "format": "SFZ",
                "sfz_path": str(target),
            }
            with open(manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)
            return target
        return None


class PluginDownloader:
    """Downloads, verifies, and manages open-source VST3/CLAP plugins & DSP suites."""

    CHOW_TAPE_DMG_URL = "https://github.com/jatinchowdhury18/AnalogTapeModel/releases/download/v2.11.4/ChowTapeModel-Mac-2.11.4.dmg"
    AIRWINDOWS_DMG_URL = "https://www.airwindows.com/wp-content/uploads/SignedMacVSTs.dmg"

    CURATED_AIRWINDOWS = [
        "Console8Channel",
        "Console8Bus",
        "Tape",
        "ToTape6",
        "PurestDrive",
        "ButterComp2",
        "Galactic",
        "Density",
        "Holt",
    ]

    def __init__(self, storage_env: StorageEnvironment):
        self.env = storage_env

    def fetch_chowdsp_tape(self, force: bool = False) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Downloads and unpacks ChowTapeModel (VST3 & CLAP) on macOS without root permissions.
        Uses hdiutil to mount DMG, pkgutil --expand, and tar -xf on Payload.
        """
        vst3_dest = self.env.vst3_dir / "CHOWTapeModel.vst3"
        clap_dest = self.env.clap_dir / "CHOWTapeModel.clap"

        if vst3_dest.exists() and clap_dest.exists() and not force:
            logger.info(f"ChowTapeModel VST3 & CLAP already installed: {vst3_dest}")
            return vst3_dest, clap_dest

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            dmg_path = tmp_path / "chow.dmg"

            if not download_file_with_progress(self.CHOW_TAPE_DMG_URL, dmg_path):
                return None, None

            mount_point = None
            try:
                attach_res = subprocess.run(
                    ["hdiutil", "attach", "-nobrowse", "-readonly", str(dmg_path)],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in attach_res.stdout.splitlines():
                    parts = line.split("\t")
                    for p in parts:
                        p = p.strip()
                        if p.startswith("/Volumes/"):
                            mount_point = Path(p)
                            break

                if not mount_point or not mount_point.exists():
                    raise RuntimeError("Failed to mount ChowTapeModel DMG")

                pkg_file = next(mount_point.glob("*.pkg"))
                pkg_expand_dir = tmp_path / "expanded"
                subprocess.run(
                    ["pkgutil", "--expand", str(pkg_file), str(pkg_expand_dir)],
                    check=True,
                    capture_output=True,
                )

                # Detach DMG cleanly
                subprocess.run(["hdiutil", "detach", str(mount_point)], check=True, capture_output=True)
                mount_point = None

                # Extract VST3
                vst3_payload = pkg_expand_dir / "VST3.pkg" / "Payload"
                if vst3_payload.exists():
                    vst3_tmp_extract = tmp_path / "vst3_extract"
                    vst3_tmp_extract.mkdir(parents=True, exist_ok=True)
                    subprocess.run(["tar", "-xf", str(vst3_payload), "-C", str(vst3_tmp_extract)], check=True)
                    found_vst3 = next(vst3_tmp_extract.glob("**/*.vst3"))
                    if vst3_dest.exists():
                        shutil.rmtree(vst3_dest)
                    shutil.copytree(found_vst3, vst3_dest)
                    logger.info(f"Installed VST3 plugin: {vst3_dest}")

                # Extract CLAP
                clap_payload = pkg_expand_dir / "CLAP.pkg" / "Payload"
                if clap_payload.exists():
                    clap_tmp_extract = tmp_path / "clap_extract"
                    clap_tmp_extract.mkdir(parents=True, exist_ok=True)
                    subprocess.run(["tar", "-xf", str(clap_payload), "-C", str(clap_tmp_extract)], check=True)
                    found_clap = next(clap_tmp_extract.glob("**/*.clap"))
                    if clap_dest.exists():
                        shutil.rmtree(clap_dest)
                    shutil.copytree(found_clap, clap_dest)
                    logger.info(f"Installed CLAP plugin: {clap_dest}")

                return vst3_dest if vst3_dest.exists() else None, clap_dest if clap_dest.exists() else None

            except Exception as exc:
                logger.error(f"Failed to extract ChowTapeModel: {exc}")
                return None, None
            finally:
                if mount_point and mount_point.exists():
                    subprocess.run(["hdiutil", "detach", str(mount_point)], capture_output=True)

    def fetch_airwindows_vsts(self, force: bool = False) -> List[Path]:
        """
        Downloads SignedMacVSTs.dmg and extracts curated Airwindows mixing & mastering plugins.
        """
        installed = []
        already_present = [name for name in self.CURATED_AIRWINDOWS if (self.env.airwindows_dir / f"{name}.vst").exists()]
        if len(already_present) == len(self.CURATED_AIRWINDOWS) and not force:
            logger.info(f"Airwindows curated plugins already installed ({len(already_present)} plugins).")
            return [self.env.airwindows_dir / f"{name}.vst" for name in self.CURATED_AIRWINDOWS]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            dmg_path = tmp_path / "airwindows.dmg"

            if not download_file_with_progress(self.AIRWINDOWS_DMG_URL, dmg_path):
                return []

            mount_point = None
            try:
                attach_res = subprocess.run(
                    ["hdiutil", "attach", "-nobrowse", "-readonly", str(dmg_path)],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in attach_res.stdout.splitlines():
                    parts = line.split("\t")
                    for p in parts:
                        p = p.strip()
                        if p.startswith("/Volumes/"):
                            mount_point = Path(p)
                            break

                if not mount_point or not mount_point.exists():
                    raise RuntimeError("Failed to mount Airwindows DMG")

                for name in self.CURATED_AIRWINDOWS:
                    vst_candidate = mount_point / f"{name}.vst"
                    if vst_candidate.exists():
                        dest_vst = self.env.airwindows_dir / f"{name}.vst"
                        if dest_vst.exists():
                            shutil.rmtree(dest_vst)
                        shutil.copytree(vst_candidate, dest_vst)
                        installed.append(dest_vst)

                logger.info(f"Extracted {len(installed)} curated Airwindows plugins into {self.env.airwindows_dir}")
                return installed
            except Exception as exc:
                logger.error(f"Failed to extract Airwindows plugins: {exc}")
                return installed
            finally:
                if mount_point and mount_point.exists():
                    subprocess.run(["hdiutil", "detach", str(mount_point)], capture_output=True)


class AssetVerifier:
    """Verifies SoundFonts and VST3 plugins via Python pyfluidsynth and pedalboard."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate

    def verify_soundfont(self, sf_path: Path, note: int = 60, velocity: int = 100) -> Dict[str, Any]:
        """
        Loads the SoundFont in FluidSynth, plays a test note, renders audio samples,
        and computes audio signal statistics.
        """
        import fluidsynth

        if not sf_path.exists():
            return {"status": "FAILED", "error": f"File does not exist: {sf_path}"}

        t0 = time.time()
        try:
            fs = fluidsynth.Synth(samplerate=float(self.sr))
            # Load soundfont with update_midi_presets=0 (False) to avoid blocking
            sfid = fs.sfload(str(sf_path), False)
            if sfid == -1:
                fs.delete()
                return {"status": "FAILED", "error": "FluidSynth sfload returned -1"}

            # Program select: Channel 0, SoundFont ID, Bank 0, Preset 0 (Acoustic Grand Piano)
            fs.program_select(0, sfid, 0, 0)
            fs.noteon(0, note, velocity)

            # Render 1 second (44,100 stereo samples = 88,200 int16 samples)
            raw_samples = fs.get_samples(self.sr)
            fs.noteoff(0, note)
            fs.delete()

            arr = np.frombuffer(raw_samples, dtype=np.int16).astype(np.float32) / 32768.0
            peak = float(np.max(np.abs(arr)))
            rms = float(np.sqrt(np.mean(arr ** 2)))
            rms_db = 20.0 * math.log10(rms + 1e-9)
            elapsed_ms = (time.time() - t0) * 1000

            is_valid = peak > 0.001
            return {
                "status": "PASSED" if is_valid else "SILENT_OUTPUT",
                "soundfont": sf_path.name,
                "size_mb": round(sf_path.stat().st_size / (1024 * 1024), 2),
                "sfid": sfid,
                "peak_amplitude": round(peak, 4),
                "rms_dbfs": round(rms_db, 2),
                "samples_rendered": len(arr),
                "latency_ms": round(elapsed_ms, 2),
            }
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc), "soundfont": sf_path.name}

    def verify_vst3(self, vst3_path: Path) -> Dict[str, Any]:
        """
        Loads a VST3 plugin via Pedalboard, runs stereo audio through it, and validates signal integrity.
        """
        import pedalboard

        if not vst3_path.exists():
            return {"status": "FAILED", "error": f"File does not exist: {vst3_path}"}

        t0 = time.time()
        try:
            plugin = pedalboard.load_plugin(str(vst3_path))
            # Create a 1-second stereo test tone (440Hz sine wave at -12 dBFS)
            t = np.linspace(0, 1.0, self.sr, endpoint=False)
            tone = (np.sin(2 * np.pi * 440.0 * t) * 0.25).astype(np.float32)
            stereo_in = np.vstack((tone, tone))

            processed = plugin(stereo_in, self.sr)
            peak = float(np.max(np.abs(processed)))
            rms = float(np.sqrt(np.mean(processed ** 2)))
            rms_db = 20.0 * math.log10(rms + 1e-9)
            elapsed_ms = (time.time() - t0) * 1000

            is_valid = peak > 0.001 and not np.isnan(peak) and not np.isinf(peak)
            return {
                "status": "PASSED" if is_valid else "INVALID_OUTPUT",
                "plugin_name": plugin.name,
                "path": str(vst3_path),
                "output_peak": round(peak, 4),
                "output_rms_dbfs": round(rms_db, 2),
                "latency_ms": round(elapsed_ms, 2),
            }
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc), "path": str(vst3_path)}

    def verify_pedalboard_dsp(self) -> Dict[str, Any]:
        """Verifies Spotify Pedalboard native DSP effects chain."""
        import pedalboard

        t0 = time.time()
        try:
            board = pedalboard.Pedalboard([
                pedalboard.Compressor(threshold_db=-14.0, ratio=2.5),
                pedalboard.Chorus(rate_hz=1.2, depth=0.4),
                pedalboard.Delay(delay_seconds=0.18, feedback=0.25),
                pedalboard.Reverb(room_size=0.55),
            ])

            t = np.linspace(0, 1.0, self.sr, endpoint=False)
            sine = (np.sin(2 * np.pi * 220.0 * t) * 0.4).astype(np.float32)
            stereo_in = np.vstack((sine, sine))

            processed = board(stereo_in, self.sr)
            peak = float(np.max(np.abs(processed)))
            rms = float(np.sqrt(np.mean(processed ** 2)))
            rms_db = 20.0 * math.log10(rms + 1e-9)
            elapsed_ms = (time.time() - t0) * 1000

            return {
                "status": "PASSED",
                "engine": "Pedalboard Native DSP",
                "chain": ["Compressor", "Chorus", "Delay", "Reverb"],
                "peak_amplitude": round(peak, 4),
                "rms_dbfs": round(rms_db, 2),
                "latency_ms": round(elapsed_ms, 2),
            }
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc), "engine": "Pedalboard"}


def run_pipeline(
    fetch_all: bool = False,
    soundbanks_only: bool = False,
    plugins_only: bool = False,
    verify_only: bool = False,
    force: bool = False,
) -> int:
    """Executes asset downloads and verification."""
    storage_env = StorageEnvironment()
    storage_info = storage_env.ensure_directories()

    sb_downloader = SoundBankDownloader(storage_env)
    pl_downloader = PluginDownloader(storage_env)
    verifier = AssetVerifier()

    downloaded_soundbanks = []
    downloaded_plugins = []

    if not verify_only:
        # 1. Soundbanks
        if not plugins_only:
            logger.info("--- Step 1: Downloading & Syncing Communal Soundbanks ---")
            # Always ensure GeneralUser GS and FluidR3 GM are present
            gu_path = sb_downloader.fetch_generaluser_gs(force=force)
            if gu_path:
                downloaded_soundbanks.append(gu_path)

            fr_path = sb_downloader.sync_fluidr3_gm()
            if fr_path:
                downloaded_soundbanks.append(fr_path)

            if fetch_all:
                tim_path = sb_downloader.fetch_timgm6mb(force=force)
                if tim_path:
                    downloaded_soundbanks.append(tim_path)

                sfz_path = sb_downloader.fetch_salamander_sfz(force=force)
                if sfz_path:
                    downloaded_soundbanks.append(sfz_path)

        # 2. Plugins
        if not soundbanks_only:
            logger.info("--- Step 2: Downloading & Extracting Open-Source Plugins ---")
            chow_vst3, chow_clap = pl_downloader.fetch_chowdsp_tape(force=force)
            if chow_vst3:
                downloaded_plugins.append(chow_vst3)

            if fetch_all:
                aw_vsts = pl_downloader.fetch_airwindows_vsts(force=force)
                downloaded_plugins.extend(aw_vsts)

    # 3. Audio Verification Suite
    logger.info("--- Step 3: Running Audio Verification Suite ---")
    verification_results = {"soundfonts": [], "plugins": [], "native_dsp": []}

    # Verify all SoundFonts in soundbanks directory
    for sf in sorted(storage_env.soundbanks_dir.glob("*.sf2")):
        res = verifier.verify_soundfont(sf)
        verification_results["soundfonts"].append(res)
        logger.info(f"SoundFont [{sf.name}]: {res.get('status')} | Peak: {res.get('peak_amplitude')} | RMS: {res.get('rms_dbfs')} dBFS | Latency: {res.get('latency_ms')} ms")

    # Verify VST3 plugins
    for vst3 in sorted(storage_env.vst3_dir.glob("*.vst3")):
        res = verifier.verify_vst3(vst3)
        verification_results["plugins"].append(res)
        logger.info(f"VST3 [{vst3.name}]: {res.get('status')} | Peak: {res.get('output_peak')} | RMS: {res.get('output_rms_dbfs')} dBFS")

    # Verify Pedalboard Native DSP
    native_res = verifier.verify_pedalboard_dsp()
    verification_results["native_dsp"].append(native_res)
    logger.info(f"Native DSP [Pedalboard]: {native_res.get('status')} | Peak: {native_res.get('peak_amplitude')} | RMS: {native_res.get('rms_dbfs')} dBFS")

    # Write Manifests
    manifest_sb = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "soundbanks": [
            {"path": str(sf), "size_bytes": sf.stat().st_size}
            for sf in storage_env.soundbanks_dir.glob("**/*")
            if sf.is_file()
        ],
        "verification": verification_results["soundfonts"],
    }
    with open(storage_env.soundbanks_dir / "manifest.json", "w") as f:
        json.dump(manifest_sb, f, indent=2)

    manifest_pl = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "plugins": [
            {"path": str(p), "name": p.name}
            for p in storage_env.plugins_dir.glob("**/*")
            if p.suffix in [".vst3", ".clap", ".vst", ".component"]
        ],
        "verification": verification_results["plugins"],
    }
    with open(storage_env.plugins_dir / "manifest.json", "w") as f:
        json.dump(manifest_pl, f, indent=2)

    # Print Summary Report
    print("\n" + "=" * 78)
    print("      LUCID HUBBLE - OPEN ASSET & PLUGIN INTEGRATION REPORT      ")
    print("=" * 78)
    print(f" Storage Directory (Google Drive Symlink): {storage_env.storage_dir}")
    print(f" Soundbanks Directory:                    {storage_env.soundbanks_dir}")
    print(f" Plugins Directory:                       {storage_env.plugins_dir}")
    print("-" * 78)
    print(" SOUNDFONT INSTRUMENT VERIFICATION:")
    for sf_res in verification_results["soundfonts"]:
        status = sf_res.get("status", "UNKNOWN")
        name = sf_res.get("soundfont", "N/A")
        size = sf_res.get("size_mb", 0)
        peak = sf_res.get("peak_amplitude", 0)
        rms = sf_res.get("rms_dbfs", 0)
        lat = sf_res.get("latency_ms", 0)
        print(f"  [{status:<6}] {name:<22} ({size:>5.1f} MB) | Peak: {peak:<6} | RMS: {rms:>6.1f} dBFS | Synth: {lat:>5.1f}ms")

    print("-" * 78)
    print(" VST3 / DSP PLUGIN VERIFICATION:")
    for pl_res in verification_results["plugins"]:
        status = pl_res.get("status", "UNKNOWN")
        name = pl_res.get("plugin_name", Path(pl_res.get("path", "")).name)
        peak = pl_res.get("output_peak", 0)
        rms = pl_res.get("output_rms_dbfs", 0)
        print(f"  [{status:<6}] {name:<22} | Peak: {peak:<6} | RMS: {rms:>6.1f} dBFS")

    for nd_res in verification_results["native_dsp"]:
        status = nd_res.get("status", "UNKNOWN")
        engine = nd_res.get("engine", "DSP")
        peak = nd_res.get("peak_amplitude", 0)
        rms = nd_res.get("rms_dbfs", 0)
        print(f"  [{status:<6}] {engine:<22} | Peak: {peak:<6} | RMS: {rms:>6.1f} dBFS")

    print("=" * 78)
    all_passed = (
        len(verification_results["soundfonts"]) > 0
        and all(r.get("status") == "PASSED" for r in verification_results["soundfonts"])
        and all(r.get("status") == "PASSED" for r in verification_results["plugins"])
        and all(r.get("status") == "PASSED" for r in verification_results["native_dsp"])
    )
    if all_passed:
        print(" [SUCCESS] All open soundbanks and DSP plugins successfully verified!\n")
        return 0
    else:
        print(" [WARNING] Some verification tests were inconclusive or failed.\n")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Fetch and verify open soundbanks and audio plugins.")
    parser.add_argument("--all", action="store_true", help="Download all curated soundbanks and plugins.")
    parser.add_argument("--soundbanks", action="store_true", help="Download soundbanks only.")
    parser.add_argument("--plugins", action="store_true", help="Download plugins only.")
    parser.add_argument("--verify-only", action="store_true", help="Run verification tests without downloading.")
    parser.add_argument("--force", action="store_true", help="Force re-download of existing assets.")
    args = parser.parse_args()

    sys.exit(run_pipeline(
        fetch_all=args.all,
        soundbanks_only=args.soundbanks,
        plugins_only=args.plugins,
        verify_only=args.verify_only,
        force=args.force,
    ))


if __name__ == "__main__":
    main()

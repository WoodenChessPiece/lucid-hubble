"""
tests/test_fetch_open_plugins.py - Verification suite for Open Asset & Plugin Integrator.
"""

import os
import unittest
from pathlib import Path
import numpy as np

from scripts.fetch_open_plugins import (
    StorageEnvironment,
    SoundBankDownloader,
    PluginDownloader,
    AssetVerifier,
)


class TestFetchOpenPlugins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.workspace_root = Path(__file__).resolve().parent.parent
        cls.storage_env = StorageEnvironment(cls.workspace_root)
        cls.storage_info = cls.storage_env.ensure_directories()
        cls.verifier = AssetVerifier(sample_rate=44100)

    def test_storage_symlink_and_directories(self):
        """Verify storage directories exist and are properly linked to Google Drive."""
        self.assertTrue(self.storage_env.storage_dir.exists())
        self.assertTrue(self.storage_env.soundbanks_dir.exists())
        self.assertTrue(self.storage_env.plugins_dir.exists())
        self.assertTrue(self.storage_env.vst3_dir.exists())
        self.assertTrue(self.storage_env.clap_dir.exists())
        self.assertTrue(self.storage_env.airwindows_dir.exists())

        # Verify it resolves to Google Drive cloud storage (0 local disk usage)
        real_target = os.path.realpath(self.storage_env.storage_dir)
        self.assertTrue("Google" in real_target or "CloudStorage" in real_target or self.storage_info["is_symlink"])

    def test_generaluser_gs_verification(self):
        """Verify GeneralUser GS v1.471 SoundFont loads and synthesizes valid audio."""
        gu_path = self.storage_env.soundbanks_dir / "GeneralUser-GS.sf2"
        self.assertTrue(gu_path.exists(), f"GeneralUser-GS.sf2 not found at {gu_path}")
        self.assertGreater(gu_path.stat().st_size, 30_000_000)

        res = self.verifier.verify_soundfont(gu_path, note=60, velocity=100)
        self.assertEqual(res.get("status"), "PASSED")
        self.assertGreater(res.get("peak_amplitude", 0), 0.005)
        self.assertLess(res.get("rms_dbfs", 0), 0.0)
        self.assertEqual(res.get("samples_rendered"), 88200)

    def test_fluidr3_gm_verification(self):
        """Verify FluidR3 GM SoundFont loads and synthesizes valid audio."""
        fr_path = self.storage_env.soundbanks_dir / "FluidR3_GM.sf2"
        self.assertTrue(fr_path.exists(), f"FluidR3_GM.sf2 not found at {fr_path}")

        res = self.verifier.verify_soundfont(fr_path, note=60, velocity=100)
        self.assertEqual(res.get("status"), "PASSED")
        self.assertGreater(res.get("peak_amplitude", 0), 0.005)

    def test_timgm6mb_verification(self):
        """Verify TimGM6mb SoundFont loads and synthesizes valid audio."""
        tim_path = self.storage_env.soundbanks_dir / "TimGM6mb.sf2"
        if tim_path.exists():
            res = self.verifier.verify_soundfont(tim_path, note=60, velocity=100)
            self.assertEqual(res.get("status"), "PASSED")
            self.assertGreater(res.get("peak_amplitude", 0), 0.005)

    def test_chowdsp_vst3_audio_processing(self):
        """Verify CHOWTapeModel VST3 plugin loads via Pedalboard and alters audio dynamically."""
        vst3_path = self.storage_env.vst3_dir / "CHOWTapeModel.vst3"
        self.assertTrue(vst3_path.exists(), f"CHOWTapeModel.vst3 not found at {vst3_path}")

        res = self.verifier.verify_vst3(vst3_path)
        self.assertEqual(res.get("status"), "PASSED")
        self.assertGreater(res.get("output_peak", 0), 0.05)
        self.assertIn("Tape", res.get("plugin_name", ""))

    def test_pedalboard_native_dsp_suite(self):
        """Verify Spotify Pedalboard DSP chain handles audio processing accurately."""
        res = self.verifier.verify_pedalboard_dsp()
        self.assertEqual(res.get("status"), "PASSED")
        self.assertGreater(res.get("peak_amplitude", 0), 0.01)
        self.assertIn("Compressor", res.get("chain", []))

    def test_manifest_generation(self):
        """Verify manifest.json files exist in soundbanks and plugins directories."""
        sb_manifest = self.storage_env.soundbanks_dir / "manifest.json"
        pl_manifest = self.storage_env.plugins_dir / "manifest.json"
        self.assertTrue(sb_manifest.exists())
        self.assertTrue(pl_manifest.exists())


if __name__ == "__main__":
    unittest.main()

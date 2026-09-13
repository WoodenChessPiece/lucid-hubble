import unittest
import numpy as np
import scipy.signal as signal
from src.engine.spatial_reverb import (
    EarlyReflections,
    AbbeyRoadFilter,
    DattorroReverbEngine,
    SidechainDucker,
    StudioSpatialReverb
)

class TestSpatialReverb(unittest.TestCase):
    def test_early_reflections(self):
        fs = 44100
        er = EarlyReflections(sample_rate=fs)
        x = np.zeros(fs, dtype=np.float32)
        x[0] = 1.0  # impulse
        out = er.process(x)
        self.assertEqual(out.shape, (fs, 2))
        self.assertTrue(np.any(out[:, 0] > 0))
        self.assertTrue(np.any(out[:, 1] > 0))
        self.assertFalse(np.array_equal(out[:, 0], out[:, 1]))

    def test_abbey_road_filter(self):
        fs = 44100
        filt = AbbeyRoadFilter(sample_rate=fs, hp_cutoff=600.0, lp_cutoff=10000.0)
        w, h_hp = signal.freqz(filt.b_hp, filt.a_hp, worN=[100, 600], fs=fs)
        w, h_lp = signal.freqz(filt.b_lp, filt.a_lp, worN=[10000, 18000], fs=fs)
        
        # 600 Hz cutoff should be ~ -3.01 dB
        gain_600 = 20 * np.log10(abs(h_hp[1]))
        self.assertAlmostEqual(gain_600, -3.01, places=1)
        
        # 10 kHz cutoff should be ~ -3.01 dB
        gain_10k = 20 * np.log10(abs(h_lp[0]))
        self.assertAlmostEqual(gain_10k, -3.01, places=1)
        
        # Low-end rumble (<100Hz) should be strongly attenuated (> 25 dB)
        self.assertLess(20 * np.log10(abs(h_hp[0])), -25.0)

    def test_dattorro_decorrelation(self):
        fs = 44100
        datt = DattorroReverbEngine(sample_rate=fs, decay=0.8)
        impulse = np.zeros(fs * 2, dtype=np.float32)
        impulse[0] = 1.0
        out = datt.process(impulse)
        self.assertEqual(out.shape, (fs * 2, 2))
        
        # Stereo tail cross-correlation must be very low (< 0.25)
        tail = out[4000:]
        rho = np.corrcoef(tail[:, 0], tail[:, 1])[0, 1]
        self.assertLess(abs(rho), 0.25)

    def test_sidechain_ducker(self):
        fs = 44100
        ducker = SidechainDucker(sample_rate=fs, threshold_db=-20.0, duck_db=6.0, attack_ms=10.0, release_ms=200.0)
        t = np.linspace(0, 1.5, int(fs * 1.5), endpoint=False)
        burst = np.zeros_like(t, dtype=np.float32)
        burst[:int(fs * 0.5)] = 0.5 * np.sin(2.0 * np.pi * 440.0 * t[:int(fs * 0.5)]) # -6 dBFS tone
        dummy_wet = np.ones((len(t), 2), dtype=np.float32)
        
        ducked, gain = ducker.process(burst, dummy_wet)
        min_gain_db = 20.0 * np.log10(np.min(gain))
        end_gain_db = 20.0 * np.log10(gain[-1])
        
        # Assert ~6 dB ducking during active tone
        self.assertTrue(-6.5 <= min_gain_db <= -5.5)
        # Assert recovery to ~0 dB after release
        self.assertGreaterEqual(end_gain_db, -0.1)

    def test_studio_spatial_reverb_master(self):
        fs = 44100
        rev = StudioSpatialReverb(sample_rate=fs, rt60_s=2.0, abbey_road=True, ducking=True, duck_db=6.0)
        x = np.sin(2 * np.pi * 440 * np.linspace(0, 1, fs, endpoint=False))
        out, stems = rev.process(x)
        self.assertEqual(out.shape, (fs, 2))
        self.assertIn('early_ref', stems)
        self.assertIn('late_wet', stems)
        self.assertIn('ducked_wet', stems)
        self.assertTrue(np.all(np.isfinite(out)))

    def test_studio_spatial_reverb_aux_send(self):
        fs = 44100
        rev = StudioSpatialReverb(
            sample_rate=fs,
            rt60_s=2.2,
            abbey_road=True,
            ducking=True,
            duck_db=6.0,
            hp_cutoff=600.0,
            lp_cutoff=8000.0
        )
        t = np.linspace(0, 1.0, fs, endpoint=False)
        send_signal = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        sidechain_key = np.zeros(fs, dtype=np.float32)
        sidechain_key[:int(fs * 0.3)] = 0.8  # Key active for first 300ms

        wet_return = rev.process_aux(send_signal, sidechain_key=sidechain_key)
        self.assertEqual(wet_return.shape, (fs, 2))
        self.assertTrue(np.all(np.isfinite(wet_return)))

        # Verify low frequency attenuation: 60 Hz tone into aux send should be strongly rejected
        sub_tone = np.sin(2 * np.pi * 60 * t).astype(np.float32)
        wet_sub = rev.process_aux(sub_tone)
        # Compare RMS of mid tone (1kHz) vs sub tone (60Hz)
        rms_sub = np.sqrt(np.mean(wet_sub**2))
        wet_mid = rev.process_aux(send_signal)
        rms_mid = np.sqrt(np.mean(wet_mid**2))
        self.assertLess(rms_sub, rms_mid * 0.1)

if __name__ == '__main__':
    unittest.main()

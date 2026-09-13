"""
src/engine/spatial_reverb.py - Professional Studio-Quality Spatial Reverb & Acoustics Engine
Implements:
1. Early Reflections: Haas integration window (10-35 ms) specular reflections
2. Abbey Road Trick: HPF 600 Hz / LPF 10 kHz 2nd-order Butterworth pre-filtering
3. Jon Dattorro (1997) Figure-Eight Plate Reverberator with LFO modulation and HF damping
4. Dynamic Sidechain Ducker: 4-8 dB gain reduction during active phrases, blooming in pauses
"""

import numpy as np
import scipy.signal as signal
from typing import Tuple, Dict, Optional


class EarlyReflections:
    """
    Multi-Tap Specular Early Reflections Generator based on Room Boundary Ray-Tracing.
    Operates within the Haas Integration Window (10 - 35 ms) using incommensurate prime
    delay times to prevent comb-filtering resonance.
    """
    def __init__(self, sample_rate: int = 44100):
        self.fs = sample_rate
        # Tap specifications: (Delay in ms, Linear Gain, Azimuth Pan [-1.0 Left to +1.0 Right])
        self.taps = [
            (11.3, 0.80, -0.75),  # Floor reflection
            (15.7, 0.70,  0.65),  # Ceiling reflection
            (21.1, 0.62, -0.40),  # Near side wall
            (26.8, 0.53,  0.80),  # Far side wall
            (32.4, 0.44, -0.85),  # Rear corner reflection
            (38.2, 0.36,  0.30),  # Back wall diffuse bounce
        ]

    def process(self, x: np.ndarray) -> np.ndarray:
        """
        Processes mono (N,) or stereo (N, 2) input into early specular stereo reflections.
        Returns: (N, 2) float32 numpy array.
        """
        if x.ndim == 2:
            mono_in = 0.5 * (x[:, 0] + x[:, 1])
        else:
            mono_in = x

        N = len(mono_in)
        out_l = np.zeros(N, dtype=np.float32)
        out_r = np.zeros(N, dtype=np.float32)

        for delay_ms, gain, pan in self.taps:
            d_samples = int(np.round(delay_ms * 1e-3 * self.fs))
            if d_samples >= N:
                continue

            # Constant-power panning (sine/cosine law)
            theta = (pan + 1.0) * (np.pi / 4.0)  # Maps -1..+1 to 0..pi/2
            gain_l = gain * np.cos(theta)
            gain_r = gain * np.sin(theta)

            delayed = np.zeros(N, dtype=np.float32)
            delayed[d_samples:] = mono_in[:N - d_samples]

            out_l += gain_l * delayed
            out_r += gain_r * delayed

        return np.stack([out_l, out_r], axis=-1)


class AbbeyRoadFilter:
    """
    The Legendary Abbey Road Reverb Send Pre-Filter:
    - High-Pass Filter at 600 Hz (12 dB/oct Butterworth): Eliminates low-end boom and mud.
    - Low-Pass Filter at 10 kHz (12 dB/oct Butterworth): Tames harsh sibilance and splash.
    """
    def __init__(self, sample_rate: int = 44100, hp_cutoff: float = 600.0, lp_cutoff: float = 10000.0):
        self.fs = sample_rate
        self.hp_cutoff = hp_cutoff
        self.lp_cutoff = lp_cutoff

        nyquist = 0.5 * sample_rate
        # 2nd-order Butterworth IIR filters
        self.b_hp, self.a_hp = signal.butter(2, hp_cutoff / nyquist, btype='highpass')
        self.b_lp, self.a_lp = signal.butter(2, lp_cutoff / nyquist, btype='lowpass')

    def process(self, x: np.ndarray) -> np.ndarray:
        """
        Filters input signal x along time axis.
        """
        y = signal.lfilter(self.b_hp, self.a_hp, x, axis=0)
        y = signal.lfilter(self.b_lp, self.a_lp, y, axis=0)
        return y.astype(np.float32)


class DattorroReverbEngine:
    """
    High-Fidelity Jon Dattorro (1997) Figure-Eight Plate Reverberator.
    Features:
    - Pre-delay buffer
    - High-frequency bandwidth limiting one-pole filter
    - 4 series input all-pass diffusers
    - Dual cross-coupled feedback tanks (Left/Right)
    - Sinusoidal LFO delay modulation to prevent flutter echoes and limit cycles
    - In-loop one-pole high-frequency damping filters
    - 7-tap cross-summed decorrelated stereo output matrix
    """
    def __init__(self, sample_rate: int = 44100, predelay_ms: float = 25.0,
                 bandwidth: float = 0.999, damping: float = 0.30, decay: float = 0.82,
                 diff_in1: float = 0.75, diff_in2: float = 0.625,
                 decay_diff1: float = 0.70, decay_diff2: float = 0.50,
                 mod_depth_samples: float = 10.0, mod_rate_hz: float = 1.0):
        self.fs = sample_rate
        scale = sample_rate / 29761.0  # Dattorro original design was at 29761 Hz

        self.predelay_samples = int(np.round(predelay_ms * 1e-3 * sample_rate))
        self.bandwidth = float(bandwidth)
        self.damping = float(damping)
        self.decay = float(decay)
        self.diff_in1 = float(diff_in1)
        self.diff_in2 = float(diff_in2)
        self.decay_diff1 = float(decay_diff1)
        self.decay_diff2 = float(decay_diff2)
        self.mod_depth = float(mod_depth_samples * scale)
        self.mod_rate = float(mod_rate_hz)

        # Scaled delay lengths for input diffusers
        self.d_in = [
            int(np.round(142 * scale)),
            int(np.round(107 * scale)),
            int(np.round(379 * scale)),
            int(np.round(277 * scale))
        ]

        # Scaled delay lengths for Left Tank
        self.d_t1 = int(np.round(672 * scale))   # Modulated delay 1
        self.d_a1 = int(np.round(4453 * scale))  # Diffuser 1
        self.d_t2 = int(np.round(3720 * scale))  # Delay 2
        self.d_a2 = int(np.round(1800 * scale))  # Diffuser 2
        self.d_t3 = int(np.round(3163 * scale))  # Delay 3

        # Scaled delay lengths for Right Tank
        self.d_t4 = int(np.round(908 * scale))   # Modulated delay 4
        self.d_a3 = int(np.round(4217 * scale))  # Diffuser 3
        self.d_t5 = int(np.round(2656 * scale))  # Delay 5
        self.d_a4 = int(np.round(2705 * scale))  # Diffuser 4
        self.d_t6 = int(np.round(4401 * scale))  # Delay 6

        # Scaled Output Tap Offsets
        self.tap_L = [
            int(np.round(266 * scale)),
            int(np.round(2974 * scale)),
            int(np.round(1913 * scale)),
            int(np.round(1996 * scale)),
            int(np.round(1990 * scale)),
            int(np.round(187 * scale)),
            int(np.round(1066 * scale))
        ]
        self.tap_R = [
            int(np.round(353 * scale)),
            int(np.round(3627 * scale)),
            int(np.round(1228 * scale)),
            int(np.round(2673 * scale)),
            int(np.round(2111 * scale)),
            int(np.round(335 * scale)),
            int(np.round(121 * scale))
        ]

    def process(self, x: np.ndarray) -> np.ndarray:
        """
        Processes audio through the Dattorro figure-8 reverberator tank.
        Returns: (N, 2) stereo diffuse reverb wet tail.
        """
        if x.ndim == 2:
            mono_in = 0.5 * (x[:, 0] + x[:, 1])
        else:
            mono_in = x

        N = len(mono_in)

        # 1. Pre-Delay
        if self.predelay_samples > 0:
            pd_in = np.zeros(N, dtype=np.float32)
            if self.predelay_samples < N:
                pd_in[self.predelay_samples:] = mono_in[:N - self.predelay_samples]
        else:
            pd_in = mono_in.astype(np.float32)

        # 2. Bandwidth Low-Pass Filter: y[n] = (1 - B)*y[n-1] + B*x[n]
        bw_out = np.zeros(N, dtype=np.float32)
        bw = self.bandwidth
        b_val = 0.0
        for n in range(N):
            b_val = (1.0 - bw) * b_val + bw * pd_in[n]
            bw_out[n] = b_val

        # 3. Input All-Pass Diffusers (4 in series)
        def run_allpass(sig, D, g):
            w = np.zeros(N + D, dtype=np.float32)
            out = np.zeros(N, dtype=np.float32)
            for n in range(N):
                delayed = w[n]
                in_val = sig[n]
                w[n + D] = in_val + g * delayed
                out[n] = -g * in_val + delayed
            return out

        d1 = run_allpass(bw_out, self.d_in[0], self.diff_in1)
        d2 = run_allpass(d1, self.d_in[1], self.diff_in1)
        d3 = run_allpass(d2, self.d_in[2], self.diff_in2)
        diff_in = run_allpass(d3, self.d_in[3], self.diff_in2)

        # 4. Figure-Eight Dual Feedback Tank Loop
        pad = 128
        buf_t1 = np.zeros(self.d_t1 + pad, dtype=np.float32)
        buf_a1 = np.zeros(self.d_a1, dtype=np.float32)
        buf_t2 = np.zeros(self.d_t2, dtype=np.float32)
        buf_a2 = np.zeros(self.d_a2, dtype=np.float32)
        buf_t3 = np.zeros(self.d_t3, dtype=np.float32)

        buf_t4 = np.zeros(self.d_t4 + pad, dtype=np.float32)
        buf_a3 = np.zeros(self.d_a3, dtype=np.float32)
        buf_t5 = np.zeros(self.d_t5, dtype=np.float32)
        buf_a4 = np.zeros(self.d_a4, dtype=np.float32)
        buf_t6 = np.zeros(self.d_t6, dtype=np.float32)

        pt1 = pa1 = pt2 = pa2 = pt3 = 0
        pt4 = pa3 = pt5 = pa4 = pt6 = 0

        damp_l = 0.0
        damp_r = 0.0

        out_L = np.zeros(N, dtype=np.float32)
        out_R = np.zeros(N, dtype=np.float32)

        decay = self.decay
        damp = self.damping
        g_diff1 = self.decay_diff1
        g_diff2 = self.decay_diff2

        lfo_phase_l = 0.0
        lfo_phase_r = np.pi / 2.0  # 90-degree quadrature phase for maximum stereo decorrelation
        lfo_inc = 2.0 * np.pi * self.mod_rate / self.fs
        mod_depth = self.mod_depth

        len_t1 = len(buf_t1)
        len_t4 = len(buf_t4)

        tL = self.tap_L
        tR = self.tap_R

        for n in range(N):
            in_s = diff_in[n]

            # --- LEFT TANK PROCESSING ---
            s_l = in_s + decay * buf_t6[pt6]

            # Modulated Delay 1
            mod_offset_l = mod_depth * (0.5 + 0.5 * np.sin(lfo_phase_l))
            read_idx_l = int(pt1 - self.d_t1 - mod_offset_l) % len_t1
            val_t1 = buf_t1[read_idx_l]
            buf_t1[pt1] = s_l
            pt1 = (pt1 + 1) % len_t1

            # Diffuser 1 (allpass)
            delayed_a1 = buf_a1[pa1]
            w_a1 = val_t1 - g_diff1 * delayed_a1
            out_a1 = delayed_a1 + g_diff1 * w_a1
            buf_a1[pa1] = w_a1
            pa1 = (pa1 + 1) % self.d_a1

            # Delay Line 2
            val_t2 = buf_t2[pt2]
            buf_t2[pt2] = out_a1
            pt2 = (pt2 + 1) % self.d_t2

            # High-Frequency Damping 1 (one-pole low-pass)
            damp_l = (1.0 - damp) * val_t2 + damp * damp_l

            # Diffuser 2 (allpass)
            delayed_a2 = buf_a2[pa2]
            w_a2 = damp_l + g_diff2 * delayed_a2
            out_a2 = delayed_a2 - g_diff2 * w_a2
            buf_a2[pa2] = w_a2
            pa2 = (pa2 + 1) % self.d_a2

            # Delay Line 3
            val_t3 = buf_t3[pt3]
            buf_t3[pt3] = out_a2
            pt3 = (pt3 + 1) % self.d_t3

            # --- RIGHT TANK PROCESSING ---
            s_r = in_s + decay * buf_t3[pt3]

            # Modulated Delay 4
            mod_offset_r = mod_depth * (0.5 + 0.5 * np.sin(lfo_phase_r))
            read_idx_r = int(pt4 - self.d_t4 - mod_offset_r) % len_t4
            val_t4 = buf_t4[read_idx_r]
            buf_t4[pt4] = s_r
            pt4 = (pt4 + 1) % len_t4

            # Diffuser 3 (allpass)
            delayed_a3 = buf_a3[pa3]
            w_a3 = val_t4 - g_diff1 * delayed_a3
            out_a3 = delayed_a3 + g_diff1 * w_a3
            buf_a3[pa3] = w_a3
            pa3 = (pa3 + 1) % self.d_a3

            # Delay Line 5
            val_t5 = buf_t5[pt5]
            buf_t5[pt5] = out_a3
            pt5 = (pt5 + 1) % self.d_t5

            # High-Frequency Damping 2 (one-pole low-pass)
            damp_r = (1.0 - damp) * val_t5 + damp * damp_r

            # Diffuser 4 (allpass)
            delayed_a4 = buf_a4[pa4]
            w_a4 = damp_r + g_diff2 * delayed_a4
            out_a4 = delayed_a4 - g_diff2 * w_a4
            buf_a4[pa4] = w_a4
            pa4 = (pa4 + 1) % self.d_a4

            # Delay Line 6
            val_t6 = buf_t6[pt6]
            buf_t6[pt6] = out_a4
            pt6 = (pt6 + 1) % self.d_t6

            # Multi-Tap Output Summation
            out_L[n] = (buf_t5[(pt5 - tL[0]) % self.d_t5] +
                        buf_t5[(pt5 - tL[1]) % self.d_t5] -
                        buf_a4[(pa4 - tL[2]) % self.d_a4] +
                        buf_t6[(pt6 - tL[3]) % self.d_t6] -
                        buf_t2[(pt2 - tL[4]) % self.d_t2] -
                        buf_a2[(pa2 - tL[5]) % self.d_a2] -
                        buf_t3[(pt3 - tL[6]) % self.d_t3])

            out_R[n] = (buf_t2[(pt2 - tR[0]) % self.d_t2] +
                        buf_t2[(pt2 - tR[1]) % self.d_t2] -
                        buf_a2[(pa2 - tR[2]) % self.d_a2] +
                        buf_t3[(pt3 - tR[3]) % self.d_t3] -
                        buf_t5[(pt5 - tR[4]) % self.d_t5] -
                        buf_a4[(pa4 - tR[5]) % self.d_a4] -
                        buf_t6[(pt6 - tR[6]) % self.d_t6])

            lfo_phase_l += lfo_inc
            lfo_phase_r += lfo_inc

        return np.stack([out_L, out_R], axis=-1)


class SidechainDucker:
    """
    Dynamic Sidechain Ducking Processor on Reverb Wet Bus.
    Monitors dry key input and ducks reverb return by duck_db (typically 4 - 8 dB)
    during active phrases, allowing the reverb to bloom during rests and pauses.
    """
    def __init__(self, sample_rate: int = 44100, threshold_db: float = -24.0,
                 duck_db: float = 6.0, attack_ms: float = 10.0, release_ms: float = 250.0):
        self.fs = sample_rate
        self.threshold_linear = 10.0 ** (threshold_db / 20.0)
        self.duck_db = duck_db

        # Exponential time constant coefficients
        self.alpha_attack = np.exp(-1.0 / (attack_ms * 1e-3 * sample_rate))
        self.alpha_release = np.exp(-1.0 / (release_ms * 1e-3 * sample_rate))

    def process(self, dry_signal: np.ndarray, wet_signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        dry_signal: (N,) mono or (N, 2) stereo input (Sidechain key)
        wet_signal: (N, 2) stereo reverb wet bus
        Returns:
            ducked_wet: (N, 2) attenuated wet signal
            gain_curve: (N,) linear gain reduction curve
        """
        if dry_signal.ndim == 2:
            dry_mono = 0.5 * (np.abs(dry_signal[:, 0]) + np.abs(dry_signal[:, 1]))
        else:
            dry_mono = np.abs(dry_signal)

        N = len(dry_mono)
        env = np.zeros(N, dtype=np.float32)
        curr_env = 0.0
        att = self.alpha_attack
        rel = self.alpha_release

        # Envelope follower with asymmetric attack/release ballistics
        for n in range(N):
            val = dry_mono[n]
            if val > curr_env:
                curr_env = att * curr_env + (1.0 - att) * val
            else:
                curr_env = rel * curr_env + (1.0 - rel) * val
            env[n] = curr_env

        # Compute logarithmic overshoot and gain reduction in dB
        env_db = 20.0 * np.log10(np.maximum(env, 1e-5))
        thresh_db = 20.0 * np.log10(self.threshold_linear)
        overs_db = np.maximum(0.0, env_db - thresh_db)

        # Proportional attenuation capped at duck_db
        atten_db = np.minimum(self.duck_db, overs_db * 0.75)
        gain = 10.0 ** (-atten_db / 20.0)

        ducked_wet = wet_signal * gain[:, np.newaxis]
        return ducked_wet.astype(np.float32), gain.astype(np.float32)


class StudioSpatialReverb:
    """
    Complete Professional Studio Spatial Reverb Processor:
    - Early Reflections Generator (Haas specular geometry)
    - Abbey Road Send Pre-Filter (HPF 600 Hz / LPF 10 kHz)
    - Dattorro (1997) Algorithmic Plate Reverb Engine
    - Dynamic Sidechain Ducking Compressor
    - Master Dry/Wet Spatial Summer
    """
    def __init__(self, sample_rate: int = 44100, predelay_ms: float = 25.0,
                 rt60_s: float = 2.5, abbey_road: bool = True, ducking: bool = True,
                 duck_db: float = 6.0, attack_ms: float = 10.0, release_ms: float = 250.0,
                 er_level: float = 0.25, wet_level: float = 0.35, dry_level: float = 0.85):
        self.fs = sample_rate
        self.abbey_road_enabled = abbey_road
        self.ducking_enabled = ducking
        self.er_level = er_level
        self.wet_level = wet_level
        self.dry_level = dry_level

        # Map target RT60 (seconds) to Dattorro internal decay feedback gain
        decay = np.clip(0.5 + 0.12 * np.log(max(0.2, rt60_s)), 0.4, 0.94)

        self.er = EarlyReflections(sample_rate=sample_rate)
        self.filter = AbbeyRoadFilter(sample_rate=sample_rate) if abbey_road else None
        self.dattorro = DattorroReverbEngine(sample_rate=sample_rate, predelay_ms=predelay_ms, decay=decay)
        self.ducker = SidechainDucker(sample_rate=sample_rate, duck_db=duck_db,
                                      attack_ms=attack_ms, release_ms=release_ms) if ducking else None

    def process(self, x: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Processes input x through the complete spatial reverb pipeline.
        Returns:
            master_out: (N, 2) final master stereo audio array
            stems: dict containing individual audio stems for inspection
        """
        if x.ndim == 1:
            x_stereo = np.stack([x, x], axis=-1).astype(np.float32)
        else:
            x_stereo = x.astype(np.float32)

        # 1. Specular Early Reflections
        early_ref = self.er.process(x_stereo)

        # 2. Abbey Road Pre-Filtering on Send
        if self.abbey_road_enabled:
            send_signal = self.filter.process(x_stereo)
        else:
            send_signal = x_stereo

        # 3. Late Diffuse Reverb Tail (Dattorro Engine)
        late_wet = self.dattorro.process(send_signal)

        # 4. Sidechain Ducking
        if self.ducking_enabled:
            ducked_wet, gain_curve = self.ducker.process(x_stereo, late_wet)
        else:
            ducked_wet = late_wet
            gain_curve = np.ones(len(x_stereo), dtype=np.float32)

        # 5. Master Spatial Summer
        master_out = (self.dry_level * x_stereo +
                      self.er_level * early_ref +
                      self.wet_level * ducked_wet)

        return master_out, {
            'dry': x_stereo,
            'early_ref': early_ref,
            'late_wet': late_wet,
            'ducked_wet': ducked_wet,
            'gain_curve': gain_curve
        }

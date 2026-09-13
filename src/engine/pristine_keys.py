"""
src/engine/pristine_keys.py - Masterclass Acoustic Piano & Rhodes E-Piano DSP Engine

Implements:
1. Acoustic Grand Piano Physical Modeling:
   - Velocity-sensitive hammer strike transient with felt damping & keybed mechanical thump
   - String dispersion & inharmonicity: f_n = n * f_0 * sqrt(1 + B * n^2)
   - Dual-exponential decay (prompt sound vs aftersound horizontal/vertical string polarization)
   - Soundboard modal resonance filtering (80Hz, 140Hz, 260Hz, 480Hz)
   - Natural stereo imaging across keyboard register
2. Fender Rhodes Electric Piano Modeling:
   - Neoprene tine strike transient (high-frequency metallic ping)
   - 2-Operator FM sine modulation with velocity-dependent modulation index decay
   - Asymmetric variable-reluctance magnetic pickup saturation ('Bark')
   - Stereo suitcase optical tremolo / auto-pan
3. SoundFont Manager & Headless Integration:
   - Automated detection of FluidSynth CLI / libraries and SoundFont paths (Salamander Grand, Rhodes)
   - Seamless fallback to pure-Python PristineKeysEngine when SoundFonts are unavailable
"""

import os
import math
import shutil
import subprocess
import numpy as np
import scipy.signal as signal
from typing import List, Optional, Tuple, Dict, Any

SAMPLE_RATE = 44100


def midi_to_freq_pure(midi_pitch: int, a4_tuning: float = 440.0) -> float:
    """Exact equal-temperament frequency calculation without any arbitrary detuning."""
    return a4_tuning * (2.0 ** ((midi_pitch - 69.0) / 12.0))


class PristinePianoVoice:
    """
    Acoustic Grand Piano synthesis based on physical modeling principles:
    - Inharmonic string partials (dispersion equation)
    - Velocity-dependent hammer felt contact time and spectral brightness
    - Dual-exponential decay (prompt vs aftersound)
    - Soundboard modal resonances (2nd-order IIR peak filters)
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        # Soundboard modal resonance frequencies and Q factors
        self.soundboard_modes = [
            (80.0, 5.0, 0.18),    # Low body resonance
            (140.0, 7.0, 0.25),   # Lower rib/bridge mode
            (260.0, 8.0, 0.22),   # Soundboard diaphragmatic mode
            (480.0, 6.0, 0.15),   # Upper bridge transmission mode
        ]
        self._precompute_soundboard_filters()

    def _precompute_soundboard_filters(self):
        self.modal_filters = []
        for freq, q, gain in self.soundboard_modes:
            # Design 2nd-order IIR peak filter
            b, a = signal.iirpeak(freq, q, fs=self.sr)
            self.modal_filters.append((b, a, gain))

    def _generate_hammer_transient(self, duration_s: float, velocity: int) -> np.ndarray:
        """
        Velocity-sensitive hammer strike transient.
        High velocity = shorter contact duration, harder impact, brighter felt transient.
        Low velocity = softer contact duration, damped high frequencies.
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        # Contact duration: 1.2ms (forte) to 4.5ms (piano)
        contact_dur = 0.0012 + 0.0033 * (1.0 - vel_norm)
        contact_samples = max(2, int(contact_dur * self.sr))
        
        t_contact = np.linspace(0, np.pi, contact_samples)
        # Raised-sine pulse (half-sine squared)
        hammer_pulse = np.sin(t_contact) ** 2

        # Mechanical thump (sub-120Hz structural impact)
        thump_samples = int(0.035 * self.sr)
        t_thump = np.linspace(0, 0.035, thump_samples, endpoint=False)
        thump = np.sin(2 * np.pi * 65.0 * t_thump) * np.exp(-95.0 * t_thump) * 0.12 * vel_norm

        total_trans_len = max(contact_samples, thump_samples)
        transient = np.zeros(total_trans_len, dtype=np.float64)
        transient[:contact_samples] += hammer_pulse * (vel_norm ** 1.3) * 0.35
        transient[:thump_samples] += thump

        # Felt damping lowpass filter: 1.8kHz (soft) up to 8.5kHz (hard strike)
        cutoff = 1800.0 + 6700.0 * (vel_norm ** 1.5)
        sos_felt = signal.butter(2, min(cutoff / (self.sr / 2.0), 0.95), btype='lowpass', output='sos')
        filtered_transient = signal.sosfilt(sos_felt, transient)

        return filtered_transient

    def render_note(
        self,
        pitch: int,
        velocity: int = 80,
        duration: float = 2.0,
        release_time: float = 0.08
    ) -> np.ndarray:
        """
        Renders an acoustic grand piano note with physical inharmonicity,
        dual-exponential decay, soundboard resonance, and stereo imaging.
        Returns: Stereo numpy array (shape: (num_samples, 2)).
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        f0 = midi_to_freq_pure(pitch)
        num_samples = int(duration * self.sr)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # 1. Inharmonicity coefficient B:
        # Grand piano strings have stiffness: B is ~0.00008 in bass, up to ~0.00045 in treble
        b_inharmonic = 0.00010 * (1.0 + 0.0035 * max(0, pitch - 21))

        # 2. Number of audible partials below Nyquist
        nyquist = self.sr * 0.46
        max_partials = min(32, max(4, int(nyquist / f0)))

        # 3. Dual-exponential decay parameters:
        # Prompt sound: fast vertical polarization decay (tau1)
        # Aftersound: slow horizontal polarization decay (tau2)
        # Bass notes sustain much longer than treble notes.
        pitch_decay_factor = (261.63 / max(30.0, f0)) ** 0.45
        tau1_base = 0.55 * pitch_decay_factor
        tau2_base = 3.80 * pitch_decay_factor

        # 4. Synthesize string partials with inharmonic dispersion
        string_signal = np.zeros(num_samples, dtype=np.float64)
        
        # Velocity-dependent harmonic slope: softer notes roll off high harmonics much faster
        harmonic_slope = 1.1 + 1.6 * (1.0 - vel_norm)

        for n in range(1, max_partials + 1):
            # Inharmonic frequency formula: f_n = n * f_0 * sqrt(1 + B * n^2)
            fn = n * f0 * math.sqrt(1.0 + b_inharmonic * (n ** 2))
            if fn >= nyquist:
                break

            # Dual decay for partial n: higher partials decay faster
            partial_decay_rate = math.sqrt(n)
            d1 = max(0.04, tau1_base / partial_decay_rate)
            d2 = max(0.20, tau2_base / partial_decay_rate)

            # Dual-exponential amplitude envelope
            env_n = 0.72 * np.exp(-t / d1) + 0.28 * np.exp(-t / d2)

            # Base harmonic amplitude with velocity-sensitive spectral tilt
            amp_n = (1.0 / (n ** harmonic_slope))

            # Initial string phase (subtle randomized micro-phase for string cluster richness)
            phi = 0.05 * np.sin(n * 1.618)
            partial_osc = np.sin(2 * np.pi * fn * t + phi)

            string_signal += partial_osc * (amp_n * env_n)

        # Apply overall velocity scaling (dynamic power curve)
        string_signal *= (vel_norm ** 1.25)

        # 5. Inject hammer strike transient at t=0
        hammer = self._generate_hammer_transient(duration, velocity)
        h_len = min(len(hammer), num_samples)
        string_signal[:h_len] += hammer[:h_len] * 0.45

        # 6. Soundboard modal resonance filtering
        soundboard_out = np.zeros_like(string_signal)
        for b, a, g in self.modal_filters:
            # Resonators excited by string vibration
            mode_response = signal.lfilter(b, a, string_signal)
            soundboard_out += mode_response * g

        # Blend dry string with resonant soundboard (80% string + 20% soundboard body)
        composite = string_signal * 0.82 + soundboard_out * 0.28

        # 7. Note release damper damping (at the end of duration)
        rel_samples = int(release_time * self.sr)
        if rel_samples > 0 and num_samples > rel_samples:
            rel_curve = np.linspace(1.0, 0.0, rel_samples) ** 2
            composite[-rel_samples:] *= rel_curve

        # 8. Stereo acoustic perspective (pianist vantage: low notes left, high notes right)
        pan = np.clip((pitch - 21.0) / (108.0 - 21.0) * 0.6 - 0.3, -0.35, 0.35)
        gain_l = math.cos((pan + 1.0) * math.pi / 4.0)
        gain_r = math.sin((pan + 1.0) * math.pi / 4.0)

        out_l = composite * gain_l
        out_r = composite * gain_r

        return np.column_stack((out_l, out_r))


class PristineRhodesVoice:
    """
    Fender Rhodes Mark I / Suitcase Electric Piano Modeling:
    - Neoprene hammer strike transient (high-frequency metallic tine "chink")
    - 2-Operator FM synthesis: Carrier f0 + Modulator f0 with dynamic modulation index decay
    - Asymmetric pickup nonlinear saturation ("Bark")
    - Stereo optical suitcase tremolo (anti-phase amplitude modulation)
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate

    def _generate_tine_transient(self, duration_s: float, velocity: int) -> np.ndarray:
        """Metallic tine strike transient (ping at 3.2kHz - 4.2kHz, 18ms decay)."""
        vel_norm = max(1, min(127, velocity)) / 127.0
        n_samples = int(0.025 * self.sr)
        t = np.linspace(0, 0.025, n_samples, endpoint=False)
        # Metallic tine ping
        freq_ping = 3400.0 + 800.0 * vel_norm
        ping = np.sin(2 * np.pi * freq_ping * t) * np.exp(-140.0 * t)
        noise = np.random.uniform(-0.5, 0.5, n_samples) * np.exp(-220.0 * t)
        transient = (ping * 0.75 + noise * 0.25) * (vel_norm ** 1.4) * 0.25
        return transient

    def render_note(
        self,
        pitch: int,
        velocity: int = 80,
        duration: float = 2.0,
        tremolo_rate: float = 4.5,
        tremolo_depth: float = 0.35,
        bark_drive: float = 1.25,
        release_time: float = 0.06
    ) -> np.ndarray:
        """
        Renders a Fender Rhodes note with FM tine physics, pickup bark, and stereo tremolo.
        Returns: Stereo numpy array (shape: (num_samples, 2)).
        """
        vel_norm = max(1, min(127, velocity)) / 127.0
        f0 = midi_to_freq_pure(pitch)
        num_samples = int(duration * self.sr)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # 1. Modulation Index beta(t) for FM tine character:
        # Harder velocity = higher initial modulation index = brighter bell attack
        beta_0 = 0.35 + 2.85 * (vel_norm ** 1.8)
        # Modulator decay rate (metallic bell sound decays quickly, leaving warm sine tine body)
        mod_decay_time = 0.08 + 0.12 * (vel_norm ** 0.5)
        mod_index = beta_0 * np.exp(-t / mod_decay_time)

        # 2. Modulator & Carrier synthesis
        # Modulator frequency: f0 (1:1 ratio gives warm classic Rhodes tine bell)
        # Secondary subtle harmonic at 2*f0 for bark character
        modulator = np.sin(2 * np.pi * f0 * t) + 0.22 * np.sin(2 * np.pi * 2.0 * f0 * t)
        fm_phase = 2 * np.pi * f0 * t + mod_index * modulator
        tine_osc = np.sin(fm_phase)

        # 3. Overall tine amplitude decay (prompt strike + long tine sustain)
        decay_tau = 1.6 * ((261.63 / max(40.0, f0)) ** 0.38)
        amp_env = (0.65 * np.exp(-t / (decay_tau * 0.4)) + 0.35 * np.exp(-t / decay_tau)) * (vel_norm ** 1.2)
        raw_tine = tine_osc * amp_env

        # 4. Add neoprene hammer strike click
        transient = self._generate_tine_transient(duration, velocity)
        tr_len = min(len(transient), num_samples)
        raw_tine[:tr_len] += transient[:tr_len]

        # 5. Variable-reluctance magnetic pickup saturation ("Bark"):
        # The pickup response is nonlinear as the tine tip swings close to the pole piece:
        # y_sat = tanh(drive * y) + 0.08 * y^2 (asymmetry creates even harmonics on hard strikes)
        driven = raw_tine * bark_drive
        bark_sound = np.tanh(driven) + 0.075 * (driven ** 2) * np.sign(driven)

        # Subtle preamp warming lowpass filter
        cutoff = min(7200.0, self.sr * 0.45)
        sos_preamp = signal.butter(2, cutoff / (self.sr / 2.0), btype='lowpass', output='sos')
        conditioned = signal.sosfilt(sos_preamp, bark_sound)

        # 6. Damper key-release
        rel_samples = int(release_time * self.sr)
        if rel_samples > 0 and num_samples > rel_samples:
            rel_curve = np.linspace(1.0, 0.0, rel_samples) ** 2
            conditioned[-rel_samples:] *= rel_curve

        # 7. Classic Suitcase Stereo Optical Tremolo (anti-phase auto-pan)
        # Optical tremolo has a smooth sine-trapezoidal shape
        trem_lfo = np.sin(2 * np.pi * tremolo_rate * t)
        pan_l = 1.0 - tremolo_depth * trem_lfo
        pan_r = 1.0 + tremolo_depth * trem_lfo

        out_l = conditioned * pan_l * 0.70
        out_r = conditioned * pan_r * 0.70

        return np.column_stack((out_l, out_r))


class SoundFontManager:
    """
    Manages headless playback of SoundFonts (e.g. Salamander Grand Piano, Rhodes)
    via FluidSynth CLI or soundfont engines, with automatic graceful fallback
    to PristinePianoVoice / PristineRhodesVoice.
    """

    SEARCH_PATHS = [
        "/opt/homebrew/share/soundfonts",
        "/usr/share/sounds/sf2",
        "/usr/local/share/soundfonts",
        "/Library/Audio/Sounds/Banks",
        os.path.expanduser("~/.fluidsynth/soundfonts"),
        os.path.expanduser("~/Soundfonts"),
    ]

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.fluidsynth_bin = self._find_fluidsynth()
        self.available_soundfonts = self._discover_soundfonts()

    def _find_fluidsynth(self) -> Optional[str]:
        """Checks if fluidsynth executable is available."""
        # 1. System path
        found = shutil.which("fluidsynth")
        if found:
            return found
        # 2. Homebrew default on Apple Silicon
        brew_path = "/opt/homebrew/bin/fluidsynth"
        if os.path.isfile(brew_path) and os.access(brew_path, os.X_OK):
            return brew_path
        return None

    def _discover_soundfonts(self) -> Dict[str, str]:
        """Discovers any installed SoundFonts in standard locations."""
        discovered = {}
        for folder in self.SEARCH_PATHS:
            if os.path.isdir(folder):
                for root, _, files in os.walk(folder):
                    for f in files:
                        if f.lower().endswith(('.sf2', '.sf3')):
                            full_path = os.path.join(root, f)
                            fname_lower = f.lower()
                            if "salamander" in fname_lower:
                                discovered["salamander"] = full_path
                            elif "rhodes" in fname_lower:
                                discovered["rhodes"] = full_path
                            elif "piano" in fname_lower or "grand" in fname_lower:
                                discovered.setdefault("grand_piano", full_path)
                            discovered[f] = full_path
        return discovered

    def is_available(self, instrument: str = "grand_piano") -> bool:
        """Returns True if fluidsynth and a matching soundfont are ready."""
        if not self.fluidsynth_bin:
            return False
        return instrument in self.available_soundfonts

    def render_midi_headless(
        self,
        midi_path: str,
        output_wav_path: str,
        soundfont_path: Optional[str] = None
    ) -> bool:
        """
        Renders a MIDI file to WAV using FluidSynth CLI in fast headless batch mode.
        fluidsynth -F output.wav -r 44100 -g 1.0 soundfont.sf2 input.mid
        """
        if not self.fluidsynth_bin:
            return False

        sf_path = soundfont_path
        if not sf_path:
            sf_path = self.available_soundfonts.get("salamander") or \
                      self.available_soundfonts.get("grand_piano") or \
                      next(iter(self.available_soundfonts.values()), None)

        if not sf_path or not os.path.exists(sf_path):
            return False

        cmd = [
            self.fluidsynth_bin,
            "-ni",                     # Non-interactive
            "-F", output_wav_path,     # Fast-render to WAV
            "-r", str(self.sr),        # Sample rate
            "-g", "1.0",               # Gain
            sf_path,
            midi_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            return res.returncode == 0 and os.path.exists(output_wav_path)
        except Exception:
            return False


class PristineKeysEngine:
    """
    Unified Masterclass Keyboard Engine.
    Provides pristine, in-tune physical modeling for:
    - 'grand_piano' (Salamander physical modal synthesis)
    - 'rhodes' (Fender Rhodes Mark I FM + Bark + Stereo Tremolo)
    With headless SoundFont auto-detection and seamless fallback.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate
        self.piano_synth = PristinePianoVoice(sample_rate=sample_rate)
        self.rhodes_synth = PristineRhodesVoice(sample_rate=sample_rate)
        self.soundfont_mgr = SoundFontManager(sample_rate=sample_rate)

    def render_note(
        self,
        pitch: int,
        velocity: int = 80,
        duration: float = 2.0,
        preset: str = "grand_piano",
        **kwargs
    ) -> np.ndarray:
        """Renders an individual note with zero detuning error."""
        if preset.lower() in ("rhodes", "epiano", "electric_piano"):
            return self.rhodes_synth.render_note(pitch, velocity, duration, **kwargs)
        else:
            return self.piano_synth.render_note(pitch, velocity, duration, **kwargs)

    def render_chord(
        self,
        pitches: List[int],
        duration: float = 2.5,
        velocity: int = 85,
        preset: str = "grand_piano",
        strum_delay_ms: float = 12.0
    ) -> np.ndarray:
        """
        Renders a voiced chord with natural humanized micro-strumming and acoustic summing.
        strum_delay_ms: realistic key descent delay across fingers (10-18ms)
        """
        total_samples = int((duration + 0.5) * self.sr)
        chord_mix = np.zeros((total_samples, 2), dtype=np.float64)

        for i, pitch in enumerate(sorted(pitches)):
            # Micro-strumming: lower notes sound a fraction of a millisecond earlier
            offset_s = (i * strum_delay_ms) / 1000.0
            offset_samples = int(offset_s * self.sr)

            # Velocity humanization across chord voicing (top note slightly louder)
            vel_voicing = int(velocity * (0.92 + 0.12 * (i / max(1, len(pitches) - 1))))
            vel_voicing = max(1, min(127, vel_voicing))

            note_audio = self.render_note(
                pitch=pitch,
                velocity=vel_voicing,
                duration=duration,
                preset=preset
            )

            end_samples = min(total_samples, offset_samples + len(note_audio))
            valid_len = end_samples - offset_samples
            if valid_len > 0:
                chord_mix[offset_samples:end_samples] += note_audio[:valid_len]

        # Apply soft master headroom leveling
        peak = np.max(np.abs(chord_mix))
        if peak > 0.95:
            # Gentle soft saturation rather than hard clipping
            chord_mix = np.tanh(chord_mix * 0.85) * 0.95
        else:
            chord_mix = chord_mix * 0.90

        return chord_mix

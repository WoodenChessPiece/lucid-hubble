"""
src/engine/soundfont_synth.py - Production-Grade Headless SoundFont & VST3 Synthesizer Engine

Implements:
1. Multi-Sampled Instrument Architecture via FluidSynth:
   - High-performance in-memory C-backed streaming (400x+ real-time).
   - Multi-velocity sample layers across GeneralUser-GS, FluidR3_GM, and communal soundbanks.
   - Masterclass instrument presets: Grand Piano, Rhodes E-Piano, Strings, Warm French Horns, Electric Bass.
2. Expressive Velocity Scaling & Release Damping:
   - Non-linear velocity mapping curves (warm_log, punchy, ballad, exponential, linear).
   - Acoustic release damping with instrument-specific tail synthesis and MIDI CC 72/74 modulation.
3. Sample-Accurate NoteEvent List Rendering:
   - Handles single notes, micro-strummed chords, monophonic/polyphonic tracks, and multi-track stems.
   - Seamless integration with Arrangement objects from src/composer/arranger.py.
4. Headless VST3 Synth Hosting via Spotify Pedalboard:
   - Headless parameterization and MIDI rendering for Surge XT, Dexed FM, Vital, and effect plugins.
5. Robust Fallback Architecture:
   - Falls back gracefully to physical modeling (PristineKeysEngine) if SoundFonts or FluidSynth are absent.
"""

import os
import math
import shutil
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np

# Configure logger
logger = logging.getLogger("SoundFontSamplerEngine")

# Try importing pyfluidsynth
try:
    import fluidsynth
    HAS_FLUIDSYNTH = True
except ImportError:
    fluidsynth = None
    HAS_FLUIDSYNTH = False

# Try importing pedalboard for VST3 hosting
try:
    import pedalboard
    HAS_PEDALBOARD = True
except ImportError:
    pedalboard = None
    HAS_PEDALBOARD = False

# Import local composer and physical modeling modules if available
try:
    from src.composer.arranger import NoteEvent, Arrangement
except ImportError:
    @dataclass
    class NoteEvent:
        pitch: int
        start_time: float
        duration: float
        velocity: int
        channel: int = 0
        track_name: str = "main"

    class Arrangement:
        pass

try:
    from src.engine.pristine_keys import PristineKeysEngine
    HAS_PRISTINE_KEYS = True
except ImportError:
    PristineKeysEngine = None
    HAS_PRISTINE_KEYS = False

SAMPLE_RATE = 44100


# ==============================================================================
# 1. SOUNDFONT REGISTRY & DISCOVERY
# ==============================================================================

class SoundFontRegistry:
    """
    Discovers, indexes, and validates SoundFont 2 (.sf2/.sf3) soundbanks
    across local workspace, storage directories, Google Drive, and OS paths.
    """

    SEARCH_PATHS = [
        os.path.abspath("storage/soundbanks"),
        os.path.abspath("storage/soundfonts"),
        os.path.abspath("storage/soundbanks/SalamanderGrandPiano"),
        "/Users/x17hubris/Library/CloudStorage/GoogleDrive-clearpointprofessional@gmail.com/My Drive/HeadlessMusicStudio/soundbanks",
        "/Users/x17hubris/Library/CloudStorage/GoogleDrive-clearpointprofessional@gmail.com/My Drive/HeadlessMusicStudio/soundfonts",
        "/Library/Audio/Sounds/Banks",
        "/System/Library/Components/CoreAudio.component/Contents/Resources",
        os.path.expanduser("~/.fluidsynth/soundfonts"),
        os.path.expanduser("~/Soundfonts"),
    ]

    def __init__(self):
        self.banks: Dict[str, str] = {}
        self._discover()

    def _discover(self):
        for base in self.SEARCH_PATHS:
            if not os.path.exists(base):
                continue
            if os.path.isfile(base) and base.lower().endswith(('.sf2', '.sf3')):
                self._register_file(base)
            elif os.path.isdir(base):
                for root, _, files in os.walk(base):
                    for f in files:
                        if f.lower().endswith(('.sf2', '.sf3')):
                            full = os.path.join(root, f)
                            self._register_file(full)

    def _register_file(self, path: str):
        fname = os.path.basename(path).lower()
        if "generaluser" in fname:
            self.banks.setdefault("general_user", path)
        elif "fluidr3" in fname:
            self.banks.setdefault("fluid_r3", path)
        elif "timgm" in fname:
            self.banks.setdefault("timgm", path)
        elif "salamander" in fname:
            self.banks.setdefault("salamander", path)
        self.banks.setdefault(os.path.splitext(os.path.basename(path))[0].lower(), path)

    def get_soundfont(self, preference: str = "general_user") -> Optional[str]:
        """Returns the best available SoundFont path matching preference."""
        if preference in self.banks and os.path.exists(self.banks[preference]):
            return self.banks[preference]

        # Preferred hierarchy
        for fallback in ["general_user", "fluid_r3", "timgm"]:
            if fallback in self.banks and os.path.exists(self.banks[fallback]):
                return self.banks[fallback]

        if self.banks:
            first_path = next(iter(self.banks.values()))
            if os.path.exists(first_path):
                return first_path
        return None

    def list_available(self) -> Dict[str, str]:
        return dict(self.banks)


# ==============================================================================
# 2. INSTRUMENT PRESET SPECIFICATION
# ==============================================================================

@dataclass
class InstrumentPreset:
    """
    Detailed acoustic and synthesis parameter specification for a multi-sampled instrument.
    """
    name: str
    bank: int
    program: int
    soundfont_preference: str = "general_user"
    velocity_curve: str = "warm_log"  # 'warm_log', 'punchy', 'ballad', 'linear', 'exponential'
    gamma: float = 1.20
    velocity_floor: int = 20
    release_tail_s: float = 0.65
    brightness_cc74: int = 64
    resonance_cc71: int = 64
    release_time_cc72: int = 64
    reverb_send_cc91: int = 40
    chorus_send_cc93: int = 0
    stereo_pan: float = 0.0  # -1.0 (left) to +1.0 (right)
    gain_db: float = 0.0


# Comprehensive catalog of authentic melodic instruments
PRESET_CATALOG: Dict[str, InstrumentPreset] = {
    # 1. Grand Piano
    "grand_piano": InstrumentPreset(
        name="Acoustic Grand Piano",
        bank=0,
        program=0,
        soundfont_preference="fluid_r3",
        velocity_curve="warm_log",
        gamma=1.22,
        velocity_floor=20,
        release_tail_s=0.85,
        brightness_cc74=64,
        release_time_cc72=68,
        gain_db=-1.0
    ),
    "bright_grand": InstrumentPreset(
        name="Bright Grand Piano",
        bank=0,
        program=1,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=0.95,
        velocity_floor=25,
        release_tail_s=0.75,
        brightness_cc74=80,
        release_time_cc72=60,
        gain_db=-1.0
    ),
    "warm_grand": InstrumentPreset(
        name="Warm Intimate Grand",
        bank=0,
        program=0,
        soundfont_preference="general_user",
        velocity_curve="ballad",
        gamma=1.35,
        velocity_floor=15,
        release_tail_s=0.90,
        brightness_cc74=54,
        release_time_cc72=72,
        gain_db=-0.5
    ),

    # 2. Rhodes & Electric Keys
    "rhodes": InstrumentPreset(
        name="Fender Rhodes Mark I (EP 1)",
        bank=0,
        program=4,
        soundfont_preference="general_user",
        velocity_curve="warm_log",
        gamma=1.15,
        velocity_floor=25,
        release_tail_s=0.60,
        brightness_cc74=68,
        release_time_cc72=64,
        chorus_send_cc93=35,
        gain_db=0.0
    ),
    "chorused_rhodes": InstrumentPreset(
        name="Detuned Chorused Rhodes",
        bank=8,
        program=4,
        soundfont_preference="general_user",
        velocity_curve="warm_log",
        gamma=1.18,
        velocity_floor=20,
        release_tail_s=0.70,
        brightness_cc74=72,
        chorus_send_cc93=55,
        gain_db=-0.5
    ),
    "fm_epiano": InstrumentPreset(
        name="Yamaha DX7 FM Electric Piano (EP 2)",
        bank=0,
        program=5,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=1.05,
        velocity_floor=25,
        release_tail_s=0.75,
        brightness_cc74=76,
        chorus_send_cc93=45,
        gain_db=0.0
    ),
    "clavinet": InstrumentPreset(
        name="D6 Funk Clavinet",
        bank=0,
        program=7,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=0.90,
        velocity_floor=30,
        release_tail_s=0.30,
        brightness_cc74=85,
        gain_db=0.5
    ),

    # 3. Strings & Orchestral Ensembles
    "strings": InstrumentPreset(
        name="Orchestral String Ensemble",
        bank=0,
        program=48,
        soundfont_preference="fluid_r3",
        velocity_curve="ballad",
        gamma=1.10,
        velocity_floor=20,
        release_tail_s=1.35,
        brightness_cc74=66,
        release_time_cc72=78,
        reverb_send_cc91=60,
        gain_db=-1.5
    ),
    "slow_strings": InstrumentPreset(
        name="Slow Ambient Strings",
        bank=8,
        program=48,
        soundfont_preference="general_user",
        velocity_curve="ballad",
        gamma=1.20,
        velocity_floor=15,
        release_tail_s=1.80,
        brightness_cc74=60,
        release_time_cc72=88,
        reverb_send_cc91=70,
        gain_db=-2.0
    ),
    "synth_strings": InstrumentPreset(
        name="Analog Warm Synth Strings",
        bank=0,
        program=50,
        soundfont_preference="general_user",
        velocity_curve="warm_log",
        gamma=1.10,
        velocity_floor=20,
        release_tail_s=1.25,
        brightness_cc74=72,
        release_time_cc72=76,
        gain_db=-1.0
    ),
    "pizzicato_strings": InstrumentPreset(
        name="Pizzicato Chamber Strings",
        bank=0,
        program=45,
        soundfont_preference="fluid_r3",
        velocity_curve="punchy",
        gamma=0.95,
        velocity_floor=30,
        release_tail_s=0.35,
        gain_db=0.0
    ),
    "cello": InstrumentPreset(
        name="Solo Cello Legato",
        bank=0,
        program=42,
        soundfont_preference="fluid_r3",
        velocity_curve="ballad",
        gamma=1.15,
        velocity_floor=20,
        release_tail_s=0.95,
        brightness_cc74=62,
        gain_db=0.0
    ),

    # 4. Warm French Horns & Brass
    "french_horn": InstrumentPreset(
        name="French Horn Solo & Section",
        bank=0,
        program=60,
        soundfont_preference="fluid_r3",
        velocity_curve="warm_log",
        gamma=1.25,
        velocity_floor=25,
        release_tail_s=1.10,
        brightness_cc74=64,
        release_time_cc72=74,
        reverb_send_cc91=55,
        gain_db=-1.0
    ),
    "warm_french_horn": InstrumentPreset(
        name="Warm French Horn (GS Variation)",
        bank=1,
        program=60,
        soundfont_preference="general_user",
        velocity_curve="ballad",
        gamma=1.30,
        velocity_floor=20,
        release_tail_s=1.20,
        brightness_cc74=58,
        release_time_cc72=78,
        gain_db=-0.8
    ),
    "brass_section": InstrumentPreset(
        name="Orchestral Brass Section",
        bank=0,
        program=61,
        soundfont_preference="fluid_r3",
        velocity_curve="punchy",
        gamma=1.05,
        velocity_floor=25,
        release_tail_s=0.80,
        brightness_cc74=75,
        release_time_cc72=62,
        gain_db=-1.2
    ),
    "synth_brass": InstrumentPreset(
        name="80s Poly Synth Brass",
        bank=0,
        program=62,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=1.00,
        velocity_floor=25,
        release_tail_s=0.85,
        brightness_cc74=80,
        release_time_cc72=68,
        gain_db=-1.0
    ),

    # 5. Electric Bass & Upright Bass
    "electric_bass": InstrumentPreset(
        name="Fender Precision Electric Finger Bass",
        bank=0,
        program=33,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=1.05,
        velocity_floor=35,
        release_tail_s=0.35,
        brightness_cc74=68,
        release_time_cc72=50,
        gain_db=1.0
    ),
    "pick_bass": InstrumentPreset(
        name="Electric Pick Bass (Rock / Punk)",
        bank=0,
        program=34,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=0.95,
        velocity_floor=40,
        release_tail_s=0.30,
        brightness_cc74=76,
        release_time_cc72=48,
        gain_db=1.0
    ),
    "fretless_bass": InstrumentPreset(
        name="Jaco Fretless Electric Bass",
        bank=0,
        program=35,
        soundfont_preference="fluid_r3",
        velocity_curve="warm_log",
        gamma=1.15,
        velocity_floor=25,
        release_tail_s=0.55,
        brightness_cc74=64,
        release_time_cc72=58,
        gain_db=0.5
    ),
    "slap_bass": InstrumentPreset(
        name="Slap Bass Funk Attack",
        bank=0,
        program=36,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=0.88,
        velocity_floor=45,
        release_tail_s=0.25,
        brightness_cc74=82,
        gain_db=0.8
    ),
    "synth_bass": InstrumentPreset(
        name="Roland SH-101 Style Synth Bass",
        bank=0,
        program=38,
        soundfont_preference="general_user",
        velocity_curve="punchy",
        gamma=1.00,
        velocity_floor=30,
        release_tail_s=0.35,
        brightness_cc74=72,
        gain_db=1.2
    ),

    # 6. Additional Melodic & Acoustic Instruments
    "vibraphone": InstrumentPreset(
        name="Jazz Vibraphone with Tremolo",
        bank=0,
        program=11,
        soundfont_preference="fluid_r3",
        velocity_curve="warm_log",
        gamma=1.12,
        velocity_floor=25,
        release_tail_s=1.20,
        gain_db=0.0
    ),
    "acoustic_guitar": InstrumentPreset(
        name="Nylon String Acoustic Guitar",
        bank=0,
        program=24,
        soundfont_preference="general_user",
        velocity_curve="warm_log",
        gamma=1.15,
        velocity_floor=20,
        release_tail_s=0.60,
        gain_db=0.0
    ),
    "flute": InstrumentPreset(
        name="Concert Flute Vibrato",
        bank=0,
        program=73,
        soundfont_preference="fluid_r3",
        velocity_curve="ballad",
        gamma=1.20,
        velocity_floor=20,
        release_tail_s=0.65,
        gain_db=-0.5
    ),
    "choir": InstrumentPreset(
        name="Choir Aahs Vocal Ensemble",
        bank=0,
        program=52,
        soundfont_preference="general_user",
        velocity_curve="ballad",
        gamma=1.25,
        velocity_floor=15,
        release_tail_s=1.40,
        gain_db=-1.5
    )
}

# Aliases for flexible lookup
PRESET_ALIASES: Dict[str, str] = {
    "piano": "grand_piano",
    "keys": "rhodes",
    "electric_piano": "rhodes",
    "epiano": "rhodes",
    "chords": "strings",
    "pad": "strings",
    "pads": "slow_strings",
    "counter": "rhodes",
    "lead": "synth_brass",
    "bass": "electric_bass",
    "horns": "french_horn",
    "horn": "french_horn",
    "brass": "brass_section",
}


# ==============================================================================
# 3. VELOCITY SCALING ENGINE
# ==============================================================================

class VelocityScaler:
    """
    Transforms raw MIDI velocity (1-127) using psychoacoustically calibrated
    curves to ensure realistic dynamic response and expressive touch.
    """

    @staticmethod
    def scale(
        raw_velocity: int,
        curve: str = "warm_log",
        gamma: float = 1.20,
        floor: int = 15
    ) -> int:
        v = max(1, min(127, raw_velocity))
        norm = v / 127.0

        if curve == "linear":
            scaled_norm = norm
        elif curve == "warm_log":
            # Warms up mid velocity and softens brittle transients
            scaled_norm = math.pow(norm, gamma)
        elif curve == "punchy":
            # Elevates lower/mid velocities for tight, punchy presence
            scaled_norm = 0.25 * math.sqrt(norm) + 0.75 * norm
        elif curve == "ballad":
            # Extended soft-touch dynamic sensitivity
            scaled_norm = math.pow(norm, max(1.3, gamma * 1.15))
        elif curve == "exponential":
            scaled_norm = (math.exp(norm * 2.0) - 1.0) / (math.exp(2.0) - 1.0)
        else:
            scaled_norm = math.pow(norm, gamma)

        final_val = int(floor + (127 - floor) * scaled_norm)
        return max(1, min(127, final_val))


# ==============================================================================
# 4. PRODUCTION SOUNDFONT SAMPLER ENGINE
# ==============================================================================

class SoundFontSamplerEngine:
    """
    Production-grade multi-sampled instrument rendering engine powered by FluidSynth.
    Provides in-memory, sample-accurate rendering of NoteEvents across all acoustic
    and melodic instruments with real multi-velocity samples and natural release damping.
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        polyphony: int = 256,
        gain: float = 0.85
    ):
        self.sr = sample_rate
        self.polyphony = polyphony
        self.gain = gain
        self.registry = SoundFontRegistry()
        self.synth: Optional[Any] = None
        self.loaded_soundfonts: Dict[str, int] = {}  # sf_path -> sfid
        self._keys_fallback: Optional[Any] = None

        if HAS_FLUIDSYNTH:
            self._init_fluidsynth()
        else:
            logger.warning("FluidSynth python package not available; using physical modeling fallback.")

    def _init_fluidsynth(self):
        try:
            self.synth = fluidsynth.Synth(samplerate=float(self.sr))
            self.synth.setting("synth.polyphony", self.polyphony)
            self.synth.setting("synth.gain", self.gain)
            self.synth.setting("synth.reverb.active", 1)
            self.synth.setting("synth.chorus.active", 1)

            # Pre-load core soundfonts
            for alias in ["general_user", "fluid_r3", "timgm"]:
                sf_path = self.registry.get_soundfont(alias)
                if sf_path and sf_path not in self.loaded_soundfonts and os.path.isfile(sf_path):
                    sfid = self.synth.sfload(sf_path)
                    if sfid > 0:
                        self.loaded_soundfonts[sf_path] = sfid
                        logger.info(f"Loaded SoundFont '{alias}' ({os.path.basename(sf_path)}) with SFID {sfid}")
        except Exception as e:
            logger.error(f"Failed to initialize FluidSynth: {e}")
            self.synth = None

    def _get_sfid_for_preset(self, preset: InstrumentPreset) -> Optional[int]:
        if not self.synth:
            return None
        sf_path = self.registry.get_soundfont(preset.soundfont_preference)
        if not sf_path or not os.path.isfile(sf_path):
            # Fallback to any loaded SFID
            if self.loaded_soundfonts:
                return next(iter(self.loaded_soundfonts.values()))
            return None

        if sf_path not in self.loaded_soundfonts:
            sfid = self.synth.sfload(sf_path)
            if sfid > 0:
                self.loaded_soundfonts[sf_path] = sfid
            else:
                return None
        return self.loaded_soundfonts[sf_path]

    def _get_preset(self, preset_name_or_alias: str) -> InstrumentPreset:
        key = preset_name_or_alias.lower().strip()
        if key in PRESET_CATALOG:
            return PRESET_CATALOG[key]
        resolved = PRESET_ALIASES.get(key, "grand_piano")
        return PRESET_CATALOG.get(resolved, PRESET_CATALOG["grand_piano"])

    def _get_keys_fallback(self) -> Any:
        if self._keys_fallback is None and HAS_PRISTINE_KEYS:
            self._keys_fallback = PristineKeysEngine(sample_rate=self.sr)
        return self._keys_fallback

    # --------------------------------------------------------------------------
    # Single Note & Chord Rendering
    # --------------------------------------------------------------------------

    def render_note(
        self,
        pitch: int,
        velocity: int = 80,
        duration: float = 2.0,
        preset: str = "grand_piano",
        tail_s: Optional[float] = None
    ) -> np.ndarray:
        """
        Renders an individual melodic note with velocity-layer mapping and acoustic release damping.
        Returns stereo float32 NumPy array of shape (num_samples, 2).
        """
        ev = NoteEvent(pitch=pitch, start_time=0.0, duration=duration, velocity=velocity)
        return self.render_note_events([ev], preset=preset, tail_s=tail_s)

    def render_chord(
        self,
        pitches: List[int],
        duration: float = 2.5,
        velocity: int = 85,
        preset: str = "grand_piano",
        strum_delay_ms: float = 12.0,
        tail_s: Optional[float] = None
    ) -> np.ndarray:
        """
        Renders a voiced chord with humanized micro-strum descent and per-voice velocity grading.
        """
        sorted_pitches = sorted(pitches)
        events = []
        n_notes = len(sorted_pitches)
        for i, p in enumerate(sorted_pitches):
            start_t = (i * strum_delay_ms) / 1000.0
            # Subtle velocity shading across voicing (top melody notes slightly accentuated)
            vel_voicing = int(velocity * (0.92 + 0.12 * (i / max(1, n_notes - 1))))
            events.append(NoteEvent(
                pitch=p,
                start_time=start_t,
                duration=duration,
                velocity=max(1, min(127, vel_voicing))
            ))
        return self.render_note_events(events, preset=preset, tail_s=tail_s)

    # --------------------------------------------------------------------------
    # Fast In-Memory Sample-Accurate NoteEvent List Rendering
    # --------------------------------------------------------------------------

    def render_note_events(
        self,
        events: List[NoteEvent],
        preset: str = "grand_piano",
        tail_s: Optional[float] = None,
        channel: int = 0
    ) -> np.ndarray:
        """
        Renders a list of NoteEvents into stereo float32 audio.
        Dispatches NoteOn and NoteOff events with sample-accurate micro-stepping in C memory.
        """
        if not events:
            return np.zeros((0, 2), dtype=np.float32)

        inst = self._get_preset(preset)
        release_tail = tail_s if tail_s is not None else inst.release_tail_s

        # If FluidSynth is unavailable, fall back to PristineKeysEngine
        if not self.synth:
            return self._render_fallback_events(events, inst)

        sfid = self._get_sfid_for_preset(inst)
        if not sfid:
            return self._render_fallback_events(events, inst)

        # Select Bank & Program on the requested MIDI channel
        self.synth.program_select(channel, sfid, inst.bank, inst.program)

        # Configure Sound Controller CCs
        self.synth.cc(channel, 74, inst.brightness_cc74)      # Brightness (LP filter cutoff)
        self.synth.cc(channel, 71, inst.resonance_cc71)       # Filter Resonance
        self.synth.cc(channel, 72, inst.release_time_cc72)    # Release Time Envelope
        self.synth.cc(channel, 91, inst.reverb_send_cc91)     # Reverb Send
        self.synth.cc(channel, 93, inst.chorus_send_cc93)     # Chorus Send
        # Stereo pan (-1.0 to 1.0 mapped to 0-127)
        pan_val = int(np.clip((inst.stereo_pan + 1.0) * 63.5, 0, 127))
        self.synth.cc(channel, 10, pan_val)

        # Build chronological discrete events: (time_s, type, pitch, scaled_velocity)
        timeline = []
        for n in events:
            scaled_v = VelocityScaler.scale(
                n.velocity,
                curve=inst.velocity_curve,
                gamma=inst.gamma,
                floor=inst.velocity_floor
            )
            timeline.append((n.start_time, "on", n.pitch, scaled_v))
            timeline.append((n.start_time + n.duration, "off", n.pitch, 0))

        # Sort timeline strictly by timestamp
        timeline.sort(key=lambda x: (x[0], 0 if x[1] == "off" else 1))

        # Stream audio chunks between timeline events
        chunks = []
        curr_time = 0.0

        for ev_time, ev_type, pitch, vel in timeline:
            dt = ev_time - curr_time
            if dt > 1e-6:
                n_samples = int(round(dt * self.sr))
                if n_samples > 0:
                    raw_chunk = self.synth.get_samples(n_samples)
                    chunks.append(raw_chunk)
                    curr_time += n_samples / self.sr

            if ev_type == "on":
                self.synth.noteon(channel, pitch, vel)
            else:
                self.synth.noteoff(channel, pitch)

        # Render acoustic release decay tail
        tail_samples = int(round(release_tail * self.sr))
        if tail_samples > 0:
            tail_chunk = self.synth.get_samples(tail_samples)
            chunks.append(tail_chunk)

        # Reset channel notes
        self.synth.all_notes_off(channel)

        if not chunks:
            return np.zeros((0, 2), dtype=np.float32)

        # Flatten and convert interleaved int16 to (N, 2) float32
        concatenated = np.concatenate(chunks)
        audio = concatenated.astype(np.float32).reshape(-1, 2) / 32768.0

        # Apply gain adjustment if specified
        if abs(inst.gain_db) > 1e-3:
            linear_gain = math.pow(10.0, inst.gain_db / 20.0)
            audio = audio * linear_gain

        return audio

    def _render_fallback_events(self, events: List[NoteEvent], inst: InstrumentPreset) -> np.ndarray:
        """Physical modeling fallback if SoundFonts/FluidSynth are not initialized."""
        keys_engine = self._get_keys_fallback()
        if not events:
            return np.zeros((0, 2), dtype=np.float32)

        total_dur = max(n.start_time + n.duration for n in events) + inst.release_tail_s
        total_samples = int(math.ceil(total_dur * self.sr))
        mix = np.zeros((total_samples, 2), dtype=np.float32)

        for n in events:
            idx = int(round(n.start_time * self.sr))
            preset_name = "rhodes" if "rhodes" in inst.name.lower() or "ep" in inst.name.lower() else "grand_piano"
            if keys_engine:
                sound = keys_engine.render_note(n.pitch, velocity=n.velocity, duration=n.duration, preset=preset_name)
            else:
                # Basic sine harmonic fallback
                t = np.linspace(0, n.duration, int(n.duration * self.sr), endpoint=False)
                freq = 440.0 * (2.0 ** ((n.pitch - 69.0) / 12.0))
                sig = np.sin(2 * np.pi * freq * t) * np.exp(-3.0 * t) * (n.velocity / 127.0)
                sound = np.column_stack((sig, sig))

            end = min(idx + len(sound), total_samples)
            valid = end - idx
            if valid > 0:
                mix[idx:end] += sound[:valid].astype(np.float32)

        return mix

    # --------------------------------------------------------------------------
    # Multi-Track Stem & Arrangement Rendering
    # --------------------------------------------------------------------------

    def render_multitrack(
        self,
        tracks: Dict[str, List[NoteEvent]],
        track_preset_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, np.ndarray]:
        """
        Renders multiple NoteEvent tracks into isolated high-resolution audio stems.
        """
        default_map = {
            "piano": "grand_piano",
            "keys": "rhodes",
            "chords": "strings",
            "pads": "slow_strings",
            "pad": "slow_strings",
            "strings": "strings",
            "french_horn": "warm_french_horn",
            "horns": "warm_french_horn",
            "brass": "brass_section",
            "bass": "electric_bass",
            "counter": "rhodes",
            "lead": "synth_brass"
        }
        active_map = default_map.copy()
        if track_preset_map:
            active_map.update(track_preset_map)

        stems: Dict[str, np.ndarray] = {}
        for track_name, notes in tracks.items():
            if not notes:
                continue
            preset_name = active_map.get(track_name, "grand_piano")
            stem_audio = self.render_note_events(notes, preset=preset_name)
            stems[track_name] = stem_audio

        return stems

    def render_arrangement(
        self,
        arrangement: Any,
        track_preset_map: Optional[Dict[str, str]] = None
    ) -> np.ndarray:
        """
        Directly renders an Arrangement object from src.composer.arranger, replacing
        crude oscillator tracks with multi-sampled acoustic and electric instruments.
        Summed output is length-aligned and normalized to prevent clipping.
        """
        if not hasattr(arrangement, "tracks"):
            raise ValueError("Arrangement object must have a 'tracks' dictionary.")

        stems = self.render_multitrack(arrangement.tracks, track_preset_map=track_preset_map)
        if not stems:
            total_samples = int(getattr(arrangement, "total_duration", 10.0) * self.sr)
            return np.zeros((total_samples, 2), dtype=np.float32)

        max_len = max(len(s) for s in stems.values())
        mix = np.zeros((max_len, 2), dtype=np.float32)

        for name, audio in stems.items():
            mix[:len(audio)] += audio

        # Master soft-saturation headroom protection
        peak = float(np.max(np.abs(mix)))
        if peak > 0.95:
            mix = np.tanh(mix * 0.88) * 0.94
        elif peak > 0:
            mix = mix * 0.92

        return mix

    def close(self):
        """Releases FluidSynth C engine resources."""
        if self.synth:
            try:
                self.synth.delete()
            except Exception:
                pass
            self.synth = None


# ==============================================================================
# 5. HEADLESS VST3 SYNTH HOSTING VIA SPOTIFY PEDALBOARD
# ==============================================================================

class HeadlessVST3SynthHost:
    """
    Headless VST3 instrument hosting engine powered by Spotify Pedalboard.
    Supports loading, parameterizing, and rendering open-source synthesizers:
    - Dexed FM (Yamaha DX7 6-OP FM synthesis)
    - Surge XT (Hybrid wavetable / subtractive / FM synthesis)
    - Vital (Spectral warping wavetable synthesis)
    - CHOWTapeModel & custom VST3 audio effects
    """

    DEFAULT_VST3_DIRS = [
        os.path.abspath("storage/plugins/vst3"),
        "/Library/Audio/Plug-Ins/VST3",
        "/Users/x17hubris/Library/CloudStorage/GoogleDrive-clearpointprofessional@gmail.com/My Drive/HeadlessMusicStudio/plugins/vst3",
        os.path.expanduser("~/Library/Audio/Plug-Ins/VST3")
    ]

    def __init__(
        self,
        plugin_path_or_name: str,
        sample_rate: int = SAMPLE_RATE
    ):
        if not HAS_PEDALBOARD:
            raise RuntimeError("Spotify Pedalboard is required for HeadlessVST3SynthHost.")

        self.sr = sample_rate
        self.plugin_path = self._resolve_plugin_path(plugin_path_or_name)
        if not self.plugin_path or not os.path.exists(self.plugin_path):
            raise FileNotFoundError(f"VST3 plugin not found: {plugin_path_or_name}")

        self.plugin = pedalboard.load_plugin(self.plugin_path)
        self.name = getattr(self.plugin, "name", os.path.basename(self.plugin_path))
        self.is_instrument = getattr(self.plugin, "is_instrument", False)

    def _resolve_plugin_path(self, target: str) -> Optional[str]:
        if os.path.isfile(target) or os.path.isdir(target):
            return os.path.abspath(target)

        target_fname = target if target.endswith(".vst3") else f"{target}.vst3"
        for d in self.DEFAULT_VST3_DIRS:
            candidate = os.path.join(d, target_fname)
            if os.path.exists(candidate):
                return candidate
        return None

    def list_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Returns a comprehensive dictionary of all controllable VST3 parameters."""
        result = {}
        for k, p in self.plugin.parameters.items():
            result[k] = {
                "raw_value": getattr(p, "raw_value", None),
                "min_value": getattr(p, "min_value", None),
                "max_value": getattr(p, "max_value", None),
                "default_value": getattr(p, "default_value", None)
            }
        return result

    def set_parameter(self, param_name: str, value: float):
        """Sets a parameter by name, automatically clamping to valid range."""
        if param_name not in self.plugin.parameters:
            raise KeyError(f"Parameter '{param_name}' not found in plugin '{self.name}'")
        p = self.plugin.parameters[param_name]
        min_v = getattr(p, "min_value", 0.0)
        max_v = getattr(p, "max_value", 1.0)
        clamped = float(np.clip(value, min_v, max_v))
        p.value = clamped

    def get_parameter(self, param_name: str) -> float:
        if param_name not in self.plugin.parameters:
            raise KeyError(f"Parameter '{param_name}' not found in plugin '{self.name}'")
        return getattr(self.plugin.parameters[param_name], "value", 0.0)

    def get_state(self) -> bytes:
        """Serializes current plugin state into raw byte array."""
        return bytes(self.plugin.raw_state)

    def set_state(self, state: bytes):
        """Restores plugin state from raw byte array."""
        self.plugin.raw_state = state

    def render_notes(
        self,
        events: List[NoteEvent],
        duration: Optional[float] = None,
        tail_s: float = 1.0
    ) -> np.ndarray:
        """
        Converts NoteEvents into Pedalboard MIDI message tuples and renders stereo audio.
        Format: ([status_byte, pitch, velocity], timestamp_in_seconds)
        """
        if not events:
            return np.zeros((2, 0), dtype=np.float32)

        total_dur = duration
        if total_dur is None:
            total_dur = max(n.start_time + n.duration for n in events) + tail_s

        # Build Pedalboard MIDI message tuples
        midi_messages = []
        for n in events:
            note_on = ([0x90 | (n.channel & 0x0F), n.pitch, max(1, min(127, n.velocity))], float(n.start_time))
            note_off = ([0x80 | (n.channel & 0x0F), n.pitch, 0], float(n.start_time + n.duration))
            midi_messages.append(note_on)
            midi_messages.append(note_off)

        # Sort strictly by timestamp
        midi_messages.sort(key=lambda x: x[1])

        # Render headlessly via Pedalboard
        audio = self.plugin(
            midi_messages,
            sample_rate=self.sr,
            duration=float(total_dur),
            num_channels=2
        )
        # Returns (2, N) -> Transpose to (N, 2)
        return audio.T.astype(np.float32)

    def render_chord(
        self,
        pitches: List[int],
        duration: float = 2.0,
        velocity: int = 85,
        strum_delay_ms: float = 12.0,
        tail_s: float = 1.0
    ) -> np.ndarray:
        """Renders voiced chord with realistic finger strumming."""
        events = []
        for i, p in enumerate(sorted(pitches)):
            events.append(NoteEvent(
                pitch=p,
                start_time=(i * strum_delay_ms) / 1000.0,
                duration=duration,
                velocity=velocity
            ))
        return self.render_notes(events, tail_s=tail_s)

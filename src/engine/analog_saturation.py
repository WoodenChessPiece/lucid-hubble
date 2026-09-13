"""
src/engine/analog_saturation.py - Analog Saturation, Diode Modeling & Console8 Summing
Implements Airwindows Console8 channel encode / bus decode & WDF diode saturation.
"""

import numpy as np
import scipy.signal as signal

def console8_channel_encode(audio: np.ndarray, drive: float = 0.85) -> np.ndarray:
    """
    Airwindows Console8 Channel Encode:
    Applies sin(x) soft saturation to track stems before summing.
    Compresses peaks gently and adds subtle odd harmonics.
    """
    scaled = np.clip(audio * drive, -np.pi / 2.0, np.pi / 2.0)
    return np.sin(scaled) / drive

def console8_bus_decode(audio: np.ndarray, drive: float = 0.85) -> np.ndarray:
    """
    Airwindows Console8 Master Bus Decode:
    Applies arcsin(x) complementary transfer function after stem summation.
    Restores dynamic expansion, creates analog summing depth, and separates instruments.
    """
    # Clip slightly inside [-1, 1] to avoid mathematical domain errors in arcsin
    bounded = np.clip(audio * drive * 0.95, -0.98, 0.98)
    decoded = np.arcsin(bounded) / (drive * 0.95)
    return decoded

def diode_bass_saturation(audio: np.ndarray, drive: float = 1.35, sample_rate: int = 44100) -> np.ndarray:
    """
    4x oversampled asymmetrical diode saturation for bass stems.
    Adds even and odd harmonics for presence on laptop speakers and phones.
    """
    up = signal.resample_poly(audio, up=4, down=1, axis=0)
    # Asymmetric soft diode clipping
    x = up * drive
    saturated = np.where(x > 0, np.tanh(x), np.tanh(x * 1.25) / 1.25)
    down = signal.resample_poly(saturated, up=1, down=4, axis=0)
    return down

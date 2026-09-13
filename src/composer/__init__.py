"""
src/composer - Lucid Hubble Algorithmic Composition & Musicology Suite
"""

from .studio_brain import StudioBrain, get_studio_brain, UnifiedArrangement
from .knowledge_base import MusicKnowledgeBase
from .billboard_loader import BillboardHitLoader, get_billboard_loader, HitProgression
from .open_midi_loader import OpenMidiLibrary, OpenMidiLoader, find_midi_library_zip
from .arranger import Arrangement, NoteEvent, create_arrangement, ARCHETYPES

__all__ = [
    "StudioBrain",
    "get_studio_brain",
    "UnifiedArrangement",
    "MusicKnowledgeBase",
    "BillboardHitLoader",
    "get_billboard_loader",
    "HitProgression",
    "OpenMidiLibrary",
    "OpenMidiLoader",
    "find_midi_library_zip",
    "Arrangement",
    "NoteEvent",
    "create_arrangement",
    "ARCHETYPES",
]

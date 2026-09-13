"""
scripts/build_billboard_database.py
Extracts and consolidates musical data from research/billboard_hits/ into:
src/composer/database/billboard_hits_database.json
"""

import os
import json
import re
from typing import List, Dict, Any

RESEARCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "billboard_hits")
TARGET_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "composer", "database", "billboard_hits_database.json")

def load_json_blocks(filepath: str) -> List[Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    raw_blocks = re.findall(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    blocks = []
    for b in raw_blocks:
        try:
            blocks.append(json.loads(b))
        except Exception as e:
            print(f"Warning: Failed to parse JSON block in {filepath}: {e}")
    return blocks

def build_database():
    harm_file = os.path.join(RESEARCH_DIR, "modern_billboard_harmonic_progressions.md")
    dance_file = os.path.join(RESEARCH_DIR, "modern_electropop_dance_architectures.md")
    vocal_file = os.path.join(RESEARCH_DIR, "modern_vocal_hooks_and_melodic_phrasing.md")

    harm_blocks = load_json_blocks(harm_file)
    dance_blocks = load_json_blocks(dance_file)
    vocal_blocks = load_json_blocks(vocal_file)

    progressions = []
    melodic_motifs = []
    bass_grooves = []

    # --------------------------------------------------------------------------
    # 1. HARMONIC PROGRESSIONS
    # --------------------------------------------------------------------------
    # Block 0: Billie Eilish - Birds of a Feather
    if len(harm_blocks) > 0 and "metadata" in harm_blocks[0]:
        b0 = harm_blocks[0]
        meta = b0["metadata"]
        sec = b0.get("sectional_progressions", {})
        
        # Verse & Main Hook
        if "verse_and_main_hook" in sec:
            v_data = sec["verse_and_main_hook"]
            chords = v_data["chords"]
            progressions.append({
                "id": "billie_eilish_birds_of_a_feather_verse",
                "title": "Birds of a Feather",
                "artist": "Billie Eilish",
                "section": "verse",
                "key": meta.get("key", "D Major"),
                "mode": "Major",
                "bpm": meta.get("tempo_bpm", 105),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": meta.get("harmonic_rhythm", "1 chord per measure"),
                "roman_numerals": "Imaj7 - ii9 - V11 - vi7",
                "roots": [c["root"] for c in chords],
                "types": ["maj7", "min9", "11", "min7"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["dreamy_pop", "indie_pop", "intimate_pop", "alt_pop", "breezy_pop"],
                "description": v_data.get("description", "Nostalgic, floating pop-jazz loop using extended Maj7 and min9 voicings.")
            })

        # Chorus Modal Shift Climax
        if "chorus_modal_shift_climax" in sec:
            c_data = sec["chorus_modal_shift_climax"]
            chords = c_data["chords"]
            progressions.append({
                "id": "billie_eilish_birds_of_a_feather_chorus_climax",
                "title": "Birds of a Feather",
                "artist": "Billie Eilish",
                "section": "chorus_climax",
                "key": meta.get("key", "D Major"),
                "mode": "Major / Modal Interchange",
                "bpm": meta.get("tempo_bpm", 105),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": meta.get("harmonic_rhythm", "1 chord per measure"),
                "roman_numerals": "Imaj7 - ii9 - IVmaj7 - iv6",
                "roots": [c["root"] for c in chords],
                "types": ["maj7", "min9", "maj7", "min6"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["dreamy_pop", "indie_pop", "modal_borrowing", "alt_pop", "nostalgic_pop"],
                "description": c_data.get("description", "Modal interchange introducing minor subdominant iv (Gm6) with descending chromatic line B -> Bb -> A.")
            })

    # Block 1: Chappell Roan - Good Luck, Babe!
    if len(harm_blocks) > 1 and "metadata" in harm_blocks[1]:
        b1 = harm_blocks[1]
        meta = b1["metadata"]
        sec = b1.get("sectional_progressions", {})

        if "verse" in sec:
            v_data = sec["verse"]
            chords = v_data["chords"]
            progressions.append({
                "id": "chappell_roan_good_luck_babe_verse",
                "title": "Good Luck, Babe!",
                "artist": "Chappell Roan",
                "section": "verse",
                "key": meta.get("key", "B Major"),
                "mode": "Major",
                "bpm": meta.get("tempo_bpm", 117),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": meta.get("harmonic_rhythm", "1 chord per measure"),
                "roman_numerals": "I - iii - vi - V",
                "roots": [c["root"] for c in chords],
                "types": ["maj", "min", "min", "maj"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["synthpop", "glam_pop", "80s_pop", "anthemic_pop"],
                "description": v_data.get("description", "Pounding 80s synthpop verse progression.")
            })

        if "chorus_soaring_cadence" in sec:
            c_data = sec["chorus_soaring_cadence"]
            chords = c_data["chords"]
            progressions.append({
                "id": "chappell_roan_good_luck_babe_chorus",
                "title": "Good Luck, Babe!",
                "artist": "Chappell Roan",
                "section": "chorus",
                "key": meta.get("key", "B Major"),
                "mode": "Major",
                "bpm": meta.get("tempo_bpm", 117),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": meta.get("harmonic_rhythm", "1 chord per measure"),
                "roman_numerals": "IV - V - vi - I6",
                "roots": [c["root"] for c in chords],
                "types": ["maj", "maj", "min", "maj/3rd"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["synthpop", "glam_pop", "80s_pop", "anthemic_pop", "soaring_chorus"],
                "description": c_data.get("description", "Soaring chorus lift with first-inversion bass resolution B/D#.")
            })

        if "heroic_lift_cadence" in sec:
            h_data = sec["heroic_lift_cadence"]
            chords = h_data["chords"]
            progressions.append({
                "id": "chappell_roan_good_luck_babe_heroic_cadence",
                "title": "Good Luck, Babe!",
                "artist": "Chappell Roan",
                "section": "bridge_climax",
                "key": meta.get("key", "B Major"),
                "mode": "Aeolian Modal Interchange / Major",
                "bpm": meta.get("tempo_bpm", 117),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": "1 chord per measure, culminating in double tonic",
                "roman_numerals": "bVI - bVII - I - I",
                "roots": [c["root"] for c in chords],
                "types": ["maj", "maj", "maj", "maj"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["synthpop", "heroic_cadence", "80s_pop", "anthemic_pop", "modal_borrowing"],
                "description": h_data.get("description", "The iconic double whole-step ascending bVI -> bVII -> I heroic lift.")
            })

    # Block 2: Sabrina Carpenter - Espresso
    if len(harm_blocks) > 2 and "metadata" in harm_blocks[2]:
        b2 = harm_blocks[2]
        meta = b2["metadata"]
        sec = b2.get("sectional_progressions", {})
        if "main_funk_groove" in sec:
            m_data = sec["main_funk_groove"]
            chords = m_data["chords"]
            progressions.append({
                "id": "sabrina_carpenter_espresso_funk_groove",
                "title": "Espresso",
                "artist": "Sabrina Carpenter",
                "section": "chorus_main",
                "key": meta.get("key", "C Major / D Dorian"),
                "mode": "Dorian / Major",
                "bpm": meta.get("tempo_bpm", 103),
                "time_signature": meta.get("time_signature", "4/4"),
                "harmonic_rhythm": meta.get("harmonic_rhythm", "Syncopated funk micro-rhythm"),
                "roman_numerals": "iv7 - v7 - i7 - iv9 - IV9 - i7",
                "roots": [c["root"] for c in chords],
                "types": ["min7", "min7", "min7", "min9", "dom9", "min7"],
                "bass_notes": [c["bass_note"] for c in chords],
                "chords": chords,
                "style_tags": ["dreamy_pop", "funk_pop", "disco_pop", "dance_pop", "retro_pop"],
                "description": m_data.get("description", "Dorian/Funk minor 7th to dominant 9th syncopated comping on upper string sets.")
            })

        # Add diatonic C Major interpretation: Fmaj7 - G - Em7 - Am7 (IVmaj7 - V - iii7 - vi7)
        progressions.append({
            "id": "sabrina_carpenter_espresso_diatonic_hook",
            "title": "Espresso (Diatonic Hook)",
            "artist": "Sabrina Carpenter",
            "section": "chorus_diatonic",
            "key": "C Major",
            "mode": "Major",
            "bpm": 103,
            "time_signature": "4/4",
            "harmonic_rhythm": "2 beats per chord / 1 chord per 2 beats",
            "roman_numerals": "IVmaj7 - V - iii7 - vi7",
            "roots": ["F", "G", "E", "A"],
            "types": ["maj7", "maj", "min7", "min7"],
            "bass_notes": ["F", "G", "E", "A"],
            "chords": [
                {
                    "measure": 1, "chord_symbol": "Fmaj7", "roman_numeral": "IVmaj7", "root": "F", "bass_note": "F", "bass_midi": 41,
                    "duration_beats": 2, "close_voicing": [53, 57, 60, 64], "drop2_voicing": [48, 53, 57, 64], "drop4_voicing": [41, 57, 60, 64]
                },
                {
                    "measure": 1, "chord_symbol": "G", "roman_numeral": "V", "root": "G", "bass_note": "G", "bass_midi": 43,
                    "duration_beats": 2, "close_voicing": [55, 59, 62, 67], "drop2_voicing": [50, 55, 59, 67], "drop4_voicing": [43, 59, 62, 67]
                },
                {
                    "measure": 2, "chord_symbol": "Em7", "roman_numeral": "iii7", "root": "E", "bass_note": "E", "bass_midi": 40,
                    "duration_beats": 2, "close_voicing": [52, 55, 59, 62], "drop2_voicing": [47, 52, 55, 62], "drop4_voicing": [40, 55, 59, 62]
                },
                {
                    "measure": 2, "chord_symbol": "Am7", "roman_numeral": "vi7", "root": "A", "bass_note": "A", "bass_midi": 45,
                    "duration_beats": 2, "close_voicing": [57, 60, 64, 67], "drop2_voicing": [52, 57, 60, 67], "drop4_voicing": [45, 60, 64, 67]
                }
            ],
            "style_tags": ["dreamy_pop", "funk_pop", "radio_pop", "dance_pop"],
            "description": "The irresistible four-chord pop cycle underlying the main vocal chorus of Espresso."
        })

    # Block 3: Taylor Swift - Fortnight & Cruel Summer
    if len(harm_blocks) > 3:
        b3 = harm_blocks[3]
        if "fortnight" in b3:
            f_data = b3["fortnight"]
            f_meta = f_data.get("metadata", {})
            f_chords = f_data.get("progression", [])
            progressions.append({
                "id": "taylor_swift_fortnight_pedal_loop",
                "title": "Fortnight (feat. Post Malone)",
                "artist": "Taylor Swift",
                "section": "main_loop",
                "key": f_meta.get("key", "B Major"),
                "mode": "Major",
                "bpm": f_meta.get("tempo_bpm", 96),
                "time_signature": f_meta.get("time_signature", "4/4"),
                "harmonic_rhythm": f_meta.get("harmonic_rhythm", "1 chord per measure"),
                "roman_numerals": "IV - V - iii - vi",
                "roots": [c["root"] for c in f_chords],
                "types": ["add9", "sus4", "min7", "min7"],
                "bass_notes": [c["bass_note"] for c in f_chords],
                "chords": f_chords,
                "style_tags": ["synthpop", "dreamy_pop", "ambient_pop", "indie_pop", "pedal_drone"],
                "description": "Suspended synth drone on F#4 and B4 anchoring an emotional IV - V - iii - vi cycle."
            })

        if "cruel_summer" in b3:
            cs_data = b3["cruel_summer"]
            cs_meta = cs_data.get("metadata", {})
            cs_chords = cs_data.get("bridge_anthem_progression", [])
            progressions.append({
                "id": "taylor_swift_cruel_summer_bridge_anthem",
                "title": "Cruel Summer",
                "artist": "Taylor Swift",
                "section": "bridge_anthem",
                "key": cs_meta.get("key", "A Major"),
                "mode": "Major",
                "bpm": cs_meta.get("tempo_bpm", 170),
                "time_signature": cs_meta.get("time_signature", "4/4"),
                "harmonic_rhythm": cs_meta.get("harmonic_rhythm", "2 measures per chord"),
                "roman_numerals": "I - iii - vi - IV",
                "roots": [c["root"] for c in cs_chords],
                "types": ["maj", "min", "min", "maj"],
                "bass_notes": [c["bass_note"] for c in cs_chords],
                "chords": cs_chords,
                "style_tags": ["synthpop", "anthemic_pop", "dance_pop", "bright_pop", "power_pop"],
                "description": "Anthemic driving synthpop progression with pulsing root pedal notes in the bass register."
            })

    # Block 4: Post Malone & Morgan Wallen - I Had Some Help
    if len(harm_blocks) > 4 and "metadata" in harm_blocks[4]:
        b4 = harm_blocks[4]
        meta = b4["metadata"]
        chords = b4.get("progression", [])
        progressions.append({
            "id": "post_malone_morgan_wallen_i_had_some_help",
            "title": "I Had Some Help (feat. Morgan Wallen)",
            "artist": "Post Malone & Morgan Wallen",
            "section": "main_chorus",
            "key": meta.get("key", "C Major"),
            "mode": "Major",
            "bpm": meta.get("tempo_bpm", 128),
            "time_signature": meta.get("time_signature", "4/4"),
            "harmonic_rhythm": meta.get("harmonic_rhythm", "2 beats per chord (High velocity)"),
            "roman_numerals": "IV - I - vi - V",
            "roots": [c["root"] for c in chords],
            "types": ["maj", "maj", "min", "maj"],
            "bass_notes": [c["bass_note"] for c in chords],
            "chords": chords,
            "style_tags": ["country_pop", "radio_pop", "nashville_pop", "anthemic_pop", "bright_pop"],
            "description": "High-velocity Nashville 2-beat subdominant launch providing continuous kinetic drive."
        })

    # Additional hit progressions from vocal & dance reports
    # Sabrina Carpenter - Please Please Please
    progressions.append({
        "id": "sabrina_carpenter_please_please_please",
        "title": "Please Please Please",
        "artist": "Sabrina Carpenter",
        "section": "chorus",
        "key": "A Major",
        "mode": "Major / Minor Plagal Cadence",
        "bpm": 107,
        "time_signature": "4/4",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "I - iii - vi - IV - iv",
        "roots": ["A", "C#", "F#", "D", "D"],
        "types": ["maj", "min", "min", "maj", "min"],
        "bass_notes": ["A", "C#", "F#", "D", "D"],
        "chords": [
            {"chord_symbol": "A", "roman_numeral": "I", "root": "A", "bass_note": "A", "bass_midi": 45, "duration_beats": 4, "close_voicing": [57, 61, 64], "drop2_voicing": [52, 57, 61, 64], "drop4_voicing": [45, 61, 64]},
            {"chord_symbol": "C#m", "roman_numeral": "iii", "root": "C#", "bass_note": "C#", "bass_midi": 49, "duration_beats": 4, "close_voicing": [61, 64, 68], "drop2_voicing": [56, 61, 64, 68], "drop4_voicing": [49, 64, 68]},
            {"chord_symbol": "F#m", "roman_numeral": "vi", "root": "F#", "bass_note": "F#", "bass_midi": 42, "duration_beats": 4, "close_voicing": [54, 57, 61], "drop2_voicing": [50, 54, 57, 61], "drop4_voicing": [42, 57, 61]},
            {"chord_symbol": "D", "roman_numeral": "IV", "root": "D", "bass_note": "D", "bass_midi": 50, "duration_beats": 4, "close_voicing": [50, 54, 57], "drop2_voicing": [45, 50, 54, 57], "drop4_voicing": [38, 54, 57]},
            {"chord_symbol": "Dm", "roman_numeral": "iv", "root": "D", "bass_note": "D", "bass_midi": 50, "duration_beats": 4, "close_voicing": [50, 53, 57], "drop2_voicing": [45, 50, 53, 57], "drop4_voicing": [38, 53, 57]}
        ],
        "style_tags": ["dreamy_pop", "synth_country", "retro_pop", "indie_pop", "minor_plagal"],
        "description": "Jack Antonoff synth-country progression highlighted by the emotional minor plagal cadence iv (Dm)."
    })

    # Billie Eilish - Lunch
    progressions.append({
        "id": "billie_eilish_lunch",
        "title": "Lunch",
        "artist": "Billie Eilish",
        "section": "main_groove",
        "key": "E Minor",
        "mode": "Dorian / Minor",
        "bpm": 125,
        "time_signature": "4/4",
        "harmonic_rhythm": "Syncopated 4-bar vamp",
        "roman_numerals": "i - III - IV - i",
        "roots": ["E", "G", "A", "E"],
        "types": ["min", "maj", "maj", "min"],
        "bass_notes": ["E", "G", "A", "E"],
        "chords": [
            {"chord_symbol": "Em", "roman_numeral": "i", "root": "E", "bass_note": "E", "bass_midi": 40, "duration_beats": 4, "close_voicing": [52, 55, 59], "drop2_voicing": [47, 52, 55, 59], "drop4_voicing": [40, 55, 59]},
            {"chord_symbol": "G", "roman_numeral": "III", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 4, "close_voicing": [55, 59, 62], "drop2_voicing": [50, 55, 59, 62], "drop4_voicing": [43, 59, 62]},
            {"chord_symbol": "A", "roman_numeral": "IV", "root": "A", "bass_note": "A", "bass_midi": 45, "duration_beats": 4, "close_voicing": [57, 61, 64], "drop2_voicing": [52, 57, 61, 64], "drop4_voicing": [45, 61, 64]},
            {"chord_symbol": "Em", "roman_numeral": "i", "root": "E", "bass_note": "E", "bass_midi": 40, "duration_beats": 4, "close_voicing": [52, 55, 59], "drop2_voicing": [47, 52, 55, 59], "drop4_voicing": [40, 55, 59]}
        ],
        "style_tags": ["alt_pop", "dark_pop", "minimal_groove", "indie_pop"],
        "description": "Heavy syncopated E minor bassline vamp with Dorian IV lift."
    })

    # Billie Eilish - Chihiro
    progressions.append({
        "id": "billie_eilish_chihiro",
        "title": "Chihiro",
        "artist": "Billie Eilish",
        "section": "chorus_drop",
        "key": "B Minor",
        "mode": "Minor",
        "bpm": 110,
        "time_signature": "4/4",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "i9 - VImaj7 - iv7 - v7",
        "roots": ["B", "G", "E", "F#"],
        "types": ["min9", "maj7", "min7", "min7"],
        "bass_notes": ["B", "G", "E", "F#"],
        "chords": [
            {"chord_symbol": "Bm9", "roman_numeral": "i9", "root": "B", "bass_note": "B", "bass_midi": 47, "duration_beats": 4, "close_voicing": [47, 50, 54, 57, 61], "drop2_voicing": [42, 47, 50, 54, 61], "drop4_voicing": [35, 50, 54, 57, 61]},
            {"chord_symbol": "Gmaj7", "roman_numeral": "VImaj7", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 4, "close_voicing": [55, 59, 62, 66], "drop2_voicing": [50, 55, 59, 66], "drop4_voicing": [43, 59, 62, 66]},
            {"chord_symbol": "Em7", "roman_numeral": "iv7", "root": "E", "bass_note": "E", "bass_midi": 40, "duration_beats": 4, "close_voicing": [52, 55, 59, 62], "drop2_voicing": [47, 52, 55, 62], "drop4_voicing": [40, 55, 59, 62]},
            {"chord_symbol": "F#m7", "roman_numeral": "v7", "root": "F#", "bass_note": "F#", "bass_midi": 42, "duration_beats": 4, "close_voicing": [54, 57, 61, 64], "drop2_voicing": [49, 54, 57, 64], "drop4_voicing": [42, 57, 61, 64]}
        ],
        "style_tags": ["dreamy_pop", "alt_pop", "deep_house_pop", "atmospheric_pop"],
        "description": "Hypnotic, reverberant 4-chord house/indie-pop loop in B minor."
    })

    # Chappell Roan - Pink Pony Club
    progressions.append({
        "id": "chappell_roan_pink_pony_club",
        "title": "Pink Pony Club",
        "artist": "Chappell Roan",
        "section": "chorus",
        "key": "F# Major",
        "mode": "Major",
        "bpm": 112,
        "time_signature": "4/4",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "I - IV - vi - V",
        "roots": ["F#", "B", "D#", "C#"],
        "types": ["maj", "maj", "min", "maj"],
        "bass_notes": ["F#", "B", "D#", "C#"],
        "chords": [
            {"chord_symbol": "F#", "roman_numeral": "I", "root": "F#", "bass_note": "F#", "bass_midi": 42, "duration_beats": 4, "close_voicing": [54, 58, 61], "drop2_voicing": [49, 54, 58, 61], "drop4_voicing": [42, 58, 61]},
            {"chord_symbol": "B", "roman_numeral": "IV", "root": "B", "bass_note": "B", "bass_midi": 47, "duration_beats": 4, "close_voicing": [59, 63, 66], "drop2_voicing": [54, 59, 63, 66], "drop4_voicing": [47, 63, 66]},
            {"chord_symbol": "D#m", "roman_numeral": "vi", "root": "D#", "bass_note": "D#", "bass_midi": 51, "duration_beats": 4, "close_voicing": [51, 54, 58], "drop2_voicing": [46, 51, 54, 58], "drop4_voicing": [39, 54, 58]},
            {"chord_symbol": "C#", "roman_numeral": "V", "root": "C#", "bass_note": "C#", "bass_midi": 49, "duration_beats": 4, "close_voicing": [49, 53, 56], "drop2_voicing": [44, 49, 53, 56], "drop4_voicing": [37, 53, 56]}
        ],
        "style_tags": ["synthpop", "glam_pop", "disco_pop", "anthemic_pop"],
        "description": "Euphoric, bittersweet disco-pop anthem progression."
    })

    # Benson Boone - Beautiful Things
    progressions.append({
        "id": "benson_boone_beautiful_things",
        "title": "Beautiful Things",
        "artist": "Benson Boone",
        "section": "chorus_drop",
        "key": "Bb Major",
        "mode": "Major",
        "bpm": 105,
        "time_signature": "6/8 (12/8 feel)",
        "harmonic_rhythm": "1 measure per chord",
        "roman_numerals": "I - V6 - vi - IV",
        "roots": ["Bb", "F", "G", "Eb"],
        "types": ["maj", "maj/3rd", "min", "maj"],
        "bass_notes": ["Bb", "A", "G", "Eb"],
        "chords": [
            {"chord_symbol": "Bb", "roman_numeral": "I", "root": "Bb", "bass_note": "Bb", "bass_midi": 46, "duration_beats": 6, "close_voicing": [58, 62, 65], "drop2_voicing": [53, 58, 62, 65], "drop4_voicing": [46, 62, 65]},
            {"chord_symbol": "F/A", "roman_numeral": "V6", "root": "F", "bass_note": "A", "bass_midi": 45, "duration_beats": 6, "close_voicing": [57, 60, 65], "drop2_voicing": [53, 57, 60, 65], "drop4_voicing": [45, 60, 65]},
            {"chord_symbol": "Gm", "roman_numeral": "vi", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 6, "close_voicing": [55, 58, 62], "drop2_voicing": [50, 55, 58, 62], "drop4_voicing": [43, 58, 62]},
            {"chord_symbol": "Eb", "roman_numeral": "IV", "root": "Eb", "bass_note": "Eb", "bass_midi": 39, "duration_beats": 6, "close_voicing": [51, 55, 58], "drop2_voicing": [46, 51, 55, 58], "drop4_voicing": [39, 55, 58]}
        ],
        "style_tags": ["pop_rock", "power_ballad", "anthemic_pop", "stadium_rock"],
        "description": "Explosive dynamic shift from intimate acoustic ballad into roaring stadium pop-rock drop."
    })

    # Teddy Swims - Lose Control
    progressions.append({
        "id": "teddy_swims_lose_control",
        "title": "Lose Control",
        "artist": "Teddy Swims",
        "section": "chorus",
        "key": "C Minor",
        "mode": "Minor",
        "bpm": 80,
        "time_signature": "6/8 / 12/8 Soul",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "i - VI - VII - III - V7",
        "roots": ["C", "Ab", "Bb", "Eb", "G"],
        "types": ["min", "maj", "maj", "maj", "dom7"],
        "bass_notes": ["C", "Ab", "Bb", "Eb", "G"],
        "chords": [
            {"chord_symbol": "Cm", "roman_numeral": "i", "root": "C", "bass_note": "C", "bass_midi": 36, "duration_beats": 6, "close_voicing": [48, 51, 55], "drop2_voicing": [43, 48, 51, 55], "drop4_voicing": [36, 51, 55]},
            {"chord_symbol": "Ab", "roman_numeral": "VI", "root": "Ab", "bass_note": "Ab", "bass_midi": 44, "duration_beats": 6, "close_voicing": [56, 60, 63], "drop2_voicing": [51, 56, 60, 63], "drop4_voicing": [44, 60, 63]},
            {"chord_symbol": "Bb", "roman_numeral": "VII", "root": "Bb", "bass_note": "Bb", "bass_midi": 46, "duration_beats": 6, "close_voicing": [58, 62, 65], "drop2_voicing": [53, 58, 62, 65], "drop4_voicing": [46, 62, 65]},
            {"chord_symbol": "Eb", "roman_numeral": "III", "root": "Eb", "bass_note": "Eb", "bass_midi": 39, "duration_beats": 6, "close_voicing": [51, 55, 58], "drop2_voicing": [46, 51, 55, 58], "drop4_voicing": [39, 55, 58]},
            {"chord_symbol": "G7", "roman_numeral": "V7", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 6, "close_voicing": [55, 59, 62, 65], "drop2_voicing": [50, 55, 59, 65], "drop4_voicing": [43, 59, 62, 65]}
        ],
        "style_tags": ["soul_pop", "rnb_pop", "blues_pop", "retro_soul"],
        "description": "Deep 6/8 retro-soul chord progression rich with gospel dominant tension."
    })

    # Charli XCX - 360 / Apple
    progressions.append({
        "id": "charli_xcx_360_minimal_club",
        "title": "360",
        "artist": "Charli XCX",
        "section": "main_groove",
        "key": "F# Minor",
        "mode": "Minor",
        "bpm": 120,
        "time_signature": "4/4",
        "harmonic_rhythm": "2 beats per chord",
        "roman_numerals": "i - III - VII - i",
        "roots": ["F#", "A", "E", "F#"],
        "types": ["min", "maj", "maj", "min"],
        "bass_notes": ["F#", "A", "E", "F#"],
        "chords": [
            {"chord_symbol": "F#m", "roman_numeral": "i", "root": "F#", "bass_note": "F#", "bass_midi": 42, "duration_beats": 2, "close_voicing": [54, 57, 61], "drop2_voicing": [45, 54, 57, 61], "drop4_voicing": [42, 57, 61]},
            {"chord_symbol": "A", "roman_numeral": "III", "root": "A", "bass_note": "A", "bass_midi": 45, "duration_beats": 2, "close_voicing": [57, 61, 64], "drop2_voicing": [52, 57, 61, 64], "drop4_voicing": [45, 61, 64]},
            {"chord_symbol": "E", "roman_numeral": "VII", "root": "E", "bass_note": "E", "bass_midi": 40, "duration_beats": 2, "close_voicing": [52, 56, 59], "drop2_voicing": [47, 52, 56, 59], "drop4_voicing": [40, 56, 59]},
            {"chord_symbol": "F#m", "roman_numeral": "i", "root": "F#", "bass_note": "F#", "bass_midi": 42, "duration_beats": 2, "close_voicing": [54, 57, 61], "drop2_voicing": [45, 54, 57, 61], "drop4_voicing": [42, 57, 61]}
        ],
        "style_tags": ["hyperpop", "electroclash", "club_pop", "dance_pop"],
        "description": "Minimalist monophonic club stabs from the Brat sound architecture."
    })

    # The Weeknd - Dancing in the Flames
    progressions.append({
        "id": "the_weeknd_dancing_in_the_flames",
        "title": "Dancing in the Flames",
        "artist": "The Weeknd",
        "section": "chorus",
        "key": "D Minor",
        "mode": "Minor",
        "bpm": 120,
        "time_signature": "4/4",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "i - v - VII - IV",
        "roots": ["D", "A", "C", "G"],
        "types": ["min", "min", "maj", "maj"],
        "bass_notes": ["D", "A", "C", "G"],
        "chords": [
            {"chord_symbol": "Dm", "roman_numeral": "i", "root": "D", "bass_note": "D", "bass_midi": 38, "duration_beats": 4, "close_voicing": [50, 53, 57], "drop2_voicing": [45, 50, 53, 57], "drop4_voicing": [38, 53, 57]},
            {"chord_symbol": "Am", "roman_numeral": "v", "root": "A", "bass_note": "A", "bass_midi": 45, "duration_beats": 4, "close_voicing": [57, 60, 64], "drop2_voicing": [52, 57, 60, 64], "drop4_voicing": [45, 60, 64]},
            {"chord_symbol": "C", "roman_numeral": "VII", "root": "C", "bass_note": "C", "bass_midi": 48, "duration_beats": 4, "close_voicing": [48, 52, 55], "drop2_voicing": [43, 48, 52, 55], "drop4_voicing": [36, 52, 55]},
            {"chord_symbol": "G", "roman_numeral": "IV", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 4, "close_voicing": [55, 59, 62], "drop2_voicing": [50, 55, 59, 62], "drop4_voicing": [43, 59, 62]}
        ],
        "style_tags": ["synthwave", "retro_synthpop", "80s_pop", "dance_pop"],
        "description": "Max Martin 80s retro-futuristic driving synthpop chorus progression."
    })

    # Dua Lipa - Houdini
    progressions.append({
        "id": "dua_lipa_houdini",
        "title": "Houdini",
        "artist": "Dua Lipa",
        "section": "main_groove",
        "key": "D Minor",
        "mode": "Minor",
        "bpm": 117,
        "time_signature": "4/4",
        "harmonic_rhythm": "1 chord per measure",
        "roman_numerals": "i - VII - iv - VI",
        "roots": ["D", "C", "G", "Bb"],
        "types": ["min", "maj", "min", "maj"],
        "bass_notes": ["D", "C", "G", "Bb"],
        "chords": [
            {"chord_symbol": "Dm", "roman_numeral": "i", "root": "D", "bass_note": "D", "bass_midi": 38, "duration_beats": 4, "close_voicing": [50, 53, 57], "drop2_voicing": [45, 50, 53, 57], "drop4_voicing": [38, 53, 57]},
            {"chord_symbol": "C", "roman_numeral": "VII", "root": "C", "bass_note": "C", "bass_midi": 48, "duration_beats": 4, "close_voicing": [48, 52, 55], "drop2_voicing": [43, 48, 52, 55], "drop4_voicing": [36, 52, 55]},
            {"chord_symbol": "Gm", "roman_numeral": "iv", "root": "G", "bass_note": "G", "bass_midi": 43, "duration_beats": 4, "close_voicing": [55, 58, 62], "drop2_voicing": [50, 55, 58, 62], "drop4_voicing": [43, 58, 62]},
            {"chord_symbol": "Bb", "roman_numeral": "VI", "root": "Bb", "bass_note": "Bb", "bass_midi": 46, "duration_beats": 4, "close_voicing": [58, 62, 65], "drop2_voicing": [53, 58, 62, 65], "drop4_voicing": [46, 62, 65]}
        ],
        "style_tags": ["nu_disco", "psych_pop", "dance_pop", "funk_pop"],
        "description": "Kevin Parker psych-pop disco groove with slap bass and acid synth layers."
    })

    # --------------------------------------------------------------------------
    # 2. MELODIC MOTIFS
    # --------------------------------------------------------------------------
    # We have 9 vocal blocks from modern_vocal_hooks_and_melodic_phrasing.md
    for b in vocal_blocks[:9]:
        tid = b.get("track_id", "")
        title = b.get("title", "")
        artist = b.get("artist", "")
        key = b.get("key", "")
        bpm = b.get("bpm", 120)
        time_sig = b.get("time_signature", "4/4")
        start_deg = b.get("hook_starting_degree", 1)
        pickup = b.get("pickup_beat", 4.5)
        climax = b.get("climax_peak", {})
        midi_seq = b.get("chorus_hook_midi", [])
        
        # Determine style tags
        stags = ["billboard_hit", "vocal_hook"]
        if "Sabrina" in artist:
            stags.extend(["dreamy_pop", "funk_pop", "conversational_pop", "earworm"])
        elif "Billie" in artist:
            stags.extend(["dreamy_pop", "alt_pop", "intimate_pop", "earworm"])
        elif "Chappell" in artist:
            stags.extend(["synthpop", "glam_pop", "anthemic_pop", "high_belt"])
        elif "Benson" in artist:
            stags.extend(["pop_rock", "power_ballad", "explosive_hook"])
        elif "Teddy" in artist:
            stags.extend(["soul_pop", "rnb_pop", "blues_belt"])

        melodic_motifs.append({
            "id": f"{tid}_hook_motif",
            "title": title,
            "artist": artist,
            "key": key,
            "bpm": bpm,
            "time_signature": time_sig,
            "starting_scale_degree": start_deg,
            "pickup_beat": pickup,
            "contour_type": "Disjunct leap to conjunct cascade" if "Espresso" in title or "Good Luck" in title else "Conjunct arch",
            "syncopation": {
                "pickup_location": pickup,
                "anticipation": "8th and 16th note pushes displacing beat 1.0"
            },
            "climax_target": {
                "pitch": climax.get("pitch"),
                "midi_number": climax.get("midi_number"),
                "scale_degree": climax.get("scale_degree"),
                "bar_location": climax.get("bar_location"),
                "lyric": climax.get("lyric"),
                "resolution_sequence": climax.get("resolution_sequence", [])
            },
            "midi_sequence": midi_seq,
            "style_tags": stags
        })

    # --------------------------------------------------------------------------
    # 3. BASS GROOVES
    # --------------------------------------------------------------------------
    # From modern_electropop_dance_architectures.md
    for b in dance_blocks:
        tid = b.get("template_id")
        genre = b.get("genre")
        tempo = b.get("tempo")
        ts = b.get("time_signature", "4/4")
        gchar = b.get("groove_characteristics", {})
        inst = b.get("instruments", {})
        bass = inst.get("bassline", {})
        drums = inst.get("drums", {})

        artist_ref = "Various"
        title_ref = tid
        stags = [genre, "bass_groove"]
        if "brat" in tid:
            artist_ref = "Charli XCX"
            title_ref = "360 / Apple / Von Dutch (Brat Sound)"
            stags.extend(["hyperpop", "electroclash", "club_pop"])
        elif "weeknd" in tid:
            artist_ref = "The Weeknd"
            title_ref = "Dancing in the Flames / Blinding Lights"
            stags.extend(["synthwave", "retro_synthpop", "80s_pop"])
        elif "dua" in tid:
            artist_ref = "Dua Lipa & Kevin Parker"
            title_ref = "Houdini / Training Season"
            stags.extend(["nu_disco", "psych_pop", "funk_pop"])

        bass_grooves.append({
            "id": tid,
            "title": title_ref,
            "artist": artist_ref,
            "genre": genre,
            "tempo": tempo,
            "time_signature": ts,
            "groove_characteristics": gchar,
            "patch_type": bass.get("patch_type", "monosynth"),
            "cutoff_hz": bass.get("cutoff_hz", 1500),
            "resonance_q": bass.get("resonance_q", 3.0),
            "envelope_decay_ms": bass.get("envelope_decay_ms", 150),
            "steps": bass.get("events", []),
            "drum_pocket": drums,
            "style_tags": stags
        })

    # Add Espresso Funk Bassline Groove
    bass_grooves.append({
        "id": "sabrina_carpenter_espresso_funk_bass",
        "title": "Espresso (Funk Pocket Bass)",
        "artist": "Sabrina Carpenter",
        "genre": "nu_disco_funk",
        "tempo": 103,
        "time_signature": "4/4",
        "groove_characteristics": {
            "swing_percentage": 54.0,
            "humanize_ms_jitter": 3.0,
            "pocket_description": "Laid-back funk pocket with 16th-note ghost pops and syncopated root octaves"
        },
        "patch_type": "vintage_p_bass_with_sub",
        "cutoff_hz": 2200,
        "resonance_q": 2.2,
        "envelope_decay_ms": 220,
        "steps": [
            {"step": 1, "note": "F1", "velocity": 112, "gate_ratio": 0.40, "offset_ms": 0.0},
            {"step": 2, "note": None, "velocity": 0, "gate_ratio": 0.0},
            {"step": 3, "note": "F2", "velocity": 95, "gate_ratio": 0.25, "offset_ms": 4.5},
            {"step": 4, "note": "F1", "velocity": 60, "gate_ratio": 0.15, "offset_ms": 5.0},
            {"step": 5, "note": None, "velocity": 0, "gate_ratio": 0.0},
            {"step": 6, "note": "G1", "velocity": 118, "gate_ratio": 0.45, "offset_ms": 3.5},
            {"step": 7, "note": None, "velocity": 0, "gate_ratio": 0.0},
            {"step": 8, "note": "G2", "velocity": 92, "gate_ratio": 0.20, "offset_ms": 4.0},
            {"step": 9, "note": "E1", "velocity": 115, "gate_ratio": 0.40, "offset_ms": 0.0},
            {"step": 10, "note": None, "velocity": 0, "gate_ratio": 0.0},
            {"step": 11, "note": "E2", "velocity": 96, "gate_ratio": 0.25, "offset_ms": 3.8},
            {"step": 12, "note": "E1", "velocity": 58, "gate_ratio": 0.15, "offset_ms": 5.2},
            {"step": 13, "note": "A1", "velocity": 120, "gate_ratio": 0.50, "offset_ms": 0.0},
            {"step": 14, "note": None, "velocity": 0, "gate_ratio": 0.0},
            {"step": 15, "note": "C2", "velocity": 104, "gate_ratio": 0.35, "offset_ms": 2.0},
            {"step": 16, "note": "D2", "velocity": 90, "gate_ratio": 0.25, "offset_ms": 3.0}
        ],
        "drum_pocket": {
            "kick": {"steps": [1, 5, 9, 13], "velocity": [124, 120, 124, 118]},
            "snare": {"steps": [5, 13], "velocity": [122, 125], "timing_offsets_ms": [0.0, 0.0]}
        },
        "style_tags": ["dreamy_pop", "funk_pop", "nu_disco", "dance_pop"]
    })

    # Assemble Unified Database
    db = {
        "metadata": {
            "database_name": "Billboard Hot 100 Knowledge Base (2024-2026)",
            "version": "1.0.0",
            "compiled_by": "Billboard Hit Knowledge Base Integrator",
            "total_progressions": len(progressions),
            "total_melodic_motifs": len(melodic_motifs),
            "total_bass_grooves": len(bass_grooves),
            "artists_covered": list(sorted(set([p["artist"] for p in progressions] + [m["artist"] for m in melodic_motifs] + [b["artist"] for b in bass_grooves]))),
            "supported_styles": list(sorted(set([s for p in progressions for s in p["style_tags"]] + [s for m in melodic_motifs for s in m["style_tags"]])))
        },
        "progressions": progressions,
        "melodic_motifs": melodic_motifs,
        "bass_grooves": bass_grooves
    }

    os.makedirs(os.path.dirname(TARGET_DB), exist_ok=True)
    with open(TARGET_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

    print(f"Successfully compiled Billboard Hits Database to: {TARGET_DB}")
    print(f"  Progressions: {len(progressions)}")
    print(f"  Melodic Motifs: {len(melodic_motifs)}")
    print(f"  Bass Grooves: {len(bass_grooves)}")
    print(f"  Artists: {len(db['metadata']['artists_covered'])}")
    print(f"  Styles: {len(db['metadata']['supported_styles'])}")

if __name__ == "__main__":
    build_database()

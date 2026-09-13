# 80s Retrowave & Darksynth Drum Pattern Architecture

## 1. Analysis of Drum Elements

### Four-on-the-Floor Driving Kicks
The backbone of 80s Synthwave is the four-on-the-floor kick pattern. Kicks are typically synthesized (e.g., Linndrum, Roland TR-707, TR-808, Oberheim DMX) with a punchy transient and a short but fat decay. In Darksynth (e.g., Perturbator, Carpenter Brut), kicks are often layered with heavy distortion and aggressive parallel compression. The consistent 1, 5, 9, 13 (in 16-step) placement anchors the pulsing 16th-note basslines. Microtiming is usually dead on the grid for kicks to drive the sidechain compression, though slight negative offsets (-1ms to -3ms) can push the track forward.

### Half-Time Snare Drops (Beat 3 vs Beats 2 & 4)
While standard disco/dance beats place the snare on beats 2 and 4 (steps 5 and 13), half-time grooves place a massive, reverb-drenched snare exclusively on beat 3 (step 9). This effectively halves the perceived tempo while the 16th-note arpeggios keep the energy high. Snares are often heavily layered with gated reverb—a defining characteristic of the 80s sound.

### Ghost Snare Rolls
Ghost notes in Synthwave add humanization to rigid sequences. In Darksynth, tightly programmed 32nd-note or 64th-note snare rolls leading into the downbeat serve as aggressive fills. Velocities for ghost notes are generally kept low (30-60) and often have a slight positive microtiming offset (+3ms to +8ms) to simulate a drummer dragging slightly.

### Open Hi-Hat Pedal Chokes
A classic technique inherited from disco and early house is the off-beat open hi-hat (steps 3, 7, 11, 15), immediately choked by a closed hi-hat on the following step (or kick). This creates a sucking, pumping rhythm that locks perfectly with sidechained basslines. The open hat velocity is usually high and consistent (90-110).

### Tom Fills (Rototoms, Simmons Electronic Toms)
The definitive 80s tom fill utilizes Simmons SDS-V hex pad sounds (characterized by a distinct pitch drop/pew-pew sound) or Rototoms. Fills often cascade down in pitch across steps 13-16. They are heavily panned and drenched in gated reverb.

### Crash Cymbal Placement
Crashes hit squarely on step 1 of a new phrase (every 16, 32, or 64 steps). Sometimes they are anticipated by a 16th note (step 16 of the previous bar) to create urgency. They are often long, synthetic crashes (e.g., TR-909) or bright acoustic samples (Linndrum), layered with white noise bursts.

---

## 2. 16-Step Drum Groove Templates

Below are 10 structured 16-step patterns. Microtiming is in milliseconds (ms), and Velocity ranges from 1-127.

```json
[
  {
    "name": "Classic Synthwave 4/4",
    "bpm": 120,
    "steps": 16,
    "description": "The quintessential driving retrowave beat with off-beat hats.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 120, "microtiming_ms": 0},
          {"step": 5, "velocity": 115, "microtiming_ms": 0},
          {"step": 9, "velocity": 120, "microtiming_ms": 0},
          {"step": 13, "velocity": 115, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 110, "microtiming_ms": 2},
          {"step": 13, "velocity": 115, "microtiming_ms": 2}
        ]
      },
      {
        "instrument": "ClosedHat",
        "sequence": [
          {"step": 1, "velocity": 80, "microtiming_ms": 0},
          {"step": 5, "velocity": 80, "microtiming_ms": 0},
          {"step": 9, "velocity": 80, "microtiming_ms": 0},
          {"step": 13, "velocity": 80, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "OpenHat",
        "sequence": [
          {"step": 3, "velocity": 100, "microtiming_ms": -2},
          {"step": 7, "velocity": 100, "microtiming_ms": -2},
          {"step": 11, "velocity": 100, "microtiming_ms": -2},
          {"step": 15, "velocity": 100, "microtiming_ms": -2}
        ]
      }
    ]
  },
  {
    "name": "Darksynth Half-Time Heavy",
    "bpm": 105,
    "steps": 16,
    "description": "Sludging, heavy Darksynth groove with a huge beat 3 snare.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 127, "microtiming_ms": 0},
          {"step": 4, "velocity": 90, "microtiming_ms": 5},
          {"step": 11, "velocity": 110, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 9, "velocity": 127, "microtiming_ms": -1}
        ]
      },
      {
        "instrument": "ClosedHat",
        "sequence": [
          {"step": 1, "velocity": 100, "microtiming_ms": 0},
          {"step": 3, "velocity": 90, "microtiming_ms": 4},
          {"step": 5, "velocity": 105, "microtiming_ms": 0},
          {"step": 7, "velocity": 90, "microtiming_ms": 4},
          {"step": 9, "velocity": 100, "microtiming_ms": 0},
          {"step": 11, "velocity": 90, "microtiming_ms": 4},
          {"step": 13, "velocity": 105, "microtiming_ms": 0},
          {"step": 15, "velocity": 90, "microtiming_ms": 4}
        ]
      }
    ]
  },
  {
    "name": "Outrun Chase Scene",
    "bpm": 135,
    "steps": 16,
    "description": "Fast-paced, syncopated 16th-note hat driver.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 120, "microtiming_ms": -1},
          {"step": 5, "velocity": 110, "microtiming_ms": 0},
          {"step": 9, "velocity": 120, "microtiming_ms": -1},
          {"step": 13, "velocity": 110, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 115, "microtiming_ms": 1},
          {"step": 13, "velocity": 120, "microtiming_ms": 1}
        ]
      },
      {
        "instrument": "ClosedHat",
        "sequence": [
          {"step": 1, "velocity": 90, "microtiming_ms": 0},
          {"step": 2, "velocity": 70, "microtiming_ms": 3},
          {"step": 3, "velocity": 80, "microtiming_ms": -2},
          {"step": 4, "velocity": 70, "microtiming_ms": 3},
          {"step": 5, "velocity": 90, "microtiming_ms": 0},
          {"step": 6, "velocity": 70, "microtiming_ms": 3},
          {"step": 7, "velocity": 80, "microtiming_ms": -2},
          {"step": 8, "velocity": 70, "microtiming_ms": 3},
          {"step": 9, "velocity": 90, "microtiming_ms": 0},
          {"step": 10, "velocity": 70, "microtiming_ms": 3},
          {"step": 11, "velocity": 80, "microtiming_ms": -2},
          {"step": 12, "velocity": 70, "microtiming_ms": 3},
          {"step": 13, "velocity": 90, "microtiming_ms": 0},
          {"step": 14, "velocity": 70, "microtiming_ms": 3},
          {"step": 15, "velocity": 80, "microtiming_ms": -2},
          {"step": 16, "velocity": 70, "microtiming_ms": 3}
        ]
      }
    ]
  },
  {
    "name": "Simmons Tom Fill Groove",
    "bpm": 115,
    "steps": 16,
    "description": "Standard beat transitioning into a classic descending tom fill.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 120, "microtiming_ms": 0},
          {"step": 9, "velocity": 120, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 110, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "TomHigh",
        "sequence": [
          {"step": 13, "velocity": 115, "microtiming_ms": -2}
        ]
      },
      {
        "instrument": "TomMid",
        "sequence": [
          {"step": 14, "velocity": 110, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "TomLow",
        "sequence": [
          {"step": 15, "velocity": 105, "microtiming_ms": 2},
          {"step": 16, "velocity": 100, "microtiming_ms": 4}
        ]
      }
    ]
  },
  {
    "name": "Cyberpunk Syncopated",
    "bpm": 100,
    "steps": 16,
    "description": "Glitchy, offset kicks with ghost snare rolls for a modern cyberpunk feel.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 127, "microtiming_ms": 0},
          {"step": 4, "velocity": 85, "microtiming_ms": 5},
          {"step": 7, "velocity": 110, "microtiming_ms": 0},
          {"step": 10, "velocity": 90, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 120, "microtiming_ms": 0},
          {"step": 13, "velocity": 120, "microtiming_ms": 0},
          {"step": 15, "velocity": 45, "microtiming_ms": 8},
          {"step": 16, "velocity": 60, "microtiming_ms": 6}
        ]
      }
    ]
  },
  {
    "name": "Dreamwave Chill Beat",
    "bpm": 90,
    "steps": 16,
    "description": "Laid back, dragging snare with sparse kick programming.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 90, "microtiming_ms": 0},
          {"step": 11, "velocity": 75, "microtiming_ms": 5}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 85, "microtiming_ms": 15},
          {"step": 13, "velocity": 90, "microtiming_ms": 18}
        ]
      },
      {
        "instrument": "ClosedHat",
        "sequence": [
          {"step": 1, "velocity": 70, "microtiming_ms": 5},
          {"step": 5, "velocity": 70, "microtiming_ms": 5},
          {"step": 9, "velocity": 70, "microtiming_ms": 5},
          {"step": 13, "velocity": 70, "microtiming_ms": 5}
        ]
      }
    ]
  },
  {
    "name": "Darksynth Climax Blast",
    "bpm": 130,
    "steps": 16,
    "description": "Double kick intensity with crashing cymbals on the 1 and 9.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 127, "microtiming_ms": 0},
          {"step": 3, "velocity": 110, "microtiming_ms": 0},
          {"step": 5, "velocity": 127, "microtiming_ms": 0},
          {"step": 7, "velocity": 110, "microtiming_ms": 0},
          {"step": 9, "velocity": 127, "microtiming_ms": 0},
          {"step": 11, "velocity": 110, "microtiming_ms": 0},
          {"step": 13, "velocity": 127, "microtiming_ms": 0},
          {"step": 15, "velocity": 110, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 127, "microtiming_ms": -2},
          {"step": 13, "velocity": 127, "microtiming_ms": -2}
        ]
      },
      {
        "instrument": "CrashCymbal",
        "sequence": [
          {"step": 1, "velocity": 115, "microtiming_ms": 0},
          {"step": 9, "velocity": 105, "microtiming_ms": 0}
        ]
      }
    ]
  },
  {
    "name": "80s Pop Dance Beat",
    "bpm": 118,
    "steps": 16,
    "description": "Classic FM synthesis era pop beat with clap-layered snares.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 115, "microtiming_ms": 0},
          {"step": 5, "velocity": 105, "microtiming_ms": 0},
          {"step": 9, "velocity": 115, "microtiming_ms": 0},
          {"step": 11, "velocity": 90, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "SnareClap",
        "sequence": [
          {"step": 5, "velocity": 120, "microtiming_ms": 0},
          {"step": 13, "velocity": 120, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Shaker",
        "sequence": [
          {"step": 1, "velocity": 70, "microtiming_ms": 0},
          {"step": 3, "velocity": 90, "microtiming_ms": 2},
          {"step": 5, "velocity": 70, "microtiming_ms": 0},
          {"step": 7, "velocity": 90, "microtiming_ms": 2},
          {"step": 9, "velocity": 70, "microtiming_ms": 0},
          {"step": 11, "velocity": 90, "microtiming_ms": 2},
          {"step": 13, "velocity": 70, "microtiming_ms": 0},
          {"step": 15, "velocity": 90, "microtiming_ms": 2}
        ]
      }
    ]
  },
  {
    "name": "Retrowave Anticipation",
    "bpm": 125,
    "steps": 16,
    "description": "Pre-chorus buildup with crash anticipation on step 16.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 120, "microtiming_ms": 0},
          {"step": 5, "velocity": 120, "microtiming_ms": 0},
          {"step": 9, "velocity": 120, "microtiming_ms": 0},
          {"step": 13, "velocity": 120, "microtiming_ms": 0},
          {"step": 15, "velocity": 100, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 115, "microtiming_ms": 0},
          {"step": 13, "velocity": 115, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "CrashCymbal",
        "sequence": [
          {"step": 16, "velocity": 120, "microtiming_ms": -5}
        ]
      }
    ]
  },
  {
    "name": "Darksynth Brutal Groove",
    "bpm": 110,
    "steps": 16,
    "description": "Aggressive minimal groove relying on heavy saturation.",
    "tracks": [
      {
        "instrument": "Kick",
        "sequence": [
          {"step": 1, "velocity": 127, "microtiming_ms": 0},
          {"step": 7, "velocity": 110, "microtiming_ms": 0},
          {"step": 11, "velocity": 120, "microtiming_ms": 0}
        ]
      },
      {
        "instrument": "Snare",
        "sequence": [
          {"step": 5, "velocity": 127, "microtiming_ms": 3},
          {"step": 13, "velocity": 127, "microtiming_ms": 3}
        ]
      },
      {
        "instrument": "RideCymbal",
        "sequence": [
          {"step": 1, "velocity": 90, "microtiming_ms": 0},
          {"step": 5, "velocity": 105, "microtiming_ms": 0},
          {"step": 9, "velocity": 90, "microtiming_ms": 0},
          {"step": 13, "velocity": 105, "microtiming_ms": 0}
        ]
      }
    ]
  }
]
```

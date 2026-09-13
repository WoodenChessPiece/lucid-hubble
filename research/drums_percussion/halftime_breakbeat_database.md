# Halftime & Breakbeat Database

## Breaking the 4/4 Monotony: Rhythmic Subversion in Electronic Music
Continuous 4/4 electronic albums can suffer from rhythmic fatigue. Artists like The Prodigy, Pendulum, Kavinsky, and The Glitch Mob intentionally break this monotony by injecting halftime sections, breakbeat interpolations, and heavily syncopated grooves.

### The Amen Break and Its Mutations
The Amen Break, originally a 4-bar drum solo by G.C. Coleman, has been sliced, pitched, and rearranged to form the backbone of jungle, drum & bass, and breakbeat hardcore. In a typical variation, kicks provide a stable syncopation on beats 1 and the 'and' of 2, while the snare sits comfortably on beats 2 and 4 (or 3 in a halftime context), surrounded by a flurry of ghost notes.

### Syncopated Kick Displacements
Displacing the kick drum introduces immediate groove and swing. For example, moving a kick from the downbeat to the 16th note 'a' of beat 1 (the 4th 16th note) or the 'e' of beat 3 (the 2nd 16th note of beat 3) creates a "push" or "pull" effect against the rigid grid, forcing the listener's ear to re-evaluate the pulse.

### Swing Quantization
Swing (or shuffle) shifts the even 16th notes later in time, creating a triplet feel. Classic drum machines (like the MPC or TR-909) apply a percentage to this delay. In modern DAWs, this is often mathematically represented by delaying the 2nd and 4th 16th notes by varying millisecond amounts.

## MIDI Groove Maps (JSON)

```json
{
  "groove_maps": [
    {
      "id": "halftime_glitch_mob_style",
      "name": "Heavy Halftime (Glitch Mob Style)",
      "tempo": 90,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 127},
        {"instrument": "hihat_closed", "position": "1.1.1", "velocity": 90},
        {"instrument": "hihat_closed", "position": "1.1.3", "velocity": 70},
        {"instrument": "snare", "position": "1.3.1", "velocity": 120},
        {"instrument": "hihat_closed", "position": "1.3.1", "velocity": 90},
        {"instrument": "kick", "position": "1.3.4", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.3.3", "velocity": 70}
      ],
      "swing_percentage": 50
    },
    {
      "id": "classic_amen_variation",
      "name": "Amen Break Variation",
      "tempo": 170,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 120},
        {"instrument": "ride", "position": "1.1.1", "velocity": 90},
        {"instrument": "kick", "position": "1.1.3", "velocity": 100},
        {"instrument": "ride", "position": "1.1.3", "velocity": 85},
        {"instrument": "snare", "position": "1.2.1", "velocity": 127},
        {"instrument": "ride", "position": "1.2.1", "velocity": 90},
        {"instrument": "snare_ghost", "position": "1.2.4", "velocity": 50},
        {"instrument": "kick", "position": "1.3.3", "velocity": 110},
        {"instrument": "snare", "position": "1.4.1", "velocity": 127}
      ],
      "swing_percentage": 50
    },
    {
      "id": "two_step_garage",
      "name": "2-Step Garage Core",
      "tempo": 135,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 110},
        {"instrument": "kick", "position": "1.2.4", "velocity": 100},
        {"instrument": "snare", "position": "1.2.1", "velocity": 120},
        {"instrument": "snare", "position": "1.4.1", "velocity": 120},
        {"instrument": "hihat_closed", "position": "1.1.3", "velocity": 90},
        {"instrument": "hihat_open", "position": "1.3.3", "velocity": 105}
      ],
      "swing_percentage": 62
    },
    {
      "id": "syncopated_kick_displacement",
      "name": "16th Note Kick Displacement",
      "tempo": 120,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 127},
        {"instrument": "kick", "position": "1.1.4", "velocity": 115},
        {"instrument": "snare", "position": "1.2.1", "velocity": 120},
        {"instrument": "kick", "position": "1.3.2", "velocity": 110},
        {"instrument": "snare", "position": "1.4.1", "velocity": 120}
      ],
      "swing_percentage": 55
    },
    {
      "id": "pendulum_dnb_step",
      "name": "Arena DnB (Pendulum Style)",
      "tempo": 174,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 127},
        {"instrument": "snare", "position": "1.2.1", "velocity": 127},
        {"instrument": "kick", "position": "1.3.3", "velocity": 120},
        {"instrument": "snare", "position": "1.4.1", "velocity": 127},
        {"instrument": "hihat_closed", "position": "1.1.1", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.1.3", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.2.1", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.2.3", "velocity": 100}
      ],
      "swing_percentage": 50
    },
    {
      "id": "kavinsky_halftime_synthwave",
      "name": "Synthwave Halftime Breakdown",
      "tempo": 100,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 127},
        {"instrument": "snare_gated", "position": "1.3.1", "velocity": 127},
        {"instrument": "kick", "position": "1.3.4", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.1.1", "velocity": 85},
        {"instrument": "hihat_closed", "position": "1.1.3", "velocity": 85},
        {"instrument": "hihat_closed", "position": "1.2.1", "velocity": 85}
      ],
      "swing_percentage": 50
    },
    {
      "id": "breakbeat_hardcore",
      "name": "Rave Breakbeat",
      "tempo": 150,
      "time_signature": "4/4",
      "resolution": "16th",
      "pattern": [
        {"instrument": "kick", "position": "1.1.1", "velocity": 120},
        {"instrument": "snare", "position": "1.2.1", "velocity": 120},
        {"instrument": "kick", "position": "1.2.4", "velocity": 100},
        {"instrument": "kick", "position": "1.3.2", "velocity": 90},
        {"instrument": "snare", "position": "1.4.1", "velocity": 120},
        {"instrument": "snare_ghost", "position": "1.4.4", "velocity": 60}
      ],
      "swing_percentage": 54
    },
    {
      "id": "halftime_trap_hybrid",
      "name": "Halftime Trap Hybrid",
      "tempo": 140,
      "time_signature": "4/4",
      "resolution": "32nd",
      "pattern": [
        {"instrument": "kick_808", "position": "1.1.1", "velocity": 127},
        {"instrument": "snare", "position": "1.3.1", "velocity": 120},
        {"instrument": "kick_808", "position": "1.3.4", "velocity": 100},
        {"instrument": "hihat_closed", "position": "1.1.1", "velocity": 90},
        {"instrument": "hihat_closed", "position": "1.1.2", "velocity": 90},
        {"instrument": "hihat_closed", "position": "1.1.3", "velocity": 90},
        {"instrument": "hihat_closed", "position": "1.1.4", "velocity": 90}
      ],
      "swing_percentage": 50
    }
  ]
}
```

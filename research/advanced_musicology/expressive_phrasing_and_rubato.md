# Scholar 5: The Human Performance Expressive Phrasing & Micro-Rubato Analyst

## 1. Micro-Rubato and Phrasing Breathing
To eliminate the rigid "quantized DAW" feel, music must exhibit temporal fluidity. This breathes life into the composition, mapping structural tension to tempo fluctuations.

### Accelerando and Ritardando
Human performers naturally accelerate into melodic climaxes (increasing tension) and decelerate (ritardando) at phrase endings (resolution). 

**Algorithmic Model (Tempo Curve):**
Let $T(t)$ be the tempo multiplier at time $t$ within a phrase of duration $D$.
$T(t) = 1.0 + A \cdot \sin(\pi \cdot \frac{t}{D}) - R \cdot e^{k \cdot (t - D)}$
Where $A$ is the peak acceleration factor, $R$ is the ritardando depth, and $k$ controls the sharpness of the ending ritardando.

### Anticipation and Laid-Back Timing
Emotional notes often do not land precisely on the grid.
- **Anticipation (Pushing the beat):** Notes arrive 15-30ms before the downbeat, creating urgency.
- **Laid-back (Dragging the beat):** Common in jazz/soul, phrases lean 20-40ms behind the beat, creating a relaxed feel.

**Algorithmic Rule:**
$t_{actual} = t_{grid} + \Delta t$
Where $\Delta t \in [-30, -15]$ ms for anticipation and $\Delta t \in [20, 40]$ ms for laid-back phrases.

## 2. Velocity Contours
A constant velocity yields a mechanical sound. Human dynamics follow fluid curves across phrases.

### Sigmoidal Arc Velocity Curves
A 4-bar phrase typically crescendos into the peak note and decrescendos into the resolution. This is best modeled by a bell or sigmoidal arc.

**Algorithmic Model (Velocity Curve):**
$V(x) = V_{base} + (V_{peak} - V_{base}) \cdot \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)$
Where $x$ is the current beat in the phrase, $\mu$ is the beat index of the melodic peak, and $\sigma$ determines the width (spread) of the crescendo/decrescendo.

## 3. Expressive Controllers
Continuous control parameters shape notes after their onset, mimicking acoustic instruments.

### Dynamic Pitch Scoops
Bending up to a target note on its onset (e.g., 2 semitones below) simulates vocal or string techniques.

**Algorithmic Model (Pitch Bend Envelope):**
$P(t) = P_{target} - \Delta P \cdot e^{-t / \tau}$
Where $\Delta P$ is the scoop depth (e.g., 2 semitones) and $\tau$ is the scoop duration (e.g., 50-100ms).

### Delayed Vibrato Swells
Vibrato should not begin immediately; it blooms after a delay and swells in depth.

**Algorithmic Model (Vibrato LFO Depth):**
$VibDepth(t) = D_{max} \cdot \frac{1}{1 + e^{-k(t - t_{delay})}}$
Where $D_{max}$ is the maximum vibrato depth, $t_{delay}$ is the delay before vibrato onset (e.g., 300ms), and $k$ controls the swell rate.

## JSON Schema Representation

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Expressive Performance Rules",
  "type": "object",
  "properties": {
    "micro_rubato": {
      "type": "object",
      "properties": {
        "anticipation_ms": {
          "type": "array",
          "items": { "type": "number" },
          "description": "Range for early notes (e.g., [-30, -15])"
        },
        "laid_back_ms": {
          "type": "array",
          "items": { "type": "number" },
          "description": "Range for dragged notes (e.g., [20, 40])"
        },
        "ritardando_depth": { "type": "number" }
      }
    },
    "velocity_contours": {
      "type": "object",
      "properties": {
        "curve_type": { "type": "string", "enum": ["sigmoidal", "linear"] },
        "peak_multiplier": { "type": "number" }
      }
    },
    "expressive_controllers": {
      "type": "object",
      "properties": {
        "pitch_scoop": {
          "type": "object",
          "properties": {
            "depth_semitones": { "type": "number" },
            "duration_ms": { "type": "number" }
          }
        },
        "delayed_vibrato": {
          "type": "object",
          "properties": {
            "delay_ms": { "type": "number" },
            "swell_rate": { "type": "number" },
            "max_depth": { "type": "number" }
          }
        }
      }
    }
  }
}
```

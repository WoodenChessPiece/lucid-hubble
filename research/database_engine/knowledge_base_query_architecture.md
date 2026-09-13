# Knowledge Base Architecture & Algorithmic Query Engine

This document defines the architectural blueprint for the algorithmic query engine and unified JSON schemas used to ingest and parse the music knowledge base into our Python studio.

## 1. Unified JSON Schemas

The following JSON schemas define the structure for various musical components stored in our knowledge base.

### 1.1 Progressions
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Progression",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "key": { "type": "string" },
    "mode": { "type": "string" },
    "chords": {
      "type": "array",
      "items": { "type": "string" }
    },
    "emotional_profile": {
      "type": "array",
      "items": { "type": "string" }
    },
    "sections": {
      "type": "array",
      "items": { "type": "string" }
    },
    "genre": { "type": "string" }
  },
  "required": ["name", "key", "mode", "chords", "emotional_profile", "sections"]
}
```

### 1.2 Melodic Motifs
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Melodic Motif",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "contour": { "type": "string" },
    "intervals": {
      "type": "array",
      "items": { "type": "integer" }
    },
    "metric_anchors": {
      "type": "array",
      "items": { "type": "number" }
    },
    "sentence_formula": { "type": "string" },
    "genre": { "type": "string" },
    "mood": { "type": "string" }
  },
  "required": ["name", "contour", "intervals", "metric_anchors", "sentence_formula"]
}
```

### 1.3 Drum Grooves
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Drum Groove",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "genre": { "type": "string" },
    "bpm_range": {
      "type": "array",
      "items": { "type": "integer" },
      "minItems": 2,
      "maxItems": 2
    },
    "kick_pattern": { "type": "array", "items": { "type": "number" } },
    "snare_pattern": { "type": "array", "items": { "type": "number" } },
    "hat_pattern": { "type": "array", "items": { "type": "number" } },
    "fills": {
      "type": "array",
      "items": { "type": "object" }
    }
  },
  "required": ["name", "genre", "bpm_range", "kick_pattern", "snare_pattern", "hat_pattern"]
}
```

### 1.4 Basslines
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Bassline",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "style": { "type": "string" },
    "genre": { "type": "string" },
    "gate_lengths": { "type": "array", "items": { "type": "number" } },
    "velocity_curve": { "type": "array", "items": { "type": "integer" } },
    "octave_strategy": { "type": "string" }
  },
  "required": ["name", "style", "gate_lengths", "velocity_curve", "octave_strategy"]
}
```

### 1.5 Song Blueprints
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Song Blueprint",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "genre": { "type": "string" },
    "tempo": { "type": "integer" },
    "sections_list": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "bars": { "type": "integer" }
        }
      }
    },
    "energy_curve": {
      "type": "array",
      "items": { "type": "number" }
    }
  },
  "required": ["name", "tempo", "sections_list", "energy_curve"]
}
```

## 2. Python Query Engine

Below is the design for `src/composer/knowledge_base.py`, a robust loader and query engine that traverses the JSON research repository, ingests the models, and permits dynamic filtering based on tags like genre, mood, or section.

```python
import os
import json
import glob
from typing import List, Dict, Any, Optional

class KnowledgeBase:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.progressions = []
        self.motifs = []
        self.grooves = []
        self.basslines = []
        self.blueprints = []
        self._load_all()

    def _load_json_files(self, sub_dir: str) -> List[Dict[str, Any]]:
        path_pattern = os.path.join(self.data_dir, sub_dir, "*.json")
        data = []
        for file_path in glob.glob(path_pattern):
            try:
                with open(file_path, 'r') as f:
                    data.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        return data

    def _load_all(self):
        """Loads all JSON artifacts from the repository."""
        self.progressions = self._load_json_files('progressions')
        self.motifs = self._load_json_files('motifs')
        self.grooves = self._load_json_files('grooves')
        self.basslines = self._load_json_files('basslines')
        self.blueprints = self._load_json_files('blueprints')

    def _filter_items(self, items: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        result = []
        for item in items:
            match = True
            for k, v in kwargs.items():
                if k not in item:
                    match = False
                    break
                
                # Handle lists like emotional_profile or sections
                if isinstance(item[k], list):
                    if v not in item[k]:
                        match = False
                        break
                elif item[k] != v:
                    match = False
                    break
            if match:
                result.append(item)
        return result

    def get_progression(self, genre: Optional[str] = None, mood: Optional[str] = None, section: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {}
        if genre: filters['genre'] = genre
        if mood: filters['emotional_profile'] = mood
        if section: filters['sections'] = section
        return self._filter_items(self.progressions, **filters)

    def get_motif(self, genre: Optional[str] = None, mood: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {}
        if genre: filters['genre'] = genre
        if mood: filters['mood'] = mood
        return self._filter_items(self.motifs, **filters)

    def get_groove(self, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {}
        if genre: filters['genre'] = genre
        return self._filter_items(self.grooves, **filters)
        
    def get_bassline(self, genre: Optional[str] = None, style: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {}
        if genre: filters['genre'] = genre
        if style: filters['style'] = style
        return self._filter_items(self.basslines, **filters)

    def get_blueprint(self, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {}
        if genre: filters['genre'] = genre
        return self._filter_items(self.blueprints, **filters)

# Example Usage
if __name__ == "__main__":
    kb = KnowledgeBase(data_dir="./research/data")
    
    # Query for a heroic synthwave chorus progression
    heroic_chorus_progs = kb.get_progression(genre='synthwave', mood='heroic', section='chorus')
    print("Found Progressions:", len(heroic_chorus_progs))
```

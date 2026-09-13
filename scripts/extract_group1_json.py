import re
import json

with open('research/edm_masterclass/group1_progressive_bigroom_billboard.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all ```json ... ``` blocks
pattern = re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL)
matches = pattern.findall(text)
print(f"Total json matches found: {len(matches)}")

for i, m in enumerate(matches):
    try:
        data = json.loads(m)
        print(f"Match {i}: valid JSON with keys {list(data.keys())}")
        with open('research/edm_masterclass/group1_progressive_bigroom_billboard.json', 'w', encoding='utf-8') as out:
            json.dump(data, out, indent=2)
        print("Wrote research/edm_masterclass/group1_progressive_bigroom_billboard.json")
        break
    except Exception as e:
        print(f"Match {i}: parse error: {e}")

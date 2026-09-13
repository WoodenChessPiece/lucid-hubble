import json

for g in [1, 2, 3, 4, 5]:
    files = {
        1: 'research/edm_masterclass/group1_progressive_bigroom_billboard.json',
        2: 'research/edm_masterclass/group2_melodic_techno_deephouse.json',
        3: 'research/edm_masterclass/group3_frenchtouch_synthwave_cyberpunk.json',
        4: 'research/edm_masterclass/group4_futurebass_trap_dubstep.json',
        5: 'research/edm_masterclass/group5_trance_dnb_idm.json'
    }
    with open(files[g]) as f:
        data = json.load(f)
    print(f"=== GROUP {g} ===")
    if 'artists' in data:
        print(f"  Artists count: {len(data['artists'])}")
        if isinstance(data['artists'], list) and len(data['artists']) > 0:
            print(f"  Sample artist keys: {list(data['artists'][0].keys())}")
            print(f"  Sample artist name: {data['artists'][0].get('artist', data['artists'][0].get('name'))}")
        elif isinstance(data['artists'], dict):
            print(f"  Sample artist dict key: {list(data['artists'].keys())[:2]}")
    if 'progressions' in data:
        print(f"  Progressions count: {len(data['progressions'])}")
        if len(data['progressions']) > 0:
            print(f"  Sample progression keys: {list(data['progressions'][0].keys())}")
    if 'melodic_motifs' in data:
        print(f"  Melodic motifs count: {len(data['melodic_motifs'])}")
    if 'bass_grooves' in data:
        print(f"  Bass grooves count: {len(data['bass_grooves'])}")

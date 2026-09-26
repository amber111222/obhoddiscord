import os
import json
import sys

PRESETS_CACHE = None

def get_presets_file():
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "presets_data.json")

def load_presets():
    global PRESETS_CACHE
    if PRESETS_CACHE is not None:
        return PRESETS_CACHE

    path = get_presets_file()
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "presets_data.json")

    with open(path, "r", encoding="utf-8") as f:
        PRESETS_CACHE = json.load(f)
    return PRESETS_CACHE

def get_preset_list():
    """Returns list of (id, display_name, description) sorted by effectiveness for Discord."""
    presets = load_presets()
    
    # Priority order optimized specifically for Discord
    priority = [
        "general (ALT)",
        "Discord Voice & Chat Fast",
        "general (ALT2)",
        "general (ALT6)",
        "general (ALT4)",
        "general (ALT8)",
        "general (FAKE TLS AUTO)",
        "general",
        "general (ALT3)",
        "general (ALT5)",
        "general (ALT10)",
        "general (ALT11)",
        "general (FAKE TLS AUTO ALT)",
        "general (SIMPLE FAKE)"
    ]
    
    sorted_keys = []
    for p in priority:
        if p in presets:
            sorted_keys.append(p)
            
    for k in presets.keys():
        if k not in sorted_keys:
            sorted_keys.append(k)

    return [(k, presets[k]["name"], presets[k]["description"]) for k in sorted_keys]

def get_preset(preset_id):
    presets = load_presets()
    return presets.get(preset_id)

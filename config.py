"""Internationalization utility"""
import json, os

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_cache = {}

def _load_json(filename):
    if filename not in _cache:
        path = os.path.join(_DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            _cache[filename] = json.load(f)
    return _cache[filename]

def t(key_path: str, lang: str = "es") -> str:
    """Get translated text. key_path uses dot notation: 'nav.login'"""
    data = _load_json("ui_text.json")
    keys = key_path.split(".")
    obj = data
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return key_path
    if isinstance(obj, dict) and lang in obj:
        return obj[lang]
    elif isinstance(obj, dict) and "es" in obj:
        return obj["es"]
    return str(obj)

def get_dimensions(lang="es"):
    data = _load_json("dimensions.json")
    result = []
    for d in data["dimensions"]:
        result.append({
            "id": d["id"],
            "icon": d["icon"],
            "color": d["color"],
            "name": d["names"].get(lang, d["names"]["es"]),
            "description": d["descriptions"].get(lang, d["descriptions"]["es"])
        })
    return result

def get_axes(lang="es"):
    data = _load_json("actions.json")
    result = []
    for ax in data["axes"]:
        actions = []
        for a in ax["actions"]:
            actions.append({
                "id": a["id"],
                "name": a["names"].get(lang, a["names"]["es"])
            })
        result.append({
            "id": ax["id"],
            "icon": ax["icon"],
            "color": ax["color"],
            "name": ax["names"].get(lang, ax["names"]["es"]),
            "actions": actions
        })
    return result

def get_bibliography():
    return _load_json("bibliography.json")

def get_actor_types(lang="es"):
    data = _load_json("ui_text.json")
    types = data["form"]["actor_types"]
    return {k: v.get(lang, v["es"]) for k, v in types.items()}

def get_connection_types(lang="es"):
    data = _load_json("ui_text.json")
    types = data["form"]["connection_types"]
    return {k: v.get(lang, v["es"]) for k, v in types.items()}

def get_impact_ranges(lang="es"):
    data = _load_json("ui_text.json")
    ranges = data["impact_ranges"]
    return {k: v.get(lang, v["es"]) for k, v in ranges.items()}

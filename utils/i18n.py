"""Internationalization utility for Puentes Regenerativos."""
import json
import os

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_cache = {}


def _load_json(filename):
    if filename not in _cache:
        path = os.path.join(_DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


def t(key_path, lang="es"):
    """Get translated text using dot notation: t('nav.login', 'es')"""
    data = _load_json("ui_text.json")
    obj = data
    for k in key_path.split("."):
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        else:
            return key_path
    if isinstance(obj, dict) and lang in obj:
        return obj[lang]
    if isinstance(obj, dict) and "es" in obj:
        return obj["es"]
    return str(obj)


def get_dimensions(lang="es"):
    data = _load_json("dimensions.json")
    return [
        {"id": d["id"], "icon": d["icon"], "color": d["color"],
         "name": d["names"].get(lang, d["names"]["es"]),
         "description": d["descriptions"].get(lang, d["descriptions"]["es"])}
        for d in data["dimensions"]
    ]


def get_axes(lang="es"):
    data = _load_json("actions.json")
    result = []
    for ax in data["axes"]:
        actions = [{"id": a["id"], "name": a["names"].get(lang, a["names"]["es"])}
                   for a in ax["actions"]]
        result.append({
            "id": ax["id"], "icon": ax["icon"], "color": ax["color"],
            "name": ax["names"].get(lang, ax["names"]["es"]),
            "actions": actions
        })
    return result


def get_bibliography():
    return _load_json("bibliography.json")


def get_actor_types(lang="es"):
    data = _load_json("ui_text.json")
    return {k: v.get(lang, v["es"]) for k, v in data["form"]["actor_types"].items()}


def get_connection_types(lang="es"):
    data = _load_json("ui_text.json")
    return {k: v.get(lang, v["es"]) for k, v in data["form"]["connection_types"].items()}


def get_impact_ranges(lang="es"):
    data = _load_json("ui_text.json")
    return {k: v.get(lang, v["es"]) for k, v in data["impact_ranges"].items()}

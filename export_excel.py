"""
Puentes Regenerativos - Settings
Reads from environment variables. Streamlit secrets are handled in app.py.
"""
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
APP_MODE = "demo" if not SUPABASE_URL else "production"
DEFAULT_LANG = "es"
LANG_LABELS = {"es": "Español", "en": "English", "ca": "Català"}
ADMIN_EMAILS = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
MAP_CENTER = [20, 0]
MAP_ZOOM = 2
INDEX_WEIGHTS = {
    "degree_centrality": 0.30,
    "action_diversity": 0.25,
    "impact_reach": 0.20,
    "network_participation": 0.15,
    "bridging_coefficient": 0.10,
}

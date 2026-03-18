"""
Supabase database layer for Puentes Regenerativos.
Same interface as DemoDB so the app can switch transparently.
"""


class SupabaseDB:
    """Real database using Supabase PostgreSQL."""

    def __init__(self, client):
        self.sb = client

    # ── Profiles ──

    def get_profiles(self, filters=None):
        q = self.sb.table("profiles").select("*")
        if filters:
            if filters.get("pais"):
                q = q.in_("pais", filters["pais"])
            if filters.get("tipo_actor"):
                q = q.in_("tipo_actor", filters["tipo_actor"])
        res = q.execute()
        profs = res.data or []
        # Post-filter for dimensions (array overlap not easy in PostgREST)
        if filters and filters.get("dimensiones"):
            dims = filters["dimensiones"]
            profs = [p for p in profs if any(d in (p.get("dimensiones_regeneracion") or []) for d in dims)]
        return profs

    def get_profile(self, profile_id):
        res = self.sb.table("profiles").select("*").eq("id", profile_id).execute()
        return res.data[0] if res.data else None

    def get_user_profiles(self, user_id):
        res = self.sb.table("profiles").select("*").eq("user_id", user_id).execute()
        return res.data or []

    def save_profile(self, data):
        # Clean data: remove keys that aren't columns
        clean = {k: v for k, v in data.items() if k not in ("pending_connections", "pending_territories", "indice_puentes")}

        if "id" in clean and clean["id"]:
            # Check if exists
            existing = self.sb.table("profiles").select("id").eq("id", clean["id"]).execute()
            if existing.data:
                self.sb.table("profiles").update(clean).eq("id", clean["id"]).execute()
                return clean["id"]

        # Insert new
        if "id" not in clean or not clean["id"]:
            clean.pop("id", None)
        res = self.sb.table("profiles").insert(clean).execute()
        if res.data:
            return res.data[0]["id"]
        return clean.get("id")

    # ── Connections ──

    def get_connections(self):
        res = self.sb.table("connections").select("*").execute()
        return res.data or []

    def add_connection(self, conn):
        clean = {k: v for k, v in conn.items() if k in (
            "source_profile_id", "target_profile_id", "tipo_relacion", "intensidad", "es_externa"
        )}
        try:
            self.sb.table("connections").insert(clean).execute()
        except Exception:
            pass  # Ignore duplicate constraint violations

    # ── Impact Locations ──

    def get_impact_locations(self):
        res = self.sb.table("impact_locations").select("*").execute()
        return res.data or []

    # ── Messages ──

    def get_messages(self, parent_id=None):
        q = self.sb.table("messages").select("*").eq("eliminado", False)
        if parent_id is None:
            q = q.is_("parent_id", "null")
        else:
            q = q.eq("parent_id", parent_id)
        res = q.order("fecha", desc=True).execute()
        return res.data or []

    def add_message(self, msg):
        clean = {k: v for k, v in msg.items() if k in (
            "user_id", "contenido", "parent_id", "autor_nombre"
        )}
        self.sb.table("messages").insert(clean).execute()

"""Excel export for admin panel."""
import io
from datetime import datetime


def export_database_to_excel(db, lang, get_dimensions, get_axes, get_actor_types,
                              get_connection_types, calculate_all_indices):
    """Export full DB to multi-sheet Excel. Returns (BytesIO, filename)."""
    import pandas as pd

    profiles = db.get_profiles()
    connections = db.get_connections()
    impact_locs = db.get_impact_locations()
    indices = calculate_all_indices(profiles, connections, impact_locs)

    dims_map = {d["id"]: d["name"] for d in get_dimensions(lang)}
    actor_map = get_actor_types(lang)
    conn_map = get_connection_types(lang)
    action_map = {}
    for ax in get_axes(lang):
        for a in ax["actions"]:
            action_map[a["id"]] = f'{ax["name"]} > {a["name"]}'
    pname = {p["id"]: p["nombre"] for p in profiles}

    rows_p = []
    for p in profiles:
        nc = len([c for c in connections if c["source_profile_id"] == p["id"] or c["target_profile_id"] == p["id"]])
        rows_p.append({
            "Nombre": p.get("nombre", ""),
            "Tipo": actor_map.get(p.get("tipo_actor", ""), ""),
            "Pais": p.get("pais", ""),
            "Region": p.get("region", ""),
            "Ciudad": p.get("ciudad", ""),
            "Lat": p.get("lat", ""),
            "Lon": p.get("lon", ""),
            "Dimensiones": " | ".join(dims_map.get(d, d) for d in p.get("dimensiones_regeneracion", [])),
            "Acciones": " | ".join(action_map.get(a, a) for a in p.get("acciones", [])),
            "Redes": " | ".join(p.get("redes_participa", [])),
            "Personas Impactadas": p.get("personas_impactadas", ""),
            "Hectareas": p.get("hectareas_regeneradas", ""),
            "Ano Inicio": p.get("ano_inicio_regeneracion", ""),
            "Conexiones": nc,
            "Indice": indices.get(p["id"], 0),
            "Fantasma": "Si" if p.get("es_fantasma") else "No",
        })
    rows_c = [{"Origen": pname.get(c.get("source_profile_id"), "?"),
               "Destino": pname.get(c.get("target_profile_id"), "?"),
               "Tipo": conn_map.get(c.get("tipo_relacion", ""), ""),
               "Intensidad": c.get("intensidad", "")} for c in connections]
    rows_i = [{"Perfil": pname.get(il.get("profile_id"), "?"),
               "Pais": il.get("pais", ""), "Ciudad": il.get("ciudad", ""),
               "Lat": il.get("lat", ""), "Lon": il.get("lon", "")} for il in impact_locs]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(rows_p).to_excel(writer, sheet_name="Perfiles", index=False)
        pd.DataFrame(rows_c).to_excel(writer, sheet_name="Conexiones", index=False)
        pd.DataFrame(rows_i).to_excel(writer, sheet_name="Territorios", index=False)
    output.seek(0)
    return output, f"puentes_regenerativos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

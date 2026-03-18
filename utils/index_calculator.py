"""Regenerative Bridges Index calculator (0-100) based on network theory."""
import math

IMPACT_MAP = {"0": 0, "1-10": 5, "11-50": 30, "51-200": 125, "201-1000": 600, "1001-5000": 3000, "5000+": 7500}
WEIGHTS = {"degree": 0.30, "diversity": 0.25, "impact": 0.20, "network": 0.15, "bridging": 0.10}


def calculate_index(profile, all_profiles, all_connections, impact_locations):
    pid = profile["id"]
    n = max(len([p for p in all_profiles if not p.get("es_fantasma")]), 1)
    conns = [c for c in all_connections if c["source_profile_id"] == pid or c["target_profile_id"] == pid]
    neighbors = set()
    for c in conns:
        neighbors.add(c["target_profile_id"] if c["source_profile_id"] == pid else c["source_profile_id"])
    avg_int = sum(c.get("intensidad", 1) for c in conns) / max(len(conns), 1)
    degree = min((len(neighbors) / max(n - 1, 1)) * 100 * (1 + (avg_int - 1) * 0.1), 100)

    actions = profile.get("acciones", [])
    if actions:
        ax_c = {}
        for a in actions:
            ax_c[a.split("_")[0]] = ax_c.get(a.split("_")[0], 0) + 1
        tot = sum(ax_c.values())
        entropy = sum(-((c / tot) * math.log2(c / tot)) for c in ax_c.values() if c > 0)
        diversity = min((entropy / math.log2(6)) * 100 + min(len(actions) / 10, 1) * 20, 100)
    else:
        diversity = 0

    pv = IMPACT_MAP.get(profile.get("personas_impactadas", "0"), 0)
    hv = IMPACT_MAP.get(profile.get("hectareas_regeneradas", "0"), 0)
    terr = len([il for il in impact_locations if il.get("profile_id") == pid]) + 1
    ps = min(math.log10(max(pv, 1)) / math.log10(7500) * 100, 100)
    hs = min(math.log10(max(hv, 1)) / math.log10(7500) * 100, 100) if hv > 0 else 0
    ts = min(terr / 5 * 100, 100)
    impact = ps * 0.4 + hs * 0.3 + ts * 0.3

    nets = profile.get("redes_participa", [])
    years = max(2026 - (profile.get("ano_inicio_regeneracion") or 2026), 0)
    network = min(len(nets) / 3 * 60 + min(years / 10, 1) * 40, 100)

    nc, nt = set(), set()
    for nid in neighbors:
        np_ = next((p for p in all_profiles if p["id"] == nid), None)
        if np_:
            if np_.get("pais"): nc.add(np_["pais"])
            if np_.get("tipo_actor"): nt.add(np_["tipo_actor"])
    bridging = min((len(nc) / 3 * 50) + (len(nt) / 4 * 50), 100)

    total = (degree * WEIGHTS["degree"] + diversity * WEIGHTS["diversity"] +
             impact * WEIGHTS["impact"] + network * WEIGHTS["network"] +
             bridging * WEIGHTS["bridging"])
    return round(min(total, 100), 1)


def calculate_all_indices(profiles, connections, impact_locations):
    return {p["id"]: calculate_index(p, profiles, connections, impact_locations) for p in profiles}


def get_formula_explanation(lang="es"):
    if lang == "en":
        return """**Regenerative Bridges Index (0-100)**\n\n| Component | Weight | Method |\n|---|---|---|\n| Degree centrality | 30% | Normalized connections x intensity |\n| Action diversity | 25% | Shannon entropy across 6 COP30 axes |\n| Impact reach | 20% | People + hectares + territories (log) |\n| Network participation | 15% | Networks + years active |\n| Bridging coefficient | 10% | Geographic + actor-type diversity |"""
    if lang == "ca":
        return """**Índex Ponts Regeneratius (0-100)**\n\n| Component | Pes | Mètode |\n|---|---|---|\n| Centralitat de grau | 30% | Connexions normalitzades x intensitat |\n| Diversitat d'accions | 25% | Entropia de Shannon sobre 6 eixos COP30 |\n| Abast d'impacte | 20% | Persones + hectàrees + territoris (log) |\n| Participació en xarxes | 15% | Xarxes + anys actius |\n| Coeficient de pont | 10% | Diversitat geogràfica + tipus |"""
    return """**Índice Puentes Regenerativos (0-100)**\n\n| Componente | Peso | Método |\n|---|---|---|\n| Centralidad de grado | 30% | Conexiones normalizadas x intensidad |\n| Diversidad de acciones | 25% | Entropía de Shannon sobre 6 ejes COP30 |\n| Alcance de impacto | 20% | Personas + hectáreas + territorios (log) |\n| Participación en redes | 15% | Redes + años activos |\n| Coeficiente de puente | 10% | Diversidad geográfica + tipo |"""

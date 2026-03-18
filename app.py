"""
Índice Puentes Regenerativos (0-100)
Based on network theory: degree centrality, Shannon diversity, impact reach,
network participation, and bridging coefficient.
"""
import math
from config import INDEX_WEIGHTS

# Impact ranges mapped to numeric values
IMPACT_MAP = {"0": 0, "1-10": 5, "11-50": 30, "51-200": 125, "201-1000": 600, "1001-5000": 3000, "5000+": 7500}
HECTARES_MAP = {"0": 0, "1-10": 5, "11-50": 30, "51-200": 125, "201-1000": 600, "5000+": 7500}


def calculate_index(profile, all_profiles, all_connections, impact_locations):
    """Calculate the Regenerative Bridges Index for a single profile (0-100)."""
    pid = profile["id"]
    n_profiles = max(len([p for p in all_profiles if not p.get("es_fantasma")]), 1)

    # 1. DEGREE CENTRALITY (30%) - normalized connections
    conns = [c for c in all_connections if c["source_profile_id"] == pid or c["target_profile_id"] == pid]
    unique_neighbors = set()
    for c in conns:
        other = c["target_profile_id"] if c["source_profile_id"] == pid else c["source_profile_id"]
        unique_neighbors.add(other)
    max_possible = n_profiles - 1
    degree_score = (len(unique_neighbors) / max(max_possible, 1)) * 100 if max_possible > 0 else 0
    # Cap at 100, bonus for weighted intensity
    avg_intensity = sum(c.get("intensidad", 1) for c in conns) / max(len(conns), 1)
    degree_score = min(degree_score * (1 + (avg_intensity - 1) * 0.1), 100)

    # 2. ACTION DIVERSITY (25%) - Shannon entropy normalized
    actions = profile.get("acciones", [])
    if actions:
        # Group by axis prefix
        axis_counts = {}
        for a in actions:
            prefix = a.split("_")[0]
            axis_counts[prefix] = axis_counts.get(prefix, 0) + 1
        total = sum(axis_counts.values())
        # Shannon entropy
        entropy = 0
        for count in axis_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        max_entropy = math.log2(6)  # 6 axes
        diversity_score = (entropy / max_entropy) * 100 if max_entropy > 0 else 0
        # Bonus for total number of actions
        action_bonus = min(len(actions) / 10, 1) * 20
        diversity_score = min(diversity_score + action_bonus, 100)
    else:
        diversity_score = 0

    # 3. IMPACT REACH (20%) - people + hectares + territories
    people_val = IMPACT_MAP.get(profile.get("personas_impactadas", "0"), 0)
    hectares_val = HECTARES_MAP.get(profile.get("hectareas_regeneradas", "0"), 0)
    profile_impacts = [il for il in impact_locations if il.get("profile_id") == pid]
    territories = len(profile_impacts) + 1  # +1 for base location

    # Logarithmic scaling
    people_score = min(math.log10(max(people_val, 1)) / math.log10(7500) * 100, 100)
    hectares_score = min(math.log10(max(hectares_val, 1)) / math.log10(7500) * 100, 100) if hectares_val > 0 else 0
    territory_score = min(territories / 5 * 100, 100)
    impact_score = (people_score * 0.4 + hectares_score * 0.3 + territory_score * 0.3)

    # 4. NETWORK PARTICIPATION (15%)
    networks = profile.get("redes_participa", [])
    years_active = max(2026 - (profile.get("ano_inicio_regeneracion") or 2026), 0)
    network_score = min(len(networks) / 3 * 60 + min(years_active / 10, 1) * 40, 100)

    # 5. BRIDGING COEFFICIENT (10%) - connects different clusters/countries
    neighbor_countries = set()
    neighbor_types = set()
    for nid in unique_neighbors:
        np = next((p for p in all_profiles if p["id"] == nid), None)
        if np:
            if np.get("pais"):
                neighbor_countries.add(np["pais"])
            if np.get("tipo_actor"):
                neighbor_types.add(np["tipo_actor"])
    bridging_score = min(
        (len(neighbor_countries) / 3 * 50) + (len(neighbor_types) / 4 * 50),
        100
    )

    # WEIGHTED TOTAL
    total = (
        degree_score * INDEX_WEIGHTS["degree_centrality"] +
        diversity_score * INDEX_WEIGHTS["action_diversity"] +
        impact_score * INDEX_WEIGHTS["impact_reach"] +
        network_score * INDEX_WEIGHTS["network_participation"] +
        bridging_score * INDEX_WEIGHTS["bridging_coefficient"]
    )

    return round(min(total, 100), 1)


def calculate_all_indices(profiles, connections, impact_locations):
    """Calculate indices for all profiles."""
    results = {}
    for p in profiles:
        results[p["id"]] = calculate_index(p, profiles, connections, impact_locations)
    return results


def get_formula_explanation(lang="es"):
    explanations = {
        "es": """**Fórmula del Índice Puentes Regenerativos (0-100)**

El índice mide la capacidad regenerativa de un actor dentro de la red, combinando 5 componentes basados en teoría de redes:

| Componente | Peso | Descripción |
|---|---|---|
| **Centralidad de grado** | 30% | Cantidad y calidad de conexiones directas, normalizada por el tamaño de la red. Mayor intensidad de relación otorga bonificación. |
| **Diversidad de acciones** | 25% | Entropía de Shannon sobre los ejes de acción. Actuar en más ejes diferentes = mayor resiliencia sistémica. |
| **Alcance de impacto** | 20% | Combinación de personas impactadas (40%), hectáreas regeneradas (30%) y territorios de alcance (30%), con escala logarítmica. |
| **Participación en redes** | 15% | Número de redes en las que participa + años activos en regeneración. |
| **Coeficiente de puente** | 10% | Diversidad geográfica y de tipos de actor entre las conexiones. Conectar actores de diferentes países y tipos = mayor capacidad de puente. |

*Inspirado en métricas de redes complejas (centralidad, betweenness, clustering) y en el concepto de "pattern literacy" de Mang & Reed (2012).*""",

        "en": """**Regenerative Bridges Index Formula (0-100)**

The index measures an actor's regenerative capacity within the network, combining 5 components based on network theory:

| Component | Weight | Description |
|---|---|---|
| **Degree centrality** | 30% | Number and quality of direct connections, normalized by network size. Higher relationship intensity provides bonus. |
| **Action diversity** | 25% | Shannon entropy across action axes. Acting across more different axes = greater systemic resilience. |
| **Impact reach** | 20% | Combination of people impacted (40%), hectares regenerated (30%) and territories reached (30%), with logarithmic scaling. |
| **Network participation** | 15% | Number of networks + years active in regeneration. |
| **Bridging coefficient** | 10% | Geographic and actor-type diversity among connections. Connecting actors from different countries and types = greater bridging capacity. |

*Inspired by complex network metrics and Mang & Reed's (2012) concept of "pattern literacy".*""",

        "ca": """**Fórmula de l'Índex Ponts Regeneratius (0-100)**

L'índex mesura la capacitat regenerativa d'un actor dins la xarxa, combinant 5 components basats en teoria de xarxes:

| Component | Pes | Descripció |
|---|---|---|
| **Centralitat de grau** | 30% | Quantitat i qualitat de connexions directes, normalitzada. |
| **Diversitat d'accions** | 25% | Entropia de Shannon sobre els eixos d'acció. |
| **Abast d'impacte** | 20% | Persones + hectàrees + territoris (escala logarítmica). |
| **Participació en xarxes** | 15% | Nombre de xarxes + anys actius. |
| **Coeficient de pont** | 10% | Diversitat geogràfica i de tipus entre connexions. |"""
    }
    return explanations.get(lang, explanations["es"])

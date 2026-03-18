"""Demo data and in-memory database for Puentes Regenerativos."""
import uuid
import random
from datetime import datetime, timedelta

DEMO_USER_ID = "demo-user-001"

_PROFILES = [
    {"id": "p1", "user_id": DEMO_USER_ID, "nombre": "Centro Eco-pedagógico Aucca", "tipo_actor": "organizacion",
     "descripcion": "Centro de educación ambiental y permacultura en Talagante, Chile.",
     "email": "aucca@example.cl", "pais": "Chile", "region": "Región Metropolitana", "ciudad": "Talagante",
     "lat": -33.6667, "lon": -70.9167,
     "dimensiones_regeneracion": ["ecological", "cultural", "social"],
     "acciones": ["af_02", "af_03", "af_06", "fob_07", "hsd_01", "hsd_02"],
     "redes_participa": ["Red de Permacultura Chile", "ERES"], "ano_inicio_regeneracion": 2012,
     "personas_impactadas": "201-1000", "hectareas_regeneradas": "1-10", "es_fantasma": False,
     "interpretacion_regeneracion": "Regenerar es mejorar la salud del ecosistema del cual somos parte."},
    {"id": "p2", "user_id": DEMO_USER_ID, "nombre": "Ecoescuela El Manzano", "tipo_actor": "organizacion",
     "descripcion": "Centro de aprendizaje en diseño regenerativo y permacultura.",
     "pais": "Chile", "region": "Región del Maule", "ciudad": "Cabrero",
     "lat": -37.0333, "lon": -72.3833,
     "dimensiones_regeneracion": ["ecological", "social", "systemic_design"],
     "acciones": ["hsd_02", "af_06", "fob_01", "ea_06", "hsd_01"],
     "redes_participa": ["Red de Permacultura Chile", "GEN"], "ano_inicio_regeneracion": 2007,
     "personas_impactadas": "1001-5000", "hectareas_regeneradas": "11-50", "es_fantasma": False,
     "interpretacion_regeneracion": "Educamos para la transición hacia una cultura permanente."},
    {"id": "p3", "user_id": "user-002", "nombre": "LivLin", "tipo_actor": "empresa_social",
     "descripcion": "Regeneración ecosocial, datos para acción climática y educación para la sostenibilidad.",
     "web": "https://livlin.cl", "pais": "Chile", "region": "Región Metropolitana", "ciudad": "Santiago",
     "lat": -33.4372, "lon": -70.6205,
     "dimensiones_regeneracion": ["systemic_design", "social", "ecological"],
     "acciones": ["ea_05", "ea_08", "hsd_01", "hsd_10", "ea_06"],
     "redes_participa": ["Race to Resilience", "CR2"], "ano_inicio_regeneracion": 2020,
     "personas_impactadas": "51-200", "es_fantasma": False,
     "interpretacion_regeneracion": "Datos y tecnología como puentes entre ciencia climática y acción territorial."},
    {"id": "p4", "user_id": "user-003", "nombre": "Regenesis Group", "tipo_actor": "organizacion",
     "descripcion": "Pioneers of regenerative development and design methodology.",
     "pais": "Estados Unidos", "region": "New Mexico", "ciudad": "Santa Fe",
     "lat": 35.6870, "lon": -105.9378,
     "dimensiones_regeneracion": ["systemic_design", "ecological", "cultural", "social", "economic"],
     "acciones": ["hsd_02", "ea_06", "ea_07", "hsd_06", "ciw_04", "fob_01"],
     "redes_participa": ["ILFI"], "ano_inicio_regeneracion": 1995,
     "personas_impactadas": "5000+", "hectareas_regeneradas": "51-200", "es_fantasma": False,
     "interpretacion_regeneracion": "Co-evolution of human communities with the living systems of their place."},
    {"id": "p5", "user_id": "user-004", "nombre": "Xarxa de Custòdia del Territori", "tipo_actor": "red",
     "descripcion": "Red catalana de custodia del territorio.",
     "pais": "España", "region": "Catalunya", "ciudad": "Barcelona",
     "lat": 41.3874, "lon": 2.1686,
     "dimensiones_regeneracion": ["ecological", "social", "economic"],
     "acciones": ["fob_01", "fob_02", "fob_03", "ea_07", "hsd_09"],
     "redes_participa": ["ELCN"], "ano_inicio_regeneracion": 2003,
     "personas_impactadas": "1001-5000", "hectareas_regeneradas": "5000+", "es_fantasma": False,
     "interpretacion_regeneracion": "Custodiar el territori és cuidar la xarxa de vida."},
    {"id": "p6", "user_id": "user-005", "nombre": "Transition Network", "tipo_actor": "red",
     "descripcion": "Global movement of communities reimagining and rebuilding our world.",
     "pais": "Reino Unido", "region": "Devon", "ciudad": "Totnes",
     "lat": 50.4319, "lon": -3.6861,
     "dimensiones_regeneracion": ["social", "economic", "ecological", "cultural"],
     "acciones": ["ea_01", "ea_03", "ciw_03", "af_04", "hsd_01", "eit_01"],
     "redes_participa": ["GEN", "Permaculture International"], "ano_inicio_regeneracion": 2006,
     "personas_impactadas": "5000+", "es_fantasma": False,
     "interpretacion_regeneracion": "Building community resilience."},
    {"id": "p7", "user_id": "user-006", "nombre": "Cooperativa Las Cañadas", "tipo_actor": "colectivo",
     "descripcion": "Centro de agroecología y permacultura en Veracruz, México.",
     "pais": "México", "region": "Veracruz", "ciudad": "Huatusco",
     "lat": 19.1489, "lon": -96.9683,
     "dimensiones_regeneracion": ["ecological", "economic", "social"],
     "acciones": ["af_01", "af_06", "af_09", "fob_07", "af_08", "ea_01"],
     "redes_participa": ["Red de Permacultura México"], "ano_inicio_regeneracion": 1998,
     "personas_impactadas": "1001-5000", "hectareas_regeneradas": "201-1000", "es_fantasma": False,
     "interpretacion_regeneracion": "Demostrar que otra forma de vida es posible."},
    {"id": "p8", "user_id": "user-007", "nombre": "Instituto Çarakura", "tipo_actor": "organizacion",
     "descripcion": "Educação para sustentabilidade e regeneração no Brasil.",
     "pais": "Brasil", "region": "São Paulo", "ciudad": "São Paulo",
     "lat": -23.5505, "lon": -46.6333,
     "dimensiones_regeneracion": ["cultural", "social", "systemic_design"],
     "acciones": ["hsd_01", "hsd_06", "hsd_07", "ea_06", "hsd_02"],
     "redes_participa": ["GEN", "Gaia Education"], "ano_inicio_regeneracion": 2010,
     "personas_impactadas": "1001-5000", "es_fantasma": False,
     "interpretacion_regeneracion": "Regeneração é reconectar humanidade e natureza."},
    {"id": "p9", "user_id": DEMO_USER_ID, "nombre": "David Holmgren", "tipo_actor": "persona",
     "descripcion": "Co-creador del concepto de permacultura.",
     "pais": "Australia", "region": "Victoria", "ciudad": "Hepburn",
     "lat": -37.2833, "lon": 144.1333,
     "dimensiones_regeneracion": ["ecological", "systemic_design"],
     "acciones": ["af_06", "hsd_02"], "redes_participa": [], "es_fantasma": True,
     "fantasma_creado_por": DEMO_USER_ID, "personas_impactadas": "5000+",
     "interpretacion_regeneracion": ""},
    {"id": "p10", "user_id": "user-008", "nombre": "Red de Huertas Urbanas Rosario", "tipo_actor": "colectivo",
     "descripcion": "Programa pionero de agricultura urbana en Rosario, Argentina.",
     "pais": "Argentina", "region": "Santa Fe", "ciudad": "Rosario",
     "lat": -32.9468, "lon": -60.6393,
     "dimensiones_regeneracion": ["ecological", "social", "economic"],
     "acciones": ["af_02", "af_01", "af_04", "ciw_02", "hsd_08"],
     "redes_participa": ["FAO Urban Agriculture"], "ano_inicio_regeneracion": 2001,
     "personas_impactadas": "5000+", "hectareas_regeneradas": "11-50", "es_fantasma": False,
     "interpretacion_regeneracion": "La huerta regenera suelo, comunidad y dignidad."},
]

_CONNECTIONS = [
    {"source_profile_id": "p1", "target_profile_id": "p2", "tipo_relacion": "aprendizaje", "intensidad": 4},
    {"source_profile_id": "p1", "target_profile_id": "p3", "tipo_relacion": "colaboracion", "intensidad": 5},
    {"source_profile_id": "p2", "target_profile_id": "p3", "tipo_relacion": "colaboracion", "intensidad": 3},
    {"source_profile_id": "p2", "target_profile_id": "p9", "tipo_relacion": "inspiracion", "intensidad": 5, "es_externa": True},
    {"source_profile_id": "p3", "target_profile_id": "p4", "tipo_relacion": "aprendizaje", "intensidad": 3},
    {"source_profile_id": "p4", "target_profile_id": "p6", "tipo_relacion": "colaboracion", "intensidad": 2},
    {"source_profile_id": "p5", "target_profile_id": "p6", "tipo_relacion": "colaboracion", "intensidad": 3},
    {"source_profile_id": "p5", "target_profile_id": "p1", "tipo_relacion": "inspiracion", "intensidad": 2},
    {"source_profile_id": "p6", "target_profile_id": "p8", "tipo_relacion": "colaboracion", "intensidad": 3},
    {"source_profile_id": "p7", "target_profile_id": "p2", "tipo_relacion": "aprendizaje", "intensidad": 4},
    {"source_profile_id": "p7", "target_profile_id": "p10", "tipo_relacion": "colaboracion", "intensidad": 3},
    {"source_profile_id": "p8", "target_profile_id": "p7", "tipo_relacion": "colaboracion", "intensidad": 2},
    {"source_profile_id": "p10", "target_profile_id": "p1", "tipo_relacion": "inspiracion", "intensidad": 2},
    {"source_profile_id": "p10", "target_profile_id": "p3", "tipo_relacion": "aprendizaje", "intensidad": 2},
    {"source_profile_id": "p3", "target_profile_id": "p6", "tipo_relacion": "colaboracion", "intensidad": 3},
]

_IMPACT_LOCATIONS = [
    {"profile_id": "p1", "pais": "Chile", "ciudad": "Valparaíso", "lat": -33.0472, "lon": -71.6127},
    {"profile_id": "p3", "pais": "Chile", "ciudad": "Concepción", "lat": -36.8270, "lon": -73.0503},
    {"profile_id": "p4", "pais": "México", "ciudad": "Todos Santos", "lat": 23.4484, "lon": -110.2237},
    {"profile_id": "p6", "pais": "Brasil", "ciudad": "Salvador", "lat": -12.9714, "lon": -38.5124},
    {"profile_id": "p5", "pais": "España", "ciudad": "Girona", "lat": 41.9794, "lon": 2.8214},
]

_MESSAGES = [
    {"id": "m1", "user_id": DEMO_USER_ID, "contenido": "¡Bienvenidos al foro de Puentes Regenerativos!", "parent_id": None, "autor_nombre": "Admin"},
    {"id": "m2", "user_id": "user-003", "contenido": "Excelente iniciativa. La conexión entre actores es clave.", "parent_id": "m1", "autor_nombre": "Regenesis Group"},
    {"id": "m3", "user_id": "user-004", "contenido": "Des de Catalunya, celebrem la diversitat d'actors regeneratius!", "parent_id": "m1", "autor_nombre": "Xarxa de Custòdia"},
    {"id": "m4", "user_id": "user-002", "contenido": "¿Alguien integra datos de biodiversidad con métricas de impacto social?", "parent_id": None, "autor_nombre": "LivLin"},
]

_DEFAULTS = {"comuna": "", "direccion_exacta": "", "telefono": "", "web": "", "email": "",
             "redes_sociales": {}, "ano_ingreso_red": None, "hectareas_regeneradas": "0",
             "personas_impactadas": "0", "indice_puentes": 0, "usa_centroid": False}


class DemoDB:
    """In-memory database for demo mode."""

    def __init__(self):
        self.profiles = {}
        for p in _PROFILES:
            for k, v in _DEFAULTS.items():
                p.setdefault(k, v)
            p.setdefault("fecha_creacion", datetime.now().isoformat())
            p.setdefault("fecha_actualizacion", datetime.now().isoformat())
            self.profiles[p["id"]] = p
        self.connections = [
            {**c, "id": str(uuid.uuid4()), "fecha_creacion": datetime.now().isoformat(),
             "es_externa": c.get("es_externa", False)}
            for c in _CONNECTIONS
        ]
        self.impact_locations = [
            {**il, "id": str(uuid.uuid4()), "region": il.get("region", "")}
            for il in _IMPACT_LOCATIONS
        ]
        self.messages = [
            {**m, "fecha": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
             "eliminado": False}
            for m in _MESSAGES
        ]

    def get_profiles(self, filters=None):
        profs = list(self.profiles.values())
        if filters:
            if filters.get("pais"):
                profs = [p for p in profs if p.get("pais") in filters["pais"]]
            if filters.get("tipo_actor"):
                profs = [p for p in profs if p.get("tipo_actor") in filters["tipo_actor"]]
            if filters.get("dimensiones"):
                profs = [p for p in profs if any(d in p.get("dimensiones_regeneracion", []) for d in filters["dimensiones"])]
        return profs

    def get_profile(self, pid):
        return self.profiles.get(pid)

    def get_user_profiles(self, uid):
        return [p for p in self.profiles.values() if p["user_id"] == uid]

    def save_profile(self, data):
        pid = data.get("id") or str(uuid.uuid4())
        data["id"] = pid
        data["fecha_actualizacion"] = datetime.now().isoformat()
        if pid not in self.profiles:
            data["fecha_creacion"] = datetime.now().isoformat()
        self.profiles[pid] = data
        return pid

    def get_connections(self):
        return self.connections

    def add_connection(self, conn):
        conn["id"] = str(uuid.uuid4())
        conn["fecha_creacion"] = datetime.now().isoformat()
        self.connections.append(conn)

    def get_impact_locations(self):
        return self.impact_locations

    def get_messages(self, parent_id=None):
        msgs = [m for m in self.messages if m.get("parent_id") == parent_id and not m.get("eliminado")]
        return sorted(msgs, key=lambda x: x.get("fecha", ""), reverse=True)

    def add_message(self, msg):
        msg["id"] = str(uuid.uuid4())
        msg["fecha"] = datetime.now().isoformat()
        msg["eliminado"] = False
        self.messages.append(msg)

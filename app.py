"""
🧭 Puentes Regenerativos v2.1
Mapeando Puentes Regenerativos | Developed by Livlin.cl
"""
import streamlit as st
import os
import sys

# Ensure project root is in path for utils imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.app_settings import (
    SUPABASE_URL, APP_MODE, DEFAULT_LANG, LANG_LABELS,
    ADMIN_EMAILS, ADMIN_PASSWORD, MAP_CENTER, MAP_ZOOM
)
from utils.i18n import (
    t, get_dimensions, get_axes, get_bibliography,
    get_actor_types, get_connection_types, get_impact_ranges
)
from utils.demo_data import DemoDB, DEMO_USER_ID
from utils.index_calculator import calculate_all_indices, get_formula_explanation
from utils.export_excel import export_database_to_excel

# Override settings with Streamlit secrets if available
try:
    if st.secrets.get("SUPABASE_URL"):
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
    if st.secrets.get("ADMIN_EMAILS"):
        ADMIN_EMAILS = [e.strip() for e in st.secrets["ADMIN_EMAILS"].split(",") if e.strip()]
    if st.secrets.get("ADMIN_PASSWORD"):
        ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Puentes Regenerativos",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(ROOT, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
for key, default in [
    ("lang", DEFAULT_LANG), ("logged_in", False), ("user_id", None),
    ("page", "map"), ("form_step", 0), ("form_data", {}),
    ("selected_profile", None), ("admin_unlocked", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default
if "db" not in st.session_state:
    st.session_state.db = DemoDB()

lang = st.session_state.lang
db = st.session_state.db


# ============================================================
# HELPERS
# ============================================================
def nav(page):
    st.session_state.page = page


def is_admin():
    if APP_MODE == "demo" and st.session_state.user_id == DEMO_USER_ID:
        return True
    return st.session_state.get("user_email", "") in ADMIN_EMAILS


def render_metric(value, label):
    st.markdown(
        f'<div class="metric-card"><div class="value">{value}</div>'
        f'<div class="label">{label}</div></div>',
        unsafe_allow_html=True,
    )


def dim_chip(did, dims):
    d = next((x for x in dims if x["id"] == did), None)
    if d:
        return f'<span class="dim-chip" style="background:{d["color"]}">{d["icon"]} {d["name"]}</span>'
    return ""


def idx_class(s):
    return "index-low" if s < 33 else "index-mid" if s < 66 else "index-high"


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    logo_path = os.path.join(ROOT, "assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

    st.markdown(f"# {t('app_title', lang)}")
    st.caption(t("app_subtitle", lang))

    lang_opts = list(LANG_LABELS.keys())
    new_lang = st.selectbox(
        t("language_selector", lang), lang_opts,
        index=lang_opts.index(lang), format_func=lambda x: LANG_LABELS[x],
    )
    if new_lang != lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()

    if not st.session_state.logged_in:
        st.subheader(t("auth.demo_mode", lang))
        if st.button(t("auth.demo_login", lang), use_container_width=True, type="primary"):
            st.session_state.logged_in = True
            st.session_state.user_id = DEMO_USER_ID
            st.rerun()
    else:
        for pid, plabel in [
            ("map", t("nav.map", lang)),
            ("profiles", t("nav.profiles", lang)),
            ("network", t("nav.network", lang)),
            ("forum", t("nav.forum", lang)),
            ("bibliography", t("nav.bibliography", lang)),
        ]:
            tp = "primary" if st.session_state.page == pid else "secondary"
            if st.button(plabel, key=f"nav_{pid}", use_container_width=True, type=tp):
                nav(pid)
                st.rerun()

        st.divider()
        if st.button(t("nav.my_profiles", lang), use_container_width=True):
            nav("my_profiles")
            st.rerun()
        if st.button(t("nav.new_profile", lang), use_container_width=True):
            st.session_state.form_data = {}
            st.session_state.form_step = 0
            nav("new_profile")
            st.rerun()

        if is_admin():
            st.divider()
            tp = "primary" if st.session_state.page == "admin" else "secondary"
            if st.button(t("nav.admin", lang), use_container_width=True, type=tp):
                nav("admin")
                st.rerun()

        st.divider()
        if st.button(t("nav.logout", lang), use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.rerun()

    st.markdown("---")
    st.markdown(
        f'<div class="footer">{t("developed_by", lang)}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# AUTH GATE
# ============================================================
if not st.session_state.logged_in:
    c1, c2 = st.columns([1, 2])
    with c1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=250)
    with c2:
        st.markdown(f"# {t('app_title', lang)}")
        st.markdown(f"### {t('app_subtitle', lang)}")
    st.info("👈 " + t("auth.demo_login", lang))
    st.stop()

# ============================================================
# COMPUTE INDICES
# ============================================================
profiles = db.get_profiles()
connections = db.get_connections()
impact_locs = db.get_impact_locations()
indices = calculate_all_indices(profiles, connections, impact_locs)
for p in profiles:
    p["indice_puentes"] = indices.get(p["id"], 0)

dims_data = get_dimensions(lang)
axes_data = get_axes(lang)


# ============================================================
# PAGE: MAP
# ============================================================
def render_map_page():
    st.markdown(f"## {t('map_view.title', lang)}")

    with st.expander(f"🔍 {t('map_view.filters', lang)}", expanded=False):
        c1, c2, c3 = st.columns(3)
        countries = sorted(set(p.get("pais", "") for p in profiles if p.get("pais")))
        with c1:
            sel_countries = st.multiselect(t("form.country", lang), countries)
        at = get_actor_types(lang)
        with c2:
            sel_types = st.multiselect(t("form.actor_type", lang), list(at.keys()), format_func=lambda x: at[x])
        with c3:
            sel_dims = st.multiselect(
                t("form.dimensions", lang),
                [d["id"] for d in dims_data],
                format_func=lambda x: next((d["name"] for d in dims_data if d["id"] == x), x),
            )

    filt = {}
    if sel_countries:
        filt["pais"] = sel_countries
    if sel_types:
        filt["tipo_actor"] = sel_types
    if sel_dims:
        filt["dimensiones"] = sel_dims
    filtered = db.get_profiles(filt) if filt else profiles

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric(len([p for p in filtered if not p.get("es_fantasma")]), t("map_view.total_profiles", lang))
    with c2:
        render_metric(len(connections), t("map_view.total_connections", lang))
    with c3:
        render_metric(len(set(p.get("pais") for p in filtered if p.get("pais"))), t("map_view.total_countries", lang))
    with c4:
        avg = sum(p.get("indice_puentes", 0) for p in filtered) / max(len(filtered), 1)
        render_metric(f"{avg:.0f}", t("index.title", lang))

    import folium
    from streamlit_folium import st_folium

    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="OpenStreetMap")
    at_map = get_actor_types(lang)

    for p in filtered:
        if p.get("lat") and p.get("lon"):
            color = "gray" if p.get("es_fantasma") else "blue"
            popup = (f"<b>{p['nombre']}</b><br>{at_map.get(p.get('tipo_actor',''),'')}"
                     f"<br>📍 {p.get('ciudad','')}, {p.get('pais','')}"
                     f"<br>🧭 {p.get('indice_puentes',0):.0f}/100")
            folium.Marker(
                [p["lat"], p["lon"]],
                popup=folium.Popup(popup, max_width=250),
                tooltip=p["nombre"],
                icon=folium.Icon(color=color, icon="leaf", prefix="fa"),
            ).add_to(m)

    pmap = {p["id"]: p for p in profiles}
    for c in connections:
        s = pmap.get(c["source_profile_id"])
        tg = pmap.get(c["target_profile_id"])
        if s and tg and s.get("lat") and tg.get("lat"):
            folium.PolyLine(
                [[s["lat"], s["lon"]], [tg["lat"], tg["lon"]]],
                weight=c.get("intensidad", 1) * 0.8,
                color="#1976D2", opacity=0.5,
                dash_array="5" if c.get("es_externa") else None,
            ).add_to(m)

    for il in impact_locs:
        if il.get("lat") and il.get("lon"):
            folium.CircleMarker(
                [il["lat"], il["lon"]], radius=6,
                color="#FF7043", fill=True, fill_opacity=0.5,
            ).add_to(m)

    st_folium(m, width=None, height=500, use_container_width=True)

    # Charts
    st.markdown("---")
    tab1, tab2 = st.tabs([f"📊 {t('charts.treemap_title', lang)}", f"🎯 {t('charts.radar_title', lang)}"])

    with tab1:
        import plotly.express as px
        import pandas as pd
        data = [
            {"pais": p.get("pais", "?"), "region": p.get("region", "?"),
             "ciudad": p.get("ciudad", "?"), "nombre": p["nombre"],
             "indice": max(p.get("indice_puentes", 1), 1)}
            for p in filtered if not p.get("es_fantasma")
        ]
        if data:
            fig = px.treemap(
                pd.DataFrame(data),
                path=["pais", "region", "ciudad", "nombre"], values="indice",
                color="indice", color_continuous_scale=["#E3F2FD", "#1565C0"],
            )
            fig.update_layout(font_family="Montserrat", margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        import plotly.graph_objects as go
        dc = {d["id"]: 0 for d in dims_data}
        for p in filtered:
            for d in p.get("dimensiones_regeneracion", []):
                if d in dc:
                    dc[d] += 1
        tot = max(sum(dc.values()), 1)
        cats = [d["name"] for d in dims_data] + [dims_data[0]["name"]]
        vals = [dc[d["id"]] / tot * 100 for d in dims_data] + [dc[dims_data[0]["id"]] / tot * 100]
        fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself", line_color="#1976D2"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), font_family="Montserrat")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"🧮 {t('index.title', lang)}"):
        st.markdown(get_formula_explanation(lang))


# ============================================================
# PAGE: PROFILES
# ============================================================
def render_profiles_page():
    st.markdown(f"## {t('nav.profiles', lang)}")
    search = st.text_input("🔍", placeholder="Buscar..." if lang == "es" else "Search...")
    at = get_actor_types(lang)
    filtered = [p for p in profiles if not p.get("es_fantasma")]
    if search:
        sl = search.lower()
        filtered = [p for p in filtered if sl in p.get("nombre", "").lower() or sl in p.get("pais", "").lower()]
    filtered.sort(key=lambda x: x.get("indice_puentes", 0), reverse=True)

    for p in filtered:
        iv = p.get("indice_puentes", 0)
        dh = " ".join(dim_chip(d, dims_data) for d in p.get("dimensiones_regeneracion", []))
        st.markdown(
            f'<div class="profile-card"><div style="display:flex;justify-content:space-between;align-items:start">'
            f'<div><h3 style="margin:0">{p["nombre"]}</h3>'
            f'<p style="color:#546E7A;margin:4px 0">{at.get(p.get("tipo_actor",""),"")} · 📍 {p.get("ciudad","")}, {p.get("pais","")}</p>'
            f'<p style="font-size:0.9rem">{(p.get("descripcion","") or "")[:150]}</p>'
            f'<div>{dh}</div></div>'
            f'<div class="index-badge {idx_class(iv)}">{iv:.0f}</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Ver → {p['nombre']}", key=f"v_{p['id']}"):
            st.session_state.selected_profile = p["id"]
            nav("profile_detail")
            st.rerun()


# ============================================================
# PAGE: PROFILE DETAIL
# ============================================================
def render_profile_detail():
    p = db.get_profile(st.session_state.selected_profile)
    if not p:
        st.error("Not found")
        return
    at = get_actor_types(lang)
    ct = get_connection_types(lang)
    st.markdown(f"## {p['nombre']}")
    st.caption(f"{at.get(p.get('tipo_actor',''),'')} · 📍 {p.get('ciudad','')}, {p.get('pais','')}")
    if p.get("descripcion"):
        st.markdown(p["descripcion"])
    if p.get("interpretacion_regeneracion"):
        st.markdown(f'> *"{p["interpretacion_regeneracion"]}"*')

    c1, c2 = st.columns(2)
    with c1:
        render_metric(f"{p.get('indice_puentes',0):.0f}", t("index.title", lang))
    pc = [c for c in connections if c["source_profile_id"] == p["id"] or c["target_profile_id"] == p["id"]]
    with c2:
        render_metric(len(pc), t("profile_view.connections_label", lang))

    dh = " ".join(dim_chip(d, dims_data) for d in p.get("dimensiones_regeneracion", []))
    st.markdown(dh, unsafe_allow_html=True)

    st.markdown(f"### {t('profile_view.connections_label', lang)}")
    for c in pc:
        oid = c["target_profile_id"] if c["source_profile_id"] == p["id"] else c["source_profile_id"]
        o = db.get_profile(oid)
        if o:
            st.markdown(f"- **{o['nombre']}** — {ct.get(c.get('tipo_relacion',''),'')} ({'●' * c.get('intensidad',1)})")

    if st.button("← " + ("Volver" if lang == "es" else "Back" if lang == "en" else "Tornar")):
        nav("profiles")
        st.rerun()


# ============================================================
# PAGE: NETWORK
# ============================================================
def render_network_page():
    st.markdown(f"## {t('network_view.title', lang)}")
    import networkx as nx
    import plotly.graph_objects as go

    G = nx.Graph()
    pmap = {p["id"]: p for p in profiles}
    for p in profiles:
        G.add_node(p["id"])
    for c in connections:
        if c["source_profile_id"] in G and c["target_profile_id"] in G:
            G.add_edge(c["source_profile_id"], c["target_profile_id"], weight=c.get("intensidad", 1))

    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    ex, ey = [], []
    for e in G.edges():
        x0, y0 = pos[e[0]]
        x1, y1 = pos[e[1]]
        ex += [x0, x1, None]
        ey += [y0, y1, None]

    nx_, ny_, nt_, ns_, nc_ = [], [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        nx_.append(x)
        ny_.append(y)
        p = pmap.get(n, {})
        iv = p.get("indice_puentes", 0)
        nt_.append(f"{p.get('nombre','?')}<br>Índice: {iv:.0f}")
        ns_.append(max(10, iv * 0.4 + G.degree(n) * 3))
        nc_.append("#BDBDBD" if p.get("es_fantasma") else iv)

    fig = go.Figure([
        go.Scatter(x=ex, y=ey, mode="lines", line=dict(width=1, color="#90CAF9"), hoverinfo="none"),
        go.Scatter(
            x=nx_, y=ny_, mode="markers+text",
            text=[pmap.get(n, {}).get("nombre", "?")[:18] for n in G.nodes()],
            textposition="top center", textfont=dict(size=9),
            hovertext=nt_, hoverinfo="text",
            marker=dict(
                size=ns_, color=nc_,
                colorscale=[[0, "#E3F2FD"], [0.5, "#42A5F5"], [1, "#1565C0"]],
                line=dict(width=1, color="white"),
                colorbar=dict(title="Índice"),
            ),
        ),
    ])
    fig.update_layout(
        showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=20, b=20), height=600,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    hubs = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:5]
    st.markdown("**Hubs:** " + ", ".join(pmap.get(h[0], {}).get("nombre", "?") for h in hubs))
    st.markdown(f"**Densidad:** {nx.density(G):.3f} · **Clusters:** {nx.number_connected_components(G)}")


# ============================================================
# PAGE: NEW PROFILE (multi-step form)
# ============================================================
def render_new_profile():
    st.markdown(f"## {t('nav.new_profile', lang)}")
    steps = [
        t("form.step_identity", lang), t("form.step_location", lang),
        t("form.step_regeneration", lang), t("form.step_impact", lang),
        t("form.step_network", lang), t("form.step_territory", lang),
    ]
    cur = st.session_state.form_step
    fd = st.session_state.form_data

    # Step indicator
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        status = "step-active" if i == cur else "step-done" if i < cur else "step-pending"
        col.markdown(
            f'<div style="text-align:center"><div class="step-dot {status}" style="margin:auto">{i+1}</div>'
            f"<small>{step}</small></div>",
            unsafe_allow_html=True,
        )
    st.markdown("")

    if cur == 0:  # Identity
        fd["nombre"] = st.text_input(t("form.name", lang), value=fd.get("nombre", ""))
        at = get_actor_types(lang)
        atk = list(at.keys())
        fd["tipo_actor"] = st.selectbox(
            t("form.actor_type", lang), atk,
            index=atk.index(fd.get("tipo_actor", "persona")) if fd.get("tipo_actor") in atk else 0,
            format_func=lambda x: at[x],
        )
        fd["descripcion"] = st.text_area(t("form.description", lang), value=fd.get("descripcion", ""))
        fd["email"] = st.text_input(t("form.email", lang), value=fd.get("email", ""))
        fd["web"] = st.text_input(t("form.web", lang), value=fd.get("web", ""))

    elif cur == 1:  # Location
        fd["pais"] = st.text_input(t("form.country", lang), value=fd.get("pais", ""))
        fd["region"] = st.text_input(t("form.region", lang), value=fd.get("region", ""))
        fd["ciudad"] = st.text_input(t("form.city", lang), value=fd.get("ciudad", ""))
        fd["comuna"] = st.text_input(t("form.commune", lang), value=fd.get("comuna", ""))
        c1, c2 = st.columns(2)
        fd["lat"] = c1.number_input("Lat", value=float(fd.get("lat", 0)), format="%.4f")
        fd["lon"] = c2.number_input("Lon", value=float(fd.get("lon", 0)), format="%.4f")

    elif cur == 2:  # Regeneration
        dims = get_dimensions(lang)
        fd["dimensiones_regeneracion"] = st.multiselect(
            t("form.dimensions", lang),
            [d["id"] for d in dims],
            default=fd.get("dimensiones_regeneracion", []),
            format_func=lambda x: next((f'{d["icon"]} {d["name"]}' for d in dims if d["id"] == x), x),
        )
        st.markdown(f"### {t('form.actions_label', lang)}")
        sel = fd.get("acciones", [])
        new_a = []
        for ax in axes_data:
            with st.expander(f"{ax['icon']} {ax['name']}"):
                for a in ax["actions"]:
                    if st.checkbox(a["name"], value=a["id"] in sel, key=f"a_{a['id']}"):
                        new_a.append(a["id"])
        fd["acciones"] = new_a
        fd["interpretacion_regeneracion"] = st.text_area(
            t("form.interpretation", lang), value=fd.get("interpretacion_regeneracion", ""),
        )

    elif cur == 3:  # Impact
        ir = get_impact_ranges(lang)
        irk = list(ir.keys())
        fd["personas_impactadas"] = ir[st.selectbox(
            t("form.people_impacted", lang), irk, format_func=lambda x: ir[x],
        )]
        fd["hectareas_regeneradas"] = st.text_input(
            t("form.hectares", lang), value=fd.get("hectareas_regeneradas", "0"),
        )
        fd["ano_inicio_regeneracion"] = st.number_input(
            t("form.year_started", lang), 1960, 2026, value=fd.get("ano_inicio_regeneracion", 2020),
        )

    elif cur == 4:  # Network
        rs = st.text_input(t("form.networks", lang), value=", ".join(fd.get("redes_participa", [])))
        fd["redes_participa"] = [r.strip() for r in rs.split(",") if r.strip()]
        st.markdown(f"### {t('form.connections', lang)}")
        existing = [p for p in profiles if p["id"] != fd.get("id")]
        ct = get_connection_types(lang)
        if "pending_connections" not in fd:
            fd["pending_connections"] = []
        sp = st.selectbox(
            "Conectar con", [""] + [p["id"] for p in existing],
            format_func=lambda x: next((p["nombre"] for p in existing if p["id"] == x), "---") if x else "---",
        )
        stype = st.selectbox(t("form.connection_type", lang), list(ct.keys()), format_func=lambda x: ct[x])
        if st.button("➕ Agregar conexión"):
            if sp:
                fd["pending_connections"].append({
                    "target_id": sp, "tipo": stype,
                    "nombre": next((p["nombre"] for p in existing if p["id"] == sp), "?"),
                    "es_externa": False,
                })
        ext = st.text_input(t("form.external_name", lang))
        if st.button("👻 Agregar conexión externa"):
            if ext.strip():
                fd["pending_connections"].append({
                    "target_id": None, "tipo": stype, "nombre": ext.strip(), "es_externa": True,
                })
        for pc in fd.get("pending_connections", []):
            st.markdown(f"{'👻' if pc['es_externa'] else '🔗'} **{pc['nombre']}** — {ct.get(pc['tipo'], '')}")

    elif cur == 5:  # Territory
        st.markdown(f"### {t('form.impact_locations', lang)}")
        if "pending_territories" not in fd:
            fd["pending_territories"] = []
        tp = st.text_input(t("form.country", lang), key="tp")
        tc = st.text_input(t("form.city", lang), key="tc")
        if st.button("📍 Agregar territorio"):
            if tp.strip():
                fd["pending_territories"].append({"pais": tp.strip(), "ciudad": tc.strip()})
        for tr in fd.get("pending_territories", []):
            st.markdown(f"📍 {tr['ciudad']}, {tr['pais']}")

    # Navigation
    st.markdown("")
    c1, _, c3 = st.columns([1, 1, 1])
    if cur > 0:
        with c1:
            if st.button(f"← {t('form.previous', lang)}"):
                st.session_state.form_step -= 1
                st.rerun()
    if cur < len(steps) - 1:
        with c3:
            if st.button(f"{t('form.next', lang)} →", type="primary"):
                st.session_state.form_step += 1
                st.rerun()
    else:
        with c3:
            if st.button(f"💾 {t('form.save', lang)}", type="primary"):
                fd["user_id"] = st.session_state.user_id
                fd["es_fantasma"] = False
                pid = db.save_profile(fd)
                for pc in fd.get("pending_connections", []):
                    if pc.get("es_externa"):
                        gid = db.save_profile({
                            "user_id": st.session_state.user_id, "nombre": pc["nombre"],
                            "tipo_actor": "persona", "es_fantasma": True, "pais": "",
                            "dimensiones_regeneracion": [], "acciones": [], "redes_participa": [],
                        })
                        db.add_connection({
                            "source_profile_id": pid, "target_profile_id": gid,
                            "tipo_relacion": pc["tipo"], "intensidad": 3, "es_externa": True,
                        })
                    elif pc.get("target_id"):
                        db.add_connection({
                            "source_profile_id": pid, "target_profile_id": pc["target_id"],
                            "tipo_relacion": pc["tipo"], "intensidad": 3, "es_externa": False,
                        })
                st.success(t("form.saved_ok", lang))
                st.session_state.form_data = {}
                st.session_state.form_step = 0
                nav("profiles")
                st.rerun()

    st.session_state.form_data = fd


# ============================================================
# PAGE: MY PROFILES
# ============================================================
def render_my_profiles():
    st.markdown(f"## {t('nav.my_profiles', lang)}")
    my = db.get_user_profiles(st.session_state.user_id)
    if not my:
        st.info("No tienes perfiles aún." if lang == "es" else "No profiles yet.")
        if st.button(t("nav.new_profile", lang)):
            nav("new_profile")
            st.rerun()
        return
    for p in my:
        st.markdown(
            f'<div class="profile-card"><h3>{p["nombre"]}</h3>'
            f'<p>📍 {p.get("ciudad","")}, {p.get("pais","")} · 🧭 {p.get("indice_puentes",0):.0f}/100</p></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"👁️ Ver {p['nombre']}", key=f"s_{p['id']}"):
            st.session_state.selected_profile = p["id"]
            nav("profile_detail")
            st.rerun()


# ============================================================
# PAGE: FORUM
# ============================================================
def render_forum():
    st.markdown(f"## {t('forum.title', lang)}")
    with st.expander(f"➕ {t('forum.new_thread', lang)}"):
        nc = st.text_area(t("forum.content", lang), key="nt")
        if st.button(t("forum.post", lang), key="pt"):
            if nc.strip():
                db.add_message({"user_id": st.session_state.user_id, "contenido": nc, "parent_id": None, "autor_nombre": "Demo User"})
                st.rerun()

    for msg in db.get_messages(parent_id=None):
        st.markdown(
            f'<div class="forum-msg"><strong>{msg.get("autor_nombre","")}</strong>'
            f' <span style="color:#90A4AE;font-size:0.8rem">· {msg.get("fecha","")[:10]}</span>'
            f'<p>{msg["contenido"]}</p></div>',
            unsafe_allow_html=True,
        )
        for r in db.get_messages(parent_id=msg["id"]):
            st.markdown(
                f'<div class="forum-msg forum-reply"><strong>{r.get("autor_nombre","")}</strong>'
                f' <span style="color:#90A4AE;font-size:0.8rem">· {r.get("fecha","")[:10]}</span>'
                f'<p>{r["contenido"]}</p></div>',
                unsafe_allow_html=True,
            )
        with st.expander(f"↩️ {t('forum.reply', lang)}"):
            rc = st.text_area(t("forum.content", lang), key=f"r_{msg['id']}")
            if st.button(t("forum.post", lang), key=f"pr_{msg['id']}"):
                if rc.strip():
                    db.add_message({"user_id": st.session_state.user_id, "contenido": rc, "parent_id": msg["id"], "autor_nombre": "Demo User"})
                    st.rerun()


# ============================================================
# PAGE: BIBLIOGRAPHY
# ============================================================
def render_bibliography():
    st.markdown(f"## {t('bibliography.title', lang)}")
    for b in get_bibliography():
        st.markdown(f"### 📖 {b['titulo']}")
        st.markdown(f"**{b['autor']}**")
        if b.get("descripcion"):
            st.markdown(b["descripcion"])
        if b.get("link"):
            st.markdown(f"🔗 [{b['link']}]({b['link']})")
        st.divider()


# ============================================================
# PAGE: ADMIN
# ============================================================
def render_admin():
    st.markdown(f"## {t('admin.title', lang)}")
    if not is_admin():
        st.error(t("admin.access_denied", lang))
        return
    if APP_MODE != "demo" and ADMIN_PASSWORD and not st.session_state.admin_unlocked:
        pwd = st.text_input(t("admin.enter_password", lang), type="password")
        if st.button(t("admin.unlock", lang)):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error(t("admin.wrong_password", lang))
        return
    if APP_MODE == "demo":
        st.info(t("admin.demo_admin_note", lang))

    c1, c2, c3 = st.columns(3)
    ng = [p for p in profiles if not p.get("es_fantasma")]
    with c1:
        render_metric(len(ng), "Perfiles")
    with c2:
        render_metric(len(connections), "Conexiones")
    with c3:
        render_metric(len(set(p.get("pais") for p in ng if p.get("pais"))), "Países")

    st.markdown("---")
    st.markdown(f"### {t('admin.download_title', lang)}")
    st.markdown(t("admin.download_desc", lang))
    try:
        excel_data, filename = export_database_to_excel(
            db, lang, get_dimensions, get_axes, get_actor_types,
            get_connection_types, calculate_all_indices,
        )
        st.download_button(
            label=t("admin.download_btn", lang), data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary", use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error: {e}")

    with st.expander("👁️ Vista previa"):
        import pandas as pd
        st.dataframe(
            pd.DataFrame([
                {"Nombre": p["nombre"], "País": p.get("pais", ""), "Índice": round(p.get("indice_puentes", 0), 1)}
                for p in profiles
            ]),
            use_container_width=True, hide_index=True,
        )


# ============================================================
# ROUTER
# ============================================================
page = st.session_state.page
try:
    {
        "map": render_map_page,
        "profiles": render_profiles_page,
        "profile_detail": render_profile_detail,
        "network": render_network_page,
        "new_profile": render_new_profile,
        "my_profiles": render_my_profiles,
        "forum": render_forum,
        "bibliography": render_bibliography,
        "admin": render_admin,
    }.get(page, render_map_page)()
except ImportError as e:
    st.warning(f"Dependencia faltante: `pip install folium streamlit-folium plotly pandas networkx`\n\n{e}")

st.markdown(
    f'<div class="footer">{t("app_subtitle", lang)} · {t("developed_by", lang)}</div>',
    unsafe_allow_html=True,
)

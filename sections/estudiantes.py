import streamlit as st
from utils.loaders import load_estudiantes, load_cursos, load_becas, load_academico
from components.cards import (
    render_kpi_ribbon,
    render_polity_cards,
    render_estudiantes_apuntes,
    render_cursos_grid,
    render_becas_grid,
    render_academico_carousel
)


def _index_subsecciones(subsecciones: list) -> dict:
    """Indexa las subsecciones por ID para acceso O(1) sin bucles condicionales anidados."""
    return {s.get("id", f"idx_{i}"): s for i, s in enumerate(subsecciones)}


def _matches_curso(c: dict, mod: str, costo: str, q: str) -> bool:
    if mod != "Todas" and c.get("modalidad") != mod:
        return False
    if costo != "Todos" and c.get("costo") != costo:
        return False
    if not q:
        return True
    blob = f"{c.get('nombre', '')} {c.get('proveedor', '')} {c.get('tema', '')} {c.get('descripcion_corta', '')}".lower()
    return q in blob


def _filter_cursos(cursos: list, mod: str, costo: str, query: str) -> list:
    q = query.lower().strip()
    return [c for c in cursos if _matches_curso(c, mod, costo, q)]


def _render_tab_sistemas(sub_map: dict):
    apuntes = sub_map.get("est_sub_5", {}).get("apuntes", [])
    st.subheader("📚 Sistemas Administrativos del Estado Peruano")
    st.markdown("Síntesis teóricas y enlaces directos a la normativa rectora de los sistemas administrativos (Ley N° 29158 - LOPE).")
    render_estudiantes_apuntes(apuntes)


def _render_tab_cursos(sub_map: dict, cursos: list):
    st.subheader("🎓 Catálogo de Cursos, MOOCs y Materiales Abiertos (MIT OCW / ENAP / BID / CEPAL)")
    if cursos:
        col1, col2, col3 = st.columns([2, 1, 1])
        modalidades = ["Todas"] + sorted({c.get("modalidad", "") for c in cursos if c.get("modalidad")})
        costos = ["Todos"] + sorted({c.get("costo", "") for c in cursos if c.get("costo")})
        with col1:
            q_curso = st.text_input(
                "🔎 Buscar por curso, universidad o temática:",
                placeholder="Ej: MIT, R, Estadística, SERVIR, CEPAL, Ciencia Política...",
                key="est_curso_search"
            )
        with col2:
            f_mod = st.selectbox("Modalidad:", modalidades, key="est_curso_mod")
        with col3:
            f_costo = st.selectbox("Costo:", costos, key="est_curso_costo")

        filtrados = _filter_cursos(cursos, f_mod, f_costo, q_curso)
        st.caption(f"Mostrando **{len(filtrados)}** de **{len(cursos)}** programas formativos verificados.")
        render_cursos_grid(filtrados)

    st.markdown("---")
    st.subheader("🛠️ Herramientas Metodológicas y Analíticas")
    render_polity_cards(sub_map.get("est_sub_2", {}).get("tarjetas", []))


def _render_tab_investigacion(sub_map: dict, academico_data: list):
    st.subheader("🔬 Últimas Alertas Académicas (OpenAlex, Politai, CLACSO)")
    render_academico_carousel(academico_data)
    st.markdown("---")
    st.subheader("📖 Estado del Arte y Repositorios de Investigación")
    render_polity_cards(sub_map.get("est_sub_1", {}).get("tarjetas", []))
    st.markdown("---")
    st.subheader("🗳️ Coyuntura y Debate Institucional")
    render_polity_cards(sub_map.get("est_sub_3", {}).get("tarjetas", []))


def _render_tab_becas_y_redes(sub_map: dict, becas: list):
    st.subheader("🏆 Becas, Movilidad y Oportunidades")
    render_becas_grid(becas)
    st.markdown("---")
    st.subheader("🤝 Redes Estudiantiles, Congresos y Colegiatura Profesional (CPOL)")
    render_polity_cards(sub_map.get("est_sub_4", {}).get("tarjetas", []))


def render_estudiantes():
    st.title("🎓 Estudiantes y Formación Metodológica")
    st.markdown(
        '<div class="banner-demo-top">🚀 <strong>Ecosistema Formativo Activo:</strong> '
        'Guías de los sistemas administrativos del Estado, catálogo de cursos abiertos (MIT OCW, ENAP, CEPAL, BID), '
        'alertas bibliográficas vía OpenAlex y oportunidades de becas actualizadas automáticamente.</div>',
        unsafe_allow_html=True
    )

    subsecciones = load_estudiantes()
    if not subsecciones:
        st.info("No se encontró información en data/estudiantes.json.")
        return

    sub_map = _index_subsecciones(subsecciones)
    cursos = load_cursos()
    becas = load_becas()
    academico_data = load_academico()
    apuntes_count = len(sub_map.get("est_sub_5", {}).get("apuntes", []))

    render_kpi_ribbon([
        {"icon": "📚", "value": str(apuntes_count), "label": "Sistemas del Estado", "sub": "Guías normativas verificadas"},
        {"icon": "🎓", "value": str(len(cursos)), "label": "Cursos y MOOCs", "sub": "MIT OCW, ENAP, BID, CEPAL, R"},
        {"icon": "🔬", "value": str(len(academico_data)), "label": "Papers en Radar", "sub": "OpenAlex, Politai y CLACSO"},
        {"icon": "🏆", "value": str(len(becas)), "label": "Portales de Becas", "sub": "PRONABEC y SENAJU"},
    ])

    tab1, tab2, tab3, tab4 = st.tabs([
        f"📚 Sistemas del Estado ({apuntes_count})",
        f"🎓 Catálogo de Cursos ({len(cursos)})",
        f"🔬 Investigación y Alertas ({len(academico_data)})",
        f"🏆 Becas y Redes ({len(becas)})",
    ])

    with tab1:
        _render_tab_sistemas(sub_map)
    with tab2:
        _render_tab_cursos(sub_map, cursos)
    with tab3:
        _render_tab_investigacion(sub_map, academico_data)
    with tab4:
        _render_tab_becas_y_redes(sub_map, becas)

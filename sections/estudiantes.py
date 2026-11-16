import streamlit as st

from components.cards import (
    render_becas_grid,
    render_cursos_grid,
    render_estudiantes_apuntes,
    render_kpi_ribbon,
    render_polity_cards,
)
from utils.loaders import (
    load_becas,
    load_cursos,
    load_estudiantes,
)


def _index_subsecciones(subsecciones: list) -> dict:
    """Indexa las subsecciones por ID para acceso O(1)."""
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


def _render_tab_sistemas(sub_map: dict) -> None:
    apuntes = sub_map.get("est_sub_5", {}).get("apuntes", [])
    st.subheader("🏛️ Sistemas Administrativos del Estado (LOPE)")
    st.caption("Guías breves y normativa rectora de los sistemas nacionales bajo la Ley N° 29158.")
    render_estudiantes_apuntes(apuntes)


def _render_tab_cursos(sub_map: dict, cursos: list) -> None:
    st.subheader("🎓 Cursos Abiertos y Especialización")
    st.caption("Programas verificados de MIT OCW, ENAP-SERVIR, BID, CEPAL y análisis cuantitativo.")
    if cursos:
        col1, col2, col3 = st.columns([2, 1, 1])
        modalidades = ["Todas"] + sorted({c.get("modalidad", "") for c in cursos if c.get("modalidad")})
        costos = ["Todos"] + sorted({c.get("costo", "") for c in cursos if c.get("costo")})
        with col1:
            q_curso = st.text_input(
                "🔎 Buscar curso o institución:",
                placeholder="Ej: MIT, R, Estadística, SERVIR, CEPAL...",
                key="est_curso_search",
            )
        with col2:
            f_mod = st.selectbox("Modalidad:", modalidades, key="est_curso_mod")
        with col3:
            f_costo = st.selectbox("Costo:", costos, key="est_curso_costo")

        filtrados = _filter_cursos(cursos, f_mod, f_costo, q_curso)
        st.caption(f"Mostrando **{len(filtrados)}** de **{len(cursos)}** cursos.")
        render_cursos_grid(filtrados)

    tools = sub_map.get("est_sub_2", {}).get("tarjetas", [])
    if tools:
        st.markdown("---")
        st.subheader("🛠️ Caja de Herramientas Metodológicas")
        render_polity_cards(tools)


def _render_tab_becas(sub_map: dict, becas: list) -> None:
    st.subheader("🏆 Portales de Becas y Movilidad")
    render_becas_grid(becas)
    gremio = sub_map.get("est_sub_4", {}).get("tarjetas", [])
    if gremio:
        st.markdown("---")
        st.subheader("🤝 Colegiatura y Representación Profesional")
        render_polity_cards(gremio)


def render_estudiantes() -> None:
    st.title("🎓 Escuela Pública y Becas")
    st.markdown(
        '<p class="hero-subtitle">Sistemas administrativos del Estado (LOPE), catálogo de cursos, guías metodológicas y becas.</p>',
        unsafe_allow_html=True,
    )

    subsecciones = load_estudiantes()
    if not subsecciones:
        st.info("No se encontró información formativa registrada.")
        return

    sub_map = _index_subsecciones(subsecciones)
    cursos = load_cursos()
    becas = load_becas()
    apuntes_count = len(sub_map.get("est_sub_5", {}).get("apuntes", []))
    tools_count = len(sub_map.get("est_sub_2", {}).get("tarjetas", []))

    render_kpi_ribbon([
        {"icon": "🏛️", "value": str(apuntes_count), "label": "Sistemas LOPE", "sub": "Normativa rectora estatal"},
        {"icon": "🎓", "value": str(len(cursos)), "label": "Cursos Abiertos", "sub": "MIT, ENAP, BID, CEPAL"},
        {"icon": "🛠️", "value": str(tools_count), "label": "Guías Técnicas", "sub": "R, Python y evaluación"},
        {"icon": "🏆", "value": str(len(becas)), "label": "Becas y Gremio", "sub": "PRONABEC, SENAJU y CPOL"},
    ])

    tab1, tab2, tab3 = st.tabs([
        f"🏛️ Sistemas del Estado ({apuntes_count})",
        f"🎓 Cursos y Metodología ({len(cursos)})",
        f"🏆 Becas y Colegio ({len(becas)})",
    ])

    with tab1:
        _render_tab_sistemas(sub_map)
    with tab2:
        _render_tab_cursos(sub_map, cursos)
    with tab3:
        _render_tab_becas(sub_map, becas)

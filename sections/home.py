import streamlit as st

from components.apocunoso_branding import build_apocunoso_hero_banner_html
from components.cards import (
    render_home_radar_and_boletines_split,
    render_noticias_carousel,
)
from sections.normas_comentadas import navegar_a_normas_comentadas
from utils.loaders import (
    load_dashboard_kpis,
    load_noticias_grouped,
)


def _go_to_page(page_name: str, clear_qp: bool = True) -> None:
    if clear_qp:
        for qp_k in ("vista", "norma", "ficha"):
            if qp_k in st.query_params:
                del st.query_params[qp_k]
    st.session_state.current_page = page_name
    theme_key = f"apocuna_nav_{st.session_state.get('theme_mode', '💻 Auto')}"
    st.session_state.pop(theme_key, None)
    st.session_state.pop("_last_sidebar_menu", None)
    st.rerun()


def _render_hero_banner() -> None:
    st.markdown(build_apocunoso_hero_banner_html(), unsafe_allow_html=True)


def _render_quick_nav_row() -> None:
    """Accesos directos por intención de uso en la primera pantalla."""
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    accesos = [
        (
            c1,
            "quick_blue",
            "⚖️ NORMATIVA DIARIA",
            "Rastrea la Norma",
            "El Peruano clasificado por Polity y Policy.",
            "Ir a Normas →",
            "btn_quick_normas",
            lambda: navegar_a_normas_comentadas(),
        ),
        (
            c2,
            "quick_green",
            "📊 BASES Y CEPLAN",
            "Políticas y Datos",
            "Microdatos con ficha, CEPLAN y evaluaciones.",
            "Explorar Datos →",
            "btn_quick_datos",
            lambda: _go_to_page("Políticas y Datos"),
        ),
        (
            c3,
            "quick_gold",
            "🌊 RIESGO CLIMÁTICO",
            "Monitoreo El Niño",
            "Visores satelitales, radar y PP 0068 PREVAED.",
            "Abrir Visores →",
            "btn_quick_fen",
            lambda: _go_to_page("Monitoreo El Niño"),
        ),
        (
            c4,
            "quick_pink",
            "📚 REVISTAS Y ESCUELA",
            "Biblioteca y Becas",
            "Notas, revistas LatAm, sistemas LOPE y cursos.",
            "Ir a Biblioteca →",
            "btn_quick_bib",
            lambda: _go_to_page("Biblioteca y Revistas"),
        ),
    ]

    for col, cls, tag, title, desc, btn_txt, btn_key, callback in accesos:
        with col:
            st.markdown(
                f'<div class="home-quick-nav-card {cls}">'
                f'<div class="home-quick-tag">{tag}</div>'
                f'<h3>{title}</h3>'
                f'<p>{desc}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(btn_txt, key=btn_key, use_container_width=True):
                callback()


def render_home():
    _render_hero_banner()
    _render_quick_nav_row()

    st.markdown("<div style='height:0.65rem;'></div>", unsafe_allow_html=True)

    # PULSO DIARIO: KPIs (izquierda) + Boletín del día (derecha)
    kpis = load_dashboard_kpis()
    render_home_radar_and_boletines_split([
        {
            "icon": "📰",
            "value": str(kpis["noticias_total"]),
            "label": "Noticias en Radar",
            "sub": "Gestión, Políticas y Coyuntura",
            "href": "#radar-noticias",
        },
        {
            "icon": "⚖️",
            "value": str(kpis["normas_total"]),
            "label": "Normas en Seguimiento",
            "sub": "Radar regulatorio diario",
            "href": "?vista=normas_comentadas",
        },
        {
            "icon": "🗄️",
            "value": str(kpis["fuentes_total"]),
            "label": "Fuentes con Ficha",
            "sub": f"{kpis.get('evaluaciones_total', 27)} evaluaciones públicas",
            "href": "?vista=polity",
        },
        {
            "icon": "🎓",
            "value": str(kpis["oportunidades_total"]),
            "label": "Cursos, Becas y Eventos",
            "sub": f"Sync: {kpis['last_sync']}",
            "href": "?vista=escuela",
        },
    ])

    # NOTICIAS POR CATEGORÍA (pre-agrupadas en caché O(1))
    st.markdown('<div id="radar-noticias"></div>', unsafe_allow_html=True)
    st.header("📰 Radar de Noticias y Análisis")
    grupos_noticias = load_noticias_grouped()

    tab_n1, tab_n2, tab_n3 = st.tabs([
        f"📁 Gestión Pública ({len(grupos_noticias['gestion'])})",
        f"📊 Políticas Públicas ({len(grupos_noticias['politicas_publicas'])})",
        f"🏛️ Gobernabilidad ({len(grupos_noticias['politica'])})",
    ])

    with tab_n1:
        render_noticias_carousel("Gestión Pública", grupos_noticias["gestion"])
    with tab_n2:
        render_noticias_carousel("Políticas Públicas", grupos_noticias["politicas_publicas"])
    with tab_n3:
        render_noticias_carousel("Gobernabilidad", grupos_noticias["politica"])

    st.markdown("---")
    if st.button("ℹ️ Sobre Apocuna, Manual Breve y Leyenda de Etiquetas →", key="btn_conocer_sitio"):
        _go_to_page("Sobre Apocuna")

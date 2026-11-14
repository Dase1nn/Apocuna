import streamlit as st
from utils.loaders import (
    load_noticias_grouped,
    load_normas,
    load_normas_oficiales,
    load_politicas_nacionales,
    load_dashboard_kpis
)
from components.cards import (
    render_home_radar_and_boletines_split,
    render_noticias_carousel,
    render_normas_carousel
)
from sections.normas_comentadas import (
    navegar_a_normas_comentadas,
    render_normas_showcase_strip,
    render_normas_visual_collection,
)


def _render_hero_banner():
    st.markdown(
        """
        <div class="snow-card hero-intro-block">
            <div class="hero-eyebrow">PLATAFORMA PERUANA DE EVIDENCIA Y POLÍTICAS PÚBLICAS</div>
            <h1 class="hero-intro-title">¿Qué es APOCUNA y por qué existe?</h1>
            <p class="hero-intro-text">
                Un punto de encuentro que reúne herramientas, datos auditados y oportunidades de formación para quienes diseñan, evalúan y estudian la política pública en el Perú.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🏛️ Conocer la misión y metodología del sitio →", key="btn_conocer_sitio"):
        st.session_state.current_page = "Sobre el sitio"
        st.rerun()


def render_home():
    _render_hero_banner()

    # SECCIÓN DIVIDIDA: Radar de Coyuntura (izquierda) + Tarjeta Grande Boletines de Normas Legales con un café (derecha)
    kpis = load_dashboard_kpis()
    render_home_radar_and_boletines_split([
        {"icon": "📰", "value": str(kpis["noticias_total"]), "label": "Noticias en Radar", "sub": "Gestión, Políticas y Coyuntura"},
        {"icon": "⚖️", "value": str(kpis["normas_total"]), "label": "Normas Monitoreadas", "sub": "Seguimiento regulatorio diario"},
        {"icon": "🗄️", "value": str(kpis["fuentes_total"]), "label": "Fuentes Verificadas", "sub": "Disponibles en Polity & Policy"},
        {"icon": "🎓", "value": str(kpis["oportunidades_total"]), "label": "Cursos, Becas y Eventos", "sub": f"Sync: {kpis['last_sync']}"},
    ])

    # 1. NOTICIAS POR CATEGORÍA (pre-agrupadas en caché O(1))
    st.header("📰 Radar de Noticias y Análisis")
    grupos_noticias = load_noticias_grouped()

    tab_n1, tab_n2, tab_n3 = st.tabs([
        f"📁 Gestión Pública ({len(grupos_noticias['gestion'])})",
        f"📊 Políticas Públicas ({len(grupos_noticias['politicas_publicas'])})",
        f"🏛️ Política y Gobernabilidad ({len(grupos_noticias['politica'])})"
    ])

    with tab_n1:
        render_noticias_carousel("Gestión Pública", grupos_noticias["gestion"])
    with tab_n2:
        render_noticias_carousel("Políticas Públicas", grupos_noticias["politicas_publicas"])
    with tab_n3:
        render_noticias_carousel("Política y Gobernabilidad", grupos_noticias["politica"])

    st.markdown("---")

    # 2. NUEVA CATEGORÍA VISUAL: NORMAS LEGALES OFICIALES DE EL PERUANO (POLITY & POLICY)
    st.header("🏛️ Normas Legales Oficiales — El Peruano")
    st.markdown(
        "Clasificación diaria automatizada por ejes **Polity** (arquitectura institucional y gestión pública) "
        "y **Policy** (regulación sectorial), alineada con Políticas Nacionales."
    )
    fichas_oficiales = load_normas_oficiales()
    catalogo = load_politicas_nacionales()
    catalogo_map = {p["id"]: p["nombre"] for p in catalogo if isinstance(p, dict) and p.get("id")}

    if fichas_oficiales:
        render_normas_showcase_strip(fichas_oficiales)
        fichas_polity = [f for f in fichas_oficiales if (f.get("eje") or "").lower() == "polity"]
        fichas_policy = [f for f in fichas_oficiales if (f.get("eje") or "").lower() == "policy"]
        tab_of_all, tab_of_polity, tab_of_policy = st.tabs([
            f"📋 Todas ({len(fichas_oficiales)})",
            f"🏛️ Polity ({len(fichas_polity)})",
            f"📊 Policy ({len(fichas_policy)})",
        ])
        with tab_of_all:
            render_normas_visual_collection(fichas_oficiales, catalogo_map=catalogo_map, layout="carousel")
        with tab_of_polity:
            render_normas_visual_collection(fichas_polity, catalogo_map=catalogo_map, layout="carousel")
        with tab_of_policy:
            render_normas_visual_collection(fichas_policy, catalogo_map=catalogo_map, layout="carousel")

    if st.button(
        "⚖️ Abrir explorador completo y filtros en Polity & Policy →",
        key="btn_home_normas_comentadas",
    ):
        navegar_a_normas_comentadas()

    st.markdown("---")

    # 3. SEGUIMIENTO DE NORMAS LEGALES (COYUNTURA Y PRENSA)
    st.header("⚖️ Seguimiento de Normas Legales")
    st.markdown("Monitoreo regulatorio automatizado de decretos, leyes y resoluciones sectoriales en prensa.")
    normas = load_normas()
    normas_filtradas = [n for n in normas if n.get("grupo") == "Noticias sobre normas legales"] or normas
    render_normas_carousel(normas_filtradas)

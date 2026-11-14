import streamlit as st
from utils.loaders import (
    load_noticias_grouped,
    load_dashboard_kpis
)
from components.cards import (
    render_home_radar_and_boletines_split,
    render_noticias_carousel,
)
from sections.normas_comentadas import navegar_a_normas_comentadas


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

    st.subheader("🔍 Rastrea la Norma · Beta v1-rastro-norma")
    st.markdown(
        "Explora el nuevo flujo animado de seguimiento diario de **El Peruano**, "
        "tarjetas visuales por ejes **Polity / Policy** y el monitoreo regulatorio completo."
    )
    if st.button(
        "🔍 Abrir Rastrea la Norma (Beta v1-rastro-norma) →",
        key="btn_home_rastrea_norma",
    ):
        navegar_a_normas_comentadas()

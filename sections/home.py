import streamlit as st
from utils.loaders import (
    load_noticias_grouped,
    load_normas,
    fetch_ckan_datasets,
    load_fuentes,
    load_dashboard_kpis
)
from components.cards import (
    render_kpi_ribbon,
    render_noticias_carousel,
    render_normas_carousel,
    render_ckan_carousel,
    render_fuentes_grid
)

BLOQUES_FUENTES = [
    ("Datos abiertos y microdatos", "📊 1. Datos abiertos y microdatos", True),
    ("Control gubernamental y conflictividad social", "⚖️ 2. Control gubernamental y conflictividad social", False),
    ("Think tanks y repositorios", "🧠 3. Think tanks y repositorios académicos", False),
    ("Organismos multilaterales", "🌍 4. Organismos multilaterales y cooperación", False),
    ("Documentos e informes específicos", "📑 5. Documentos e informes específicos", False),
]


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


def _matches_fuente(f: dict, bloque_sel: str, q_lower: str) -> bool:
    if bloque_sel != "Todos los bloques" and f.get("bloque", "").lower() != bloque_sel.lower():
        return False
    if not q_lower:
        return True
    blob = f"{f.get('nombre', '')} {f.get('institucion', '')} {f.get('descripcion_corta', '')}".lower()
    return q_lower in blob


def _render_catalogo_fuentes(fuentes: list):
    st.header("📊 Catálogo Auditado de Fuentes de Información")
    st.markdown("Bases de datos oficiales, plataformas de microdatos y repositorios organizados por bloques temáticos.")

    col_search, col_bloque = st.columns([2, 1])
    with col_search:
        query = st.text_input(
            "🔎 Filtrar fuentes por institución, nombre o temática:",
            placeholder="Ej: INEI, ENAHO, GRADE, CEPAL, Contraloría, MINSA...",
            key="home_fuentes_search"
        )
    with col_bloque:
        opciones_bloque = ["Todos los bloques"] + [b[0] for b in BLOQUES_FUENTES]
        bloque_sel = st.selectbox("Bloque temático:", opciones_bloque, key="home_fuentes_bloque")

    q_lower = query.lower().strip()
    if q_lower or bloque_sel != "Todos los bloques":
        filtradas = [f for f in fuentes if _matches_fuente(f, bloque_sel, q_lower)]
        st.caption(f"Mostrando **{len(filtradas)}** de **{len(fuentes)}** fuentes registradas.")
        render_fuentes_grid(filtradas)
        return

    for key_bloque, titulo_bloque, exp_default in BLOQUES_FUENTES:
        fuentes_bloque = [f for f in fuentes if f.get("bloque", "").lower() == key_bloque.lower()]
        with st.expander(f"{titulo_bloque} ({len(fuentes_bloque)})", expanded=exp_default):
            render_fuentes_grid(fuentes_bloque)


def render_home():
    _render_hero_banner()

    st.title("🌐 Radar de Coyuntura, Normas y Fuentes Oficiales")
    st.markdown(
        '<p class="hero-subtitle">Vigilancia continua de políticas públicas, marco regulatorio y portales de datos abiertos del Perú.</p>',
        unsafe_allow_html=True
    )

    kpis = load_dashboard_kpis()
    render_kpi_ribbon([
        {"icon": "📰", "value": str(kpis["noticias_total"]), "label": "Noticias en Radar", "sub": "Gestión, Políticas y Coyuntura"},
        {"icon": "⚖️", "value": str(kpis["normas_total"]), "label": "Normas Monitoreadas", "sub": "Seguimiento regulatorio diario"},
        {"icon": "🗄️", "value": str(kpis["fuentes_total"]), "label": "Fuentes Verificadas", "sub": "5 bloques institucionales"},
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

    # 2. NORMAS LEGALES
    st.header("⚖️ Seguimiento de Normas Legales")
    st.markdown("Monitoreo regulatorio automatizado de decretos, leyes y resoluciones sectoriales.")
    normas = load_normas()
    normas_filtradas = [n for n in normas if n.get("grupo") == "Noticias sobre normas legales"] or normas
    render_normas_carousel(normas_filtradas)

    st.markdown("---")

    # 3. DATASETS RECIENTES Y PORTALES DE DATOS ABIERTOS
    st.header("🔄 Portales Nacionales de Datos Abiertos y Salud")
    st.markdown("Acceso directo a los catálogos nacionales de datos abiertos (PCM, GOB.PE, MINSA REUNIS y CDC Perú).")
    fuentes = load_fuentes()
    portales_ckan = [f for f in fuentes if f.get("id") in ("f_001", "f_002", "f_003", "f_004")]
    ckan_datasets = fetch_ckan_datasets()
    render_ckan_carousel(ckan_datasets, portales_directos=portales_ckan)

    st.markdown("---")

    # 4. DIRECTORIO DE FUENTES DE DATOS
    _render_catalogo_fuentes(fuentes)

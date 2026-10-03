import streamlit as st
from utils.loaders import (
    load_noticias,
    load_normas,
    fetch_ckan_datasets,
    load_fuentes
)
from components.cards import (
    render_noticias_carousel,
    render_normas_carousel,
    render_ckan_carousel,
    render_fuentes_grid
)

def render_home():
    # 1. BLOQUE EN HOME: ARRIBA DE TODO en Inicio, ANTES del título
    st.markdown(
        """
        <div class="snow-card hero-intro-block">
            <h1 class="hero-intro-title">¿Qué es APOCUNA y por qué existe?</h1>
            <p class="hero-intro-text">
                Un punto de encuentro que reúne herramientas, datos y oportunidades de formación para quienes hacen y estudian la política en el Perú. Descubre qué es APOCUNA, a quién sirve y hacia dónde va.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Conocer el sitio", key="btn_conocer_sitio"):
        st.session_state.current_page = "Sobre el sitio"
        st.rerun()

    # 2. TÍTULO DE INICIO Y SUBTÍTULO
    st.title("🌐 Inicio: Radar de Coyuntura, Normas y Fuentes")
    st.markdown(
        '<p class="hero-subtitle">Vigilancia endógena de políticas públicas, marco regulatorio y datos abiertos del Perú.</p>',
        unsafe_allow_html=True
    )
    
    # 1. NOTICIAS POR CATEGORÍA
    st.header("📰 Radar de Noticias y Análisis")
    noticias = load_noticias()
    # Ordenar de más reciente a menos reciente por fecha_iso
    noticias_ordenadas = sorted(noticias, key=lambda x: x.get("fecha_iso", ""), reverse=True)
    
    noticias_gestion = [n for n in noticias_ordenadas if n.get("categoria") == "gestion"]
    noticias_polpub = [n for n in noticias_ordenadas if n.get("categoria") == "politicas_publicas"]
    noticias_politica = [n for n in noticias_ordenadas if n.get("categoria") == "politica"]
    
    tab_n1, tab_n2, tab_n3 = st.tabs([
        "📁 Gestión Pública", 
        "📊 Políticas Públicas", 
        "🏛️ Política y Gobernabilidad"
    ])
    
    with tab_n1:
        render_noticias_carousel("Gestión Pública", noticias_gestion)
    with tab_n2:
        render_noticias_carousel("Políticas Públicas", noticias_polpub)
    with tab_n3:
        render_noticias_carousel("Política y Gobernabilidad", noticias_politica)
        
    st.markdown("---")
    
    # 2. NORMAS LEGALES DE EL PERUANO
    st.header("⚖️ Normas Legales")
    st.markdown("Seguimiento regulatorio de normas. *(Vía Google News, no es el listado oficial)*")
    normas = load_normas()
    
    normas_filtradas = [n for n in normas if n.get("grupo") == "Noticias sobre normas legales"]
    
    # Mostrar directamente en carrusel
    render_normas_carousel(normas_filtradas)
        
    st.markdown("---")
    
    # 3. DATASETS RECIENTES CKAN
    st.header("🔄 Datasets Recientes (Portales CKAN)")
    st.markdown("Consulta automatizada a los catálogos nacionales de datos abiertos (PCM y MINSA).")
    fuentes = load_fuentes()
    portales_ckan = [f for f in fuentes if f.get("id") in ["f_001", "f_004"]]
    ckan_datasets = fetch_ckan_datasets()
    render_ckan_carousel(ckan_datasets, portales_directos=portales_ckan)
    
    st.markdown("---")
    
    # 4. DIRECTORIO DE FUENTES DE DATOS (5 BLOQUES)
    st.header("📊 Catálogo de Fuentes de Información")
    st.markdown("Bases de datos, plataformas de microdatos y repositorios organizados por bloques temáticos.")
    
    fuentes = load_fuentes()
    
    bloques = [
        ("Datos abiertos y microdatos", "📊 1. Datos abiertos y microdatos", True),
        ("Control gubernamental y conflictividad social", "⚖️ 2. Control gubernamental y conflictividad social", False),
        ("Think tanks y repositorios", "🧠 3. Think tanks y repositorios académicos", False),
        ("Organismos multilaterales", "🌍 4. Organismos multilaterales y cooperación", False),
        ("Documentos e informes específicos", "📑 5. Documentos e informes específicos", False)
    ]
    
    for key_bloque, titulo_bloque, exp_default in bloques:
        fuentes_bloque = [f for f in fuentes if f.get("bloque", "").lower() == key_bloque.lower()]
        with st.expander(titulo_bloque, expanded=exp_default):
            render_fuentes_grid(fuentes_bloque)

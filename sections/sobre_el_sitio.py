"""Sección 'Sobre el sitio' estructurada en tarjetas ordenadas de 2 columnas (apocunoso-style)."""

import streamlit as st


TARJETAS_SOBRE_EL_SITIO = [
    {
        "orden": "01",
        "eyebrow": "HISTORIA INSTITUCIONAL · TAHUANTINSUYO",
        "color_class": "about-card-blue",
        "pregunta": "¿Qué eran los Apocuna?",
        "contenido_html": (
            "<p>En la organización política del Tahuantinsuyo, los <strong>Apocuna</strong> "
            "(plural de <em>Apu</em>, «grandes señores» o «autoridades principales») integraban el "
            "Consejo Imperial encargado de asesorar al Sapa Inca y administrar los cuatro <em>suyus</em> "
            "del territorio (Rostworowski, 1999).</p>"
            "<p>Su labor consistía en articular el gobierno central con las realidades locales, supervisar "
            "la ejecución de obras públicas y tomar decisiones basadas en los registros estadísticos que los "
            "<em>quipucamayoc</em> recolectaban en cada región (Espinoza Soriano, 1997; Murra, 1975). "
            "Inspirado en esta institución de alta dirección territorial, <strong>APOCUNA</strong> busca "
            "traducir los datos públicos y la producción normativa del Perú contemporáneo en evidencia "
            "accesible para el análisis y la gestión pública.</p>"
        ),
    },
    {
        "orden": "02",
        "eyebrow": "MARCO ANALÍTICO · POLITY, POLITICS & POLICY",
        "color_class": "about-card-green",
        "pregunta": "¿Cuál es el oficio del politólogo y el análisis político?",
        "contenido_html": (
            "<p>La ciencia política contemporánea nos exige comprender la política desde sus múltiples "
            "dimensiones. Siguiendo la distinción clásica, el análisis debe abordar la <strong>polity</strong> "
            "(las estructuras e instituciones del Estado), la <strong>politics</strong> (la dinámica del poder, "
            "los actores y las elecciones) y las <strong>policies</strong> (las políticas públicas y las "
            "decisiones gubernamentales).</p>"
            "<p>En este contexto, el rol de quienes analizan lo público adquiere una doble dimensión: académica "
            "y profesional. <em>«Como científico, el politólogo debe saber identificar problemas, como "
            "profesional, debe coadyuvar a resolverlos»</em> (Barrientos, 2019, p. 12). Apocuna busca ser un "
            "puente entre estas esferas, proporcionando insumos tanto para la investigación rigurosamente "
            "fundada como para la toma de decisiones informada.</p>"
        ),
    },
    {
        "orden": "03",
        "eyebrow": "ARQUITECTURA DE DATOS · ECOSISTEMA PÚBLICO",
        "color_class": "about-card-gold",
        "pregunta": "¿Cómo mapeamos las organizaciones y recursos?",
        "contenido_html": (
            "<p>Para cumplir su objetivo, la plataforma integra un mapeo sistemático y auditado de actores "
            "y fuentes clave en tres niveles complementarios:</p>"
            "<ul>"
            "<li><strong>Instituciones Estatales:</strong> Repositorios de datos abiertos, seguimiento diario de "
            "normatividad en <em>El Peruano</em>, sistemas administrativos y estadísticas oficiales.</li>"
            "<li><strong>Centros de Investigación y Think Tanks:</strong> Espacios de producción de conocimiento "
            "empírico, evaluación de políticas y documentos de balance.</li>"
            "<li><strong>Redes Académicas y Estudiantiles:</strong> Congresos, revistas arbitradas, becas y "
            "asociaciones que fomentan la deliberación y la profesionalización de la disciplina.</li>"
            "</ul>"
        ),
    },
    {
        "orden": "04",
        "eyebrow": "PROYECCIÓN CIENTÍFICA · ESTILO APOCUNOSO",
        "color_class": "about-card-pink",
        "pregunta": "¿Hacia dónde va nuestra discusión científica e identidad?",
        "contenido_html": (
            "<p><strong>Apocuna</strong> no es solo un repositorio estático, sino un proyecto vivo que aspira a "
            "fomentar una discusión científica permanente. Buscamos expandir el alcance de nuestros indicadores, "
            "automatizar la trazabilidad normativa con verificación estricta y propiciar el intercambio de ideas "
            "metodológicas y teóricas que contribuyan al fortalecimiento institucional y democrático.</p>"
            "<p>Visualmente, la plataforma adopta el sistema <strong>apocunoso-style</strong>: una síntesis entre "
            "la arquitectura de marcos geométricos, la cartografía amazónica peruana <strong>Kené</strong> del "
            "pueblo Shipibo-Konibo (Patrimonio Cultural de la Nación) y la legibilidad editorial de la "
            "tipografía <strong>Swiss International</strong>.</p>"
        ),
    },
]


REFERENCIAS_APA = [
    (
        "Barrientos del Monte, F. (2019).",
        "<em>El oficio de politólogo (El rol del politólogo en la sociedad)</em>. Conferencia.",
    ),
    (
        "Cieza de León, P. (2005).",
        "<em>Crónica del Perú: El señorío de los Incas</em> (F. Cantù, Ed.). Biblioteca Ayacucho. (Obra original publicada en 1553).",
    ),
    (
        "Espinoza Soriano, W. (1997).",
        "<em>Los Incas: Economía, sociedad y Estado en la era del Tahuantinsuyo</em> (3.ª ed.). Amaru Editores.",
    ),
    (
        "Guamán Poma de Ayala, F. (1980).",
        "<em>El primer nueva corónica y buen gobierno</em> (J. V. Murra y R. Adorno, Eds.). Siglo XXI Editores. (Obra original escrita ca. 1615).",
    ),
    (
        "Murra, J. V. (1975).",
        "<em>Formaciones económicas y políticas del mundo andino</em>. Instituto de Estudios Peruanos (IEP).",
    ),
    (
        "Pease, F. (1991).",
        "<em>Los últimos incas del Cuzco</em>. Alianza Editorial.",
    ),
    (
        "Rostworowski, M. (1999).",
        "<em>Historia del Tahuantinsuyo</em> (2.ª ed.). Instituto de Estudios Peruanos (IEP).",
    ),
]


def render_sobre_el_sitio() -> None:
    """Renderiza la sección 'Sobre el sitio' con tarjetas ordenadas en 2 columnas."""
    st.title("🏛️ Sobre Apocuna: Propósito, Identidad y Metodología")

    # Bloque introductorio general a ancho completo (Orden 00)
    st.markdown(
        """
        <div class="apocunoso-about-intro">
            <div class="apocunoso-about-intro-head">
                <span class="apocunoso-order-badge">00 · PROPÓSITO GENERAL</span>
                <span class="apocunoso-about-tag">CIENCIA POLÍTICA &amp; GESTIÓN PÚBLICA EN EL PERÚ</span>
            </div>
            <h2 class="apocunoso-about-intro-title">¿Por qué nace Apocuna Hub?</h2>
            <p class="apocunoso-about-intro-text">
                <strong>Apocuna</strong> surge como una iniciativa orientada a consolidar un espacio de información,
                análisis y recursos para el estudio y la práctica de la ciencia política y la gestión pública en el Perú.
                Nuestro propósito es facilitar el acceso a evidencia empírica, seguimiento normativo diario, herramientas
                metodológicas y espacios de debate para la comunidad politológica, académica y ciudadana.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Grilla de 2 columnas con las 4 preguntas numeradas en orden (01, 02, 03, 04)
    cards_html = []
    for item in TARJETAS_SOBRE_EL_SITIO:
        cards_html.append(
            f'<article class="apocunoso-about-card {item["color_class"]}">'
            f'<div class="apocunoso-about-card-topbar"></div>'
            f'<div class="apocunoso-about-card-inner">'
            f'<div class="apocunoso-about-card-meta">'
            f'<span class="apocunoso-order-badge">PASO {item["orden"]}</span>'
            f'<span class="apocunoso-about-eyebrow">{item["eyebrow"]}</span>'
            f'</div>'
            f'<h3 class="apocunoso-about-question">{item["pregunta"]}</h3>'
            f'<div class="apocunoso-about-body">{item["contenido_html"]}</div>'
            f'</div>'
            f'</article>'
        )

    st.markdown(
        f'<div class="apocunoso-about-grid-2col">{"".join(cards_html)}</div>',
        unsafe_allow_html=True,
    )

    # Tarjeta inferior de ancho completo para Referencias Bibliográficas (Orden 05)
    refs_items = "".join(
        f'<div class="apocunoso-ref-item"><strong>{autor}</strong> {obra}</div>'
        for autor, obra in REFERENCIAS_APA
    )
    st.markdown(
        f"""
        <div class="apocunoso-about-refs-card">
            <div class="apocunoso-about-card-meta">
                <span class="apocunoso-order-badge">05 · FUENTES ACADÉMICAS</span>
                <span class="apocunoso-about-eyebrow">REFERENCIAS BIBLIOGRÁFICAS (APA 7.ª EDICIÓN)</span>
            </div>
            <h3 class="apocunoso-about-question">Sustento Histórico y Politológico</h3>
            <div class="apocunoso-refs-grid">{refs_items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

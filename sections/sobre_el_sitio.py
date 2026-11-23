"""Sección 'Sobre el sitio': Identidad, Manual Breve y Leyenda Oficial de Etiquetas (apocunoso-style)."""

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


MANUAL_MODULOS = [
    {
        "orden": "MÓDULO 01",
        "eyebrow": "PORTADA Y TELEMETRÍA EN VIVO",
        "color_class": "about-card-blue",
        "titulo": "Inicio y Radar Automatizado de Coyuntura",
        "contenido_html": (
            "<p>La vista <strong>Inicio</strong> concentra el pulso diario de la plataforma en tres bloques:</p>"
            "<ul>"
            "<li><strong>KPIs y Boletín Matutino:</strong> Contadores automáticos de noticias, normas monitoreadas, "
            "fuentes auditadas y el acceso directo matutino a <em>El Peruano</em>.</li>"
            "<li><strong>Carruseles Temáticos:</strong> Noticias clasificadas en <em>Gestión Pública</em>, "
            "<em>Políticas Públicas</em> y <em>Política y Gobernabilidad</em>.</li>"
            "<li><strong>Selector de Apariencia:</strong> Desde la barra lateral puedes alternar al instante entre "
            "<strong>Auto</strong>, <strong>Oscuro</strong> y <strong>Claro</strong>.</li>"
            "</ul>"
        ),
    },
    {
        "orden": "MÓDULO 02",
        "eyebrow": "VIGILANCIA REGULATORIA · EL PERUANO",
        "color_class": "about-card-green",
        "titulo": "Rastrea la Norma (Trazabilidad y Verificación IA)",
        "contenido_html": (
            "<p>Sigue el ciclo completo de las normas legales publicadas diariamente en el diario oficial:</p>"
            "<ul>"
            "<li><strong>Diagrama de Flujo:</strong> Muestra en 5 pasos la recolección respetuosa, filtros "
            "determinísticos, hash <code>SHA-256</code> y verificación de citas por IA.</li>"
            "<li><strong>Filtros Combinados:</strong> Filtra por fecha de edición, subtema, entidad emisora o "
            "<strong>Política Nacional (CEPLAN)</strong>.</li>"
            "<li><strong>Fichas Analíticas y Permalink:</strong> Pulsa <code>Analizar ficha →</code> para abrir "
            "qué dispone, repercusiones y citas normativas verificadas.</li>"
            "</ul>"
        ),
    },
    {
        "orden": "MÓDULO 03",
        "eyebrow": "BASES DE DATOS Y FICHAS METODOLÓGICAS",
        "color_class": "about-card-gold",
        "titulo": "Políticas y Datos y Fichas Técnicas de Fuentes",
        "contenido_html": (
            "<p>Organiza las fuentes primarias del Estado, think tanks, Políticas Nacionales CEPLAN y evaluaciones:</p>"
            "<ul>"
            "<li><strong>Doble acción en tarjetas:</strong> El botón <code>Abrir recurso ↗</code> te lleva al "
            "portal oficial, mientras que <code>📄 Ficha técnica →</code> abre su documentación metodológica dentro de Apocuna.</li>"
            "<li><strong>Qué trae cada Ficha Técnica:</strong> Variables y formatos (<code>.dta</code>, <code>.sav</code>, "
            "<code>.csv</code>), unidad de análisis, llaves de cruce (<code>UBIGEO</code>, <code>CUI</code>, <code>COD_MOD</code>), "
            "precauciones estadísticas e investigaciones donde se ha utilizado.</li>"
            "</ul>"
        ),
    },
    {
        "orden": "MÓDULO 04",
        "eyebrow": "CLIMA, BIBLIOTECA Y FORMACIÓN",
        "color_class": "about-card-pink",
        "titulo": "Monitoreo El Niño, Biblioteca y Escuela y Becas",
        "contenido_html": (
            "<p>Tres espacios especializados para monitoreo climático, hemeroteca pública y formación:</p>"
            "<ul>"
            "<li><strong>Monitoreo El Niño:</strong> Visores satelitales/oceanográficos en vivo, radar RSS "
            "de declaratorias de emergencia, seguimiento presupuestal <code>PP 0068 PREVAED</code> y 16 herramientas con Ficha Técnica.</li>"
            "<li><strong>Biblioteca y Revistas:</strong> Ensayos propios, 12 revistas de gestión pública (Perú y Latinoamérica), "
            "papers recientes, alertas OpenAlex y memorias de congresos.</li>"
            "<li><strong>Escuela y Becas:</strong> Sistemas Administrativos (LOPE), cursos abiertos "
            "(MIT, ENAP, CEPAL, BID), guías metodológicas y becas.</li>"
            "</ul>"
        ),
    },
]


FAMILIAS_LEYENDA = [
    {
        "familia": "FAMILIA 01",
        "eyebrow": "ARRIBA A LA IZQUIERDA DE CADA TARJETA",
        "color_class": "about-card-blue",
        "titulo": "Tipo y Naturaleza del Recurso",
        "filas": [
            (
                '<span class="badge-tipo">PORTAL</span> <span class="badge-tipo">REPOSITORIO</span>',
                "Plataforma institucional oficial o archivo documental/bibliográfico en línea.",
            ),
            (
                '<span class="badge-tipo">MICRODATOS / SERIE</span> <span class="badge-tipo">API</span>',
                "Bases de datos descargables (ENAHO, ENDES, ESCALE, CEPALSTAT) o interfaz programática.",
            ),
            (
                '<span class="badge-tipo">NORMA LEGAL</span> <span class="badge-tipo">SISTEMA ADM.</span>',
                "Dispositivo oficial de <em>El Peruano</em> o síntesis normativa de los sistemas del Estado (LOPE).",
            ),
            (
                '<span class="badge-tipo">MOOC / AUTOGUIADO</span> <span class="badge-tipo">BECA</span>',
                "Modalidad de programa formativo o portal oficial de becas y movilidad académica.",
            ),
            (
                '<span class="badge-tipo">REVISTA</span> <span class="badge-tipo">CONGRESO</span> <span class="badge-tipo">MEMORIA CONGRESO</span>',
                "Publicación científica arbitrada, encuentro académico o actas y documentos de trabajo.",
            ),
            (
                '<span class="badge-tipo">PROGRAMA SOCIAL</span> <span class="badge-tipo">POLÍTICA PÚBLICA</span>',
                "Evaluación priorizada de intervención social (Juntos, Pensión 65, Cuna Más) o política sectorial/PpR.",
            ),
            (
                '<span class="badge-tipo">BASE DE DATOS</span> <span class="badge-tipo">PAPER 2026</span>',
                "Registro maestro CEPLAN/SINAPLAN o artículo reciente indexado en gestión y política pública.",
            ),
        ],
    },
    {
        "familia": "FAMILIA 02",
        "eyebrow": "ARRIBA A LA DERECHA DE CADA TARJETA",
        "color_class": "about-card-green",
        "titulo": "Frecuencia de Actualización y Condición",
        "filas": [
            (
                '<span class="badge-freq badge-freq-diaria">TIEMPO REAL</span> <span class="badge-freq badge-freq-diaria">DIARIA</span>',
                "Monitoreo satelital continuo o publicación oficial con actualización diaria.",
            ),
            (
                '<span class="badge-freq badge-freq-semanal">SEMANAL</span> <span class="badge-freq badge-freq-mensual">MENSUAL</span>',
                "Reportes epidemiológicos/opinión semanales o boletines y series de frecuencia mensual.",
            ),
            (
                '<span class="badge-freq badge-freq-anual">ANUAL</span> <span class="badge-freq badge-freq-permanente">PERMANENTE</span>',
                "Censos o eventos anuales/bienales (ocre) y archivos o guías estables (piedra).",
            ),
            (
                '<span class="badge-continua">GRATUITO</span> <span class="badge-continua">GRATUITO (CERT. OPCIONAL)</span>',
                "Acceso abierto sin costo; algunos MOOC cobran únicamente por emitir certificado.",
            ),
            (
                '<span class="badge-continua">🟢 RECEPCIÓN CONTINUA</span> <span class="badge-deadline">⏳ PLAZO / CONSULTAR</span>',
                "Estado de postulación de revistas científicas, congresos o costo sujeto a verificación.",
            ),
        ],
    },
    {
        "familia": "FAMILIA 03",
        "eyebrow": "SEÑAL TEMÁTICA (NORMAS Y MONITOREO FEN)",
        "color_class": "about-card-gold",
        "titulo": "Ejes Analíticos y Dominios Técnicos",
        "filas": [
            (
                '<span class="badge-portal badge-domain-blue">EJE: POLITY</span>',
                "Normas sobre arquitectura del Estado, sistemas administrativos, competencia y reforma institucional.",
            ),
            (
                '<span class="badge-portal badge-domain-green">EJE: POLICY</span>',
                "Normas sobre políticas públicas sectoriales (salud, educación, ambiente, economía, transferencias).",
            ),
            (
                '<span class="badge-portal badge-domain-pink">EJE: MIXTO</span>',
                "Dispositivos que articulan cambios institucionales y decisiones regulatorias sectoriales.",
            ),
            (
                '<span class="badge-portal badge-domain-blue">OCEANOGRÁFICO / HÍDRICO</span>',
                "Plataformas del mar peruano, ENSO, cuencas hidrográficas y reservorios (ENFEN, NOAA, ANA, SUNASS).",
            ),
            (
                '<span class="badge-portal badge-domain-green">GEOESPACIAL</span> <span class="badge-portal badge-domain-gold">PRESUPUESTAL</span> <span class="badge-portal badge-domain-pink">METEOROLÓGICO</span>',
                "Dominios técnicos del FEN: cartografía de riesgo (SIGRID), gasto (MEF PP 0068) y clima (SENAMHI).",
            ),
            (
                '<span class="badge-freq badge-domain-blue">IMPACTO • AÑO</span> <span class="badge-freq badge-domain-green">SEGUIMIENTO • AÑO</span> <span class="badge-freq badge-domain-gold">EDEP • AÑO</span> <span class="badge-freq badge-domain-pink">IMPLEMENTACIÓN • AÑO</span>',
                "Tipo y año de evaluación pública: impacto causal, seguimiento SINAPLAN, diseño presupuestal (EDEP) o implementación.",
            ),
            (
                '<span class="badge-freq badge-domain-blue">INVERSIÓN PÚBLICA</span> <span class="badge-freq badge-domain-blue">SERVICIO CIVIL</span> <span class="badge-freq badge-domain-blue">CAPACIDAD ESTATAL</span>',
                "Ámbito temático de papers y ensayos en gestión, administración y política pública.",
            ),
        ],
    },
    {
        "familia": "FAMILIA 04",
        "eyebrow": "TRAZABILIDAD, VERIFICACIÓN Y ACCIÓN INTERNA",
        "color_class": "about-card-pink",
        "titulo": "Estado Editorial, Auditoría y Fichas Técnicas",
        "filas": [
            (
                '<span class="norma-estado-pill" style="background:#1B8668;color:#FAF7E9;">REVISADO</span>',
                "Ficha de norma curada o reemplazada manualmente en <code>data/normas_comentadas/</code>.",
            ),
            (
                '<span class="norma-estado-pill" style="background:#B45309;color:#FAF7E9;">BORRADOR IA</span>',
                "Síntesis automática por IA con citas validadas contra el texto oficial (requiere verificación humana).",
            ),
            (
                '<span class="norma-estado-pill" style="background:#2775AA;color:#FAF7E9;">RADAR SIN IA</span>',
                "Norma indexada en modo determinístico mediante reglas y hash <code>SHA-256</code>.",
            ),
            (
                '<span class="badge-continua">✓ AUDITADA / VERIFICADO</span>',
                "Enlace oficial comprobado mediante script automatizado de disponibilidad HTTP.",
            ),
            (
                '<span class="btn-ficha-tecnica">📄 FICHA TÉCNICA →</span>',
                "Botón interno que abre la documentación metodológica completa (variables, alcance, cruces e investigaciones).",
            ),
        ],
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


def _render_tab_identidad() -> None:
    """Pestaña 1: Propósito, historia institucional, marco analítico y fuentes APA."""
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
        <div class="apocunoso-about-grid-2col" style="margin-bottom: 1.25rem;">
            <article class="apocunoso-about-card about-card-blue">
                <div class="apocunoso-about-card-topbar"></div>
                <div class="apocunoso-about-card-inner">
                    <div class="apocunoso-about-card-meta">
                        <span class="apocunoso-order-badge">🎯 MISIÓN</span>
                        <span class="apocunoso-about-eyebrow">PROPÓSITO OPERATIVO</span>
                    </div>
                    <h3 class="apocunoso-about-question">Misión</h3>
                    <div class="apocunoso-about-body">
                        <p>Democratizar el acceso a datos públicos auditados, trazabilidad normativa diaria y herramientas de análisis politológico en el Perú, transformando información estatal dispersa en evidencia verificable para fortalecer la investigación aplicada y la toma de decisiones públicas.</p>
                    </div>
                </div>
            </article>
            <article class="apocunoso-about-card about-card-green">
                <div class="apocunoso-about-card-topbar"></div>
                <div class="apocunoso-about-card-inner">
                    <div class="apocunoso-about-card-meta">
                        <span class="apocunoso-order-badge">🔭 VISIÓN</span>
                        <span class="apocunoso-about-eyebrow">HORIZONTE INSTITUCIONAL</span>
                    </div>
                    <h3 class="apocunoso-about-question">Visión</h3>
                    <div class="apocunoso-about-body">
                        <p>Consolidarse como el observatorio digital de referencia en ciencia política, gestión pública y políticas basadas en evidencia en el Perú y la región andina, articulando rigor metodológico, transparencia institucional y participación académica y ciudadana.</p>
                    </div>
                </div>
            </article>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        <div class="apocunoso-about-grid-2col" style="margin-top: 1.25rem;">
            <article class="apocunoso-about-card about-card-gold">
                <div class="apocunoso-about-card-topbar"></div>
                <div class="apocunoso-about-card-inner">
                    <div class="apocunoso-about-card-meta">
                        <span class="apocunoso-order-badge">06 · EQUIPO</span>
                        <span class="apocunoso-about-eyebrow">INTEGRACIÓN DE APOCUNA HUB</span>
                    </div>
                    <h3 class="apocunoso-about-question">Equipo de Apocuna</h3>
                    <div class="apocunoso-about-body">
                        <ul>
                            <li><strong>José Gastón Silva Ipanaque</strong></li>
                            <li><strong>Gabriel Stefano Ancajima Raymundo</strong></li>
                            <li><strong>Mario Alfonso Lanao De La Torre</strong></li>
                        </ul>
                    </div>
                </div>
            </article>
            <article class="apocunoso-about-card about-card-blue">
                <div class="apocunoso-about-card-topbar"></div>
                <div class="apocunoso-about-card-inner">
                    <div class="apocunoso-about-card-meta">
                        <span class="apocunoso-order-badge">07 · CONTACTO</span>
                        <span class="apocunoso-about-eyebrow">CANALES DIRECTOS DE COORDINACIÓN</span>
                    </div>
                    <h3 class="apocunoso-about-question">Contacto Oficial</h3>
                    <div class="apocunoso-about-body">
                        <p><strong>José Gastón Silva Ipanaque</strong></p>
                        <ul>
                            <li><strong>Teléfono:</strong> <a href="tel:+51922739533">+51 922 739 533</a></li>
                            <li><strong>Correo:</strong> <a href="mailto:gsilva7516@gmail.com">gsilva7516@gmail.com</a></li>
                            <li><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/jsilv" target="_blank" rel="noopener noreferrer">linkedin.com/in/jsilv ↗</a></li>
                        </ul>
                    </div>
                </div>
            </article>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_tab_manual() -> None:
    """Pestaña 2: Manual breve de uso del sitio en tarjetas de 2 columnas."""
    st.markdown(
        """
        <div class="apocunoso-about-intro">
            <div class="apocunoso-about-intro-head">
                <span class="apocunoso-order-badge">00 · GUÍA RÁPIDA DE NAVEGACIÓN</span>
                <span class="apocunoso-about-tag">MANUAL OPERATIVO DEL OBSERVATORIO</span>
            </div>
            <h2 class="apocunoso-about-intro-title">¿Cómo utilizar Apocuna Hub paso a paso?</h2>
            <p class="apocunoso-about-intro-text">
                La plataforma separa los recursos en módulos temáticos desde la barra lateral izquierda. Todas las fichas
                normativas (<code>?vista=normas_comentadas&amp;norma=...</code>) y las Fichas Técnicas Metodológicas de bases de datos
                (<code>?vista=polity&amp;ficha=...</code>) cuentan con <strong>enlace directo compartible (permalink)</strong> y botones de retorno sin perder contexto.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    manual_cards = []
    for item in MANUAL_MODULOS:
        manual_cards.append(
            f'<article class="apocunoso-about-card {item["color_class"]}">'
            f'<div class="apocunoso-about-card-topbar"></div>'
            f'<div class="apocunoso-about-card-inner">'
            f'<div class="apocunoso-about-card-meta">'
            f'<span class="apocunoso-order-badge">{item["orden"]}</span>'
            f'<span class="apocunoso-about-eyebrow">{item["eyebrow"]}</span>'
            f'</div>'
            f'<h3 class="apocunoso-about-question">{item["titulo"]}</h3>'
            f'<div class="apocunoso-about-body">{item["contenido_html"]}</div>'
            f'</div>'
            f'</article>'
        )

    st.markdown(
        f'<div class="apocunoso-about-grid-2col">{"".join(manual_cards)}</div>',
        unsafe_allow_html=True,
    )


def _render_tab_leyenda() -> None:
    """Pestaña 3: Leyenda oficial unificada con chips reales en vivo."""
    st.markdown(
        """
        <div class="apocunoso-about-intro">
            <div class="apocunoso-about-intro-head">
                <span class="apocunoso-order-badge">00 · GRAMÁTICA VISUAL DE TARJETAS</span>
                <span class="apocunoso-about-tag">SISTEMA UNIFICADO DE 4 FAMILIAS (APOCUNOSO-STYLE)</span>
            </div>
            <h2 class="apocunoso-about-intro-title">¿Cómo leer las etiquetas de cualquier tarjeta?</h2>
            <p class="apocunoso-about-intro-text">
                Cada tarjeta del sitio sigue una regla espacial fija: <strong>arriba a la izquierda</strong> indica <em>qué tipo de recurso es</em>;
                <strong>arriba a la derecha</strong> muestra <em>su frecuencia de actualización o estado</em>; debajo aparece la <strong>institución productora</strong>;
                y al pie encontrarás los botones de acceso externo (<code>↗</code>) y análisis o ficha técnica interna (<code>→</code>).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    legend_cards = []
    for fam in FAMILIAS_LEYENDA:
        rows_html = "".join(
            f'<div class="legend-item-row">'
            f'<div class="legend-chip-col">{chips}</div>'
            f'<div class="legend-desc-col">{desc}</div>'
            f'</div>'
            for chips, desc in fam["filas"]
        )
        legend_cards.append(
            f'<article class="apocunoso-about-card {fam["color_class"]}">'
            f'<div class="apocunoso-about-card-topbar"></div>'
            f'<div class="apocunoso-about-card-inner">'
            f'<div class="apocunoso-about-card-meta">'
            f'<span class="apocunoso-order-badge">{fam["familia"]}</span>'
            f'<span class="apocunoso-about-eyebrow">{fam["eyebrow"]}</span>'
            f'</div>'
            f'<h3 class="apocunoso-about-question">{fam["titulo"]}</h3>'
            f'<div class="legend-list">{rows_html}</div>'
            f'</div>'
            f'</article>'
        )

    st.markdown(
        f'<div class="apocunoso-about-grid-2col">{"".join(legend_cards)}</div>',
        unsafe_allow_html=True,
    )


def render_sobre_el_sitio() -> None:
    """Renderiza la sección 'Sobre el sitio' en 3 pestañas: Identidad, Manual Breve y Leyenda."""
    st.title("🏛️ Sobre Apocuna: Identidad, Manual y Leyenda")

    tab_id, tab_manual, tab_leyenda = st.tabs([
        "🏛️ Identidad y Propósito",
        "🧭 Manual Breve del Sitio",
        "🏷️ Leyenda de Etiquetas",
    ])

    with tab_id:
        _render_tab_identidad()
    with tab_manual:
        _render_tab_manual()
    with tab_leyenda:
        _render_tab_leyenda()

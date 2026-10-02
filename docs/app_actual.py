import streamlit as st
import feedparser
import pandas as pd
import plotly.express as px

# 1. Configuración básica de la página
st.set_page_config(page_title="Dashboard de Gobernanza", layout="wide", initial_sidebar_state="expanded")

# 2. Estado de Sesión para el Tema (Toggle)
# Guardamos la preferencia en la memoria de la sesión. Por defecto inicia en Oscuro.
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = True

st.sidebar.markdown("### ⚙️ Apariencia")
modo_oscuro = st.sidebar.toggle("🌙 Modo Oscuro / Claro", value=st.session_state.tema_oscuro)
st.session_state.tema_oscuro = modo_oscuro
st.sidebar.markdown("---")

# 3. Variables de Color Dinámicas
if st.session_state.tema_oscuro:
    css_variables = """
    :root {
        --bg-main: #0B0F19;
        --bg-sec: #161B22;
        --text-main: #E6EDF3;
        --text-muted: #8B949E;
        --border-color: #30363D;
        --accent-cyan: #00F2FE;
        --accent-pink: #FF6584;
        --accent-purple: #8A2BE2;
        --card-shadow: 0 4px 15px rgba(0, 242, 254, 0.1);
    }
    """
    img_url = "https://placehold.co/400x150/0B0F19/FFFFFF?text=Gobernanza+TOPP"
else:
    css_variables = """
    :root {
        --bg-main: #F8F9FA;
        --bg-sec: #FFFFFF;
        --text-main: #1F2328;
        --text-muted: #656D76;
        --border-color: #D0D7DE;
        --accent-cyan: #007ACC;
        --accent-pink: #D83B64;
        --accent-purple: #6F42C1;
        --card-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    """
    img_url = "https://placehold.co/400x150/F8FAFC/1E293B?text=Apocuna+Hub"

# 4. Inyección del CSS estructurado
custom_css = f"""
<style>
{css_variables}

/* Forzar fondo general de Streamlit */
.stApp {{
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
}}

/* Forzar color de texto en los componentes nativos de Streamlit */
h1, h2, h3, p, div, span, label, li {{
    color: var(--text-main) !important;
}}

/* Contenedor de Scroll Horizontal */
.horizontal-scroll-wrapper {{
    display: flex;
    overflow-x: auto;
    gap: 20px;
    padding-bottom: 15px;
    scrollbar-width: thin;
    scrollbar-color: var(--accent-cyan) var(--border-color);
}}
.horizontal-scroll-wrapper::-webkit-scrollbar {{ height: 8px; }}
.horizontal-scroll-wrapper::-webkit-scrollbar-track {{ background: var(--bg-main); border-radius: 10px; }}
.horizontal-scroll-wrapper::-webkit-scrollbar-thumb {{ background: var(--accent-cyan); border-radius: 10px; }}

/* Tarjetas estilo Snowflake / Neón */
.neon-card {{
    background-color: var(--bg-sec);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 24px;
    box-shadow: var(--card-shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
    margin-bottom: 1rem;
    min-width: 320px;
    max-width: 320px;
    flex-shrink: 0;
}}
.neon-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 20px var(--card-shadow);
}}

/* Bordes de acento para las tarjetas */
.neon-card.cyan {{ border-left: 4px solid var(--accent-cyan); }}
.neon-card.pink {{ border-left: 4px solid var(--accent-pink); border-top: none; }}
.neon-card.purple {{ border-left: 4px solid var(--accent-purple); border-top: none; }}

/* Tipografía de las tarjetas */
.card-source {{
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}}
.card-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-main) !important;
    margin-bottom: 12px;
    line-height: 1.4;
}}
.card-date {{ font-size: 0.85rem; color: var(--accent-cyan); margin-bottom: 10px; font-weight: 600;}}
.neon-card p {{ color: var(--text-main) !important; }}
.neon-card a {{
    color: var(--accent-cyan) !important;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    display: inline-block;
    margin-top: 10px;
}}
.neon-card a:hover {{ text-decoration: underline; color: var(--accent-pink) !important; }}

/* Tarjetas Horizontales (Sección Notas) */
.horizontal-note-card {{
    display: flex;
    background-color: var(--bg-sec);
    border-radius: 12px;
    border-left: 5px solid var(--accent-pink);
    border-top: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: var(--card-shadow);
    transition: transform 0.2s;
}}
.horizontal-note-card:hover {{
    transform: scale(1.01);
    box-shadow: 0 10px 15px var(--card-shadow);
}}
.note-img {{
    width: 300px;
    min-width: 300px;
    object-fit: cover;
    background-color: var(--border-color);
}}
.note-content {{
    padding: 25px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.note-title {{ font-size: 1.5rem; font-weight: 700; color: var(--text-main) !important; margin-bottom: 10px; margin-top: 0; }}
.note-excerpt {{ font-size: 1rem; color: var(--text-main) !important; margin-bottom: 15px; line-height: 1.5; }}
.note-meta {{ font-size: 0.85rem; color: var(--text-muted) !important; font-weight: 600; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.sidebar.image(img_url, use_container_width=True)
st.sidebar.title("Navegación")
menu = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "1. Inicio (Radar y Fuentes)", 
        "2. Polity and Policy", 
        "3. Estudiantes (DEMO)", 
        "4. Notas e Investigación", 
        "5. Eventos y Congresos"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Plataforma de vigilancia endógena y auditoría de datos en el Perú. Actualización automatizada.")

if menu == "1. Inicio (Radar y Fuentes)":
    st.title("🌐 Inicio: Radar de Coyuntura y Fuentes")
    
    st.header("Últimas Noticias y Normas Legales")
    st.markdown("Noticias relevantes de gestión, políticas públicas y normas de El Peruano.")
    
    # Simulación de extracción RSS (Usamos un feed genérico/oficial o mocks si falla la conexión)
    try:
        feed = feedparser.parse("https://www.cepal.org/es/rss.xml")
        entradas = feed.entries[:5]
    except:
        entradas = []

    # Construimos el HTML para el scroll horizontal estilo Snowflake
    cards_html = '<div class="horizontal-scroll-wrapper">'
    
    # Añadimos tarjetas simuladas de El Peruano (Normas)
    cards_html += f"""
        <div class="neon-card pink">
            <div class="card-source">EL PERUANO - NORMAS LEGALES</div>
            <div class="card-date">HOY</div>
            <div class="card-title">Decreto Supremo que aprueba la Política Nacional de Modernización de la Gestión Pública al 2030</div>
            <a href="#">Leer norma completa →</a>
        </div>
        <div class="neon-card pink">
            <div class="card-source">EL PERUANO - NORMAS LEGALES</div>
            <div class="card-date">AYER</div>
            <div class="card-title">Resolución Ministerial sobre lineamientos de gobernanza territorial y presupuesto por resultados</div>
            <a href="#">Leer norma completa →</a>
        </div>
    """
    
    # Añadimos las noticias reales del RSS
    for entry in entradas:
        cards_html += f"""
        <div class="neon-card">
            <div class="card-source">CEPAL / GESTIÓN</div>
            <div class="card-date">{entry.published[:16] if 'published' in entry else 'Reciente'}</div>
            <div class="card-title">{entry.title}</div>
            <a href="{entry.link}" target="_blank">Leer artículo →</a>
        </div>
        """
    cards_html += '</div>'
    
    st.markdown(cards_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("Directorio de Fuentes de Datos (Vigilancia y Auditoría)")
    st.markdown("Relación estructurada de URLs, endpoints de APIs y repositorios institucionales.")
    
    # Mostrando las fuentes en un formato estructurado con expanders
    with st.expander("📊 1. Plataformas de Datos Abiertos y Microdatos (APIs y Catálogos)", expanded=True):
        st.markdown("""
        * **Plataforma Nacional de Datos Abiertos (PCM):**
          * Portal general: [Plataforma Nacional de Datos Abiertos](https://www.datosabiertos.gob.pe)
          * Endpoint API CKAN: [Búsqueda y ordenamiento](https://www.datosabiertos.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=10)
        * **Ministerio de Salud (MINSA) / CDC Perú:**
          * Endpoint API CKAN: [MINSA API](https://datos.minsa.gob.pe/api/3/action/package_search?sort=metadata_modified+desc&rows=5)
          * Portal CDC Perú: [Centro Nacional de Epidemiología](https://www.google.com/search?q=https://www.dge.gob.pe/portal/)
        * **INEI (Instituto Nacional de Estadística e Informática):**
          * Consulta y Descarga de Microdatos (ENAHO, ENDES): [Portal SIGA INEI](https://systems.inei.gob.pe/SigaINei/)
          * Repositorio de Informes: [INEI Informes](https://www.gob.pe/institucion/inei/informes-publicaciones)
        * **MINEDU (Ministerio de Educación):**
          * Estadística de la Calidad Educativa: [ESCALE MINEDU](https://escale.minedu.gob.pe/)
          * Censo Escolar: [Repositorio ESCALE](https://escale.minedu.gob.pe/censo-escolar)
        """)

    with st.expander("⚖️ 2. Control Gubernamental y Conflictividad Social", expanded=False):
        st.markdown("""
        * **Defensoría del Pueblo:**
          * Repositorio de reportes: [Reportes](https://www.defensoria.gob.pe/categorias_de_documentos/reportes/)
          * Prevención de Conflictos Sociales: [Unidad de Prevención](https://www.defensoria.gob.pe/areas_tematicas/prevencion-de-conflictos/)
        * **Contraloría General de la República:**
          * Alertas de control: [Noticias y Alertas](https://www.gob.pe/institucion/contraloria/noticias)
        """)

    with st.expander("🧠 3. Think Tanks y Repositorios Académicos Nacionales", expanded=False):
        st.markdown("""
        * **CIES:** [Investigaciones y propuestas](https://cies.org.pe/investigaciones/)
        * **IEP:** [Encuestas de Opinión](https://iep.org.pe/publicaciones/encuestas/) | [Repositorio](https://repositorio.iep.org.pe)
        * **GRADE:** [Documentos de Política](https://grade.org.pe/publicaciones_categorias/documento-de-politica/) | [Área de Educación](https://grade.org.pe/publicaciones/areas/educacion-y-aprendizajes/)
        * **IPE:** [Publicaciones](https://www.ipe.org.pe/portal/publicaciones/) | [INCORE Perú](https://incoreperu.pe)
        * **Videnza:** [Gestión Pública](https://videnzainstituto.org/publicaciones/)
        """)

    with st.expander("🌍 4. Organismos Multilaterales y Cooperación", expanded=False):
        st.markdown("""
        * **CEPAL:** [CEPALSTAT API](https://api-cepalstat.cepal.org)
        * **UNICEF Perú:** [Informes de infancia](https://www.unicef.org/peru/informes)
        * **PNUD Perú:** [Diagnósticos de desarrollo](https://undp.org/es/peru/publicaciones)
        * **OIT Andina:** [ILOSTAT Data](https://ilostat.ilo.org/data/)
        * **Banco Mundial:** [Open Knowledge Repository](https://openknowledge.worldbank.org/)
        """)

    with st.expander("📑 5. Informes Específicos Extraídos en Auditorías (2026)", expanded=False):
        st.markdown("""
        * **INEI – TIC (II Trimestre 2026):** [El 64,5% con Internet](https://www.gob.pe/institucion/inei/noticias/1450362)
        * **INEI – Socioeconómica:** [ENAHO Niñez y Adolescencia 2025](https://www.gob.pe/institucion/inei/informes-publicaciones/8655583)
        * **INEI/UNICEF – Niñez Indígena:** [Documento Oficial](https://www.unicef.org/peru/informes/ninez-y-adolescencia-indigena-y-afroperuana)
        * **PNUD:** [Integridad Elecciones 2026](https://www.undp.org/es/peru/publicaciones/integridad-de-la-informacion-en-las-elecciones-generales-2026)
        * **Contraloría:** [Hito de Control Pto. San Juan de Marcona](https://www.gob.pe/institucion/contraloria/noticias/1449744)
        """)

elif menu == "2. Polity and Policy":
    st.title("🏛️ Polity and Policy")
    st.markdown("Insumos y mecanismos de actualización indispensables para la formulación, ejecución y evaluación de políticas públicas.")
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
        ### 1. Actualización Normativa (Diaria)
        Los cambios en el marco legal modifican las reglas del juego para cualquier política sectorial o intervención subnacional.
        * **Boletines de Normas Legales (El Peruano/SPIJ):** Monitoreo diario de decretos supremos, resoluciones ministeriales y ordenanzas clave.
        * **Alertas SGP (PCM) y CEPLAN:** Nuevos lineamientos de modernización del Estado y metodologías de presupuesto.
        * **Monitoreo del Congreso:** Seguimiento de proyectos de ley en comisiones (dictámenes y prepublicaciones).
        
        ### 3. Coyuntura y Clima Político (Semanal)
        Para entender las ventanas de oportunidad política (policy windows) y las restricciones.
        * **Estudios de Opinión (IEP, Ipsos):** Pulso sobre aprobación de autoridades y confianza institucional.
        * **Think Tanks (CIES, GRADE):** Lectura de policy briefs que traducen problemas complejos en recomendaciones prácticas.
        * **Revistas especializadas:** Boletines académicos en ciencia política y administración pública.
        """)
    with colB:
        st.markdown("""
        ### 2. Datos Estadísticos y Microdatos (Mensual)
        La base del diseño de políticas basadas en evidencia.
        * **Actualizaciones INEI:** Alertas de indicadores coyunturales y microdatos (ENAHO, ENDES).
        * **Plataforma Datos Abiertos y GIS:** Seguimiento de nuevos datasets para cruzar variables territoriales.
        * **Transparencia Económica (MEF):** Revisión semanal de ejecución del gasto (avance devengado, canon, PIM).
        
        ### 4. Gestión del Conocimiento (Permanente)
        * **Repositorios de Buenas Prácticas:** Monitoreo de iniciativas ganadoras (Ciudadanos al Día - CAD).
        * **Metodologías de Evaluación:** Guías sobre evaluaciones de impacto (experimental/cuasiexperimental) alineadas al SINAPLAN.
        """)

elif menu == "3. Estudiantes (DEMO)":
    st.title("🎓 Área de Estudiantes (Próximamente)")
    st.markdown("Para estudiantes de **Ciencia Política, Gobierno y Gestión Pública**, el foco pasa a la formación analítica, metodológica y la construcción de un archivo de conocimiento sólido.")
    
    st.markdown("### 1. Actualización Académica y Estado del Arte (Semanal)")
    st.markdown("""
    * **Alertas Automatizadas:** Configurar alertas en Google Scholar, Scopus o Cybertesis (ej. *gobernanza subnacional*).
    * **Blogs Académicos y Revistas:** Lectura de papers (como *Politai*) para ver discusiones actuales.
    * **Boletines de Centros de Pensamiento:** Seguir policy briefs de CIES, IEP, GRADE.
    """)
    
    st.markdown("### 2. Herramientas Metodológicas y Analíticas (Práctica Constante)")
    st.markdown("""
    * **Tutoriales y Repositorios:** Práctica semanal en Python o R (manipulación de datos INEI o JNE).
    * **Guías Metodológicas Internacionales:** Manuales de BID, CEPAL sobre evaluaciones de impacto o marcos lógicos.
    * **Gestores de Referencias:** Uso diario de Zotero/Mendeley.
    """)
    
    st.markdown("### 3. Focos de Coyuntura y Debate Político (Diario/Semanal)")
    st.markdown("""
    * **Pilas de Opinión:** Identificar enfoques de economía política y diseño institucional en noticias.
    * **Observatorios Electorales (JNE, ONPE):** Revisión de hojas de vida y financiamiento para trabajos prácticos.
    """)
    
    st.markdown("### 4. Espacios de Formación y Redes (Mensual)")
    st.markdown("""
    * **Coloquios y Congresos:** Convocatorias de ponencias y talleres (ej. Macrocoloquio de Estudiantes).
    """)
    
    st.markdown("---")
    st.header("📚 Apuntes de Clases y Guías (Sistemas Administrativos)")
    st.info("Simulación de repositorio de apuntes universitarios compartidos.")
    with st.expander("Sistema Nacional de Presupuesto Público (Apuntes Semana 4)"):
        st.write("**Concepto clave:** El presupuesto por resultados (PpR) no es solo asignar dinero, es condicionar la asignación a bienes y servicios que generen cambios comprobables en el ciudadano.")
        st.write("**Normativa base:** Decreto Legislativo N° 1440.")
    with st.expander("Modernización de la Gestión Pública (Apuntes Semana 6)"):
        st.write("Pilares de la Política Nacional: 1. Políticas Públicas, Planes y Diseño Institucional. 2. Presupuesto por Resultados. 3. Gestión por Procesos. 4. Servicio Civil Meritocrático. 5. Sistemas de Información, Seguimiento y Evaluación.")

elif menu == "4. Notas e Investigación":
    st.title("📝 Notas, Opinión y Ensayos")
    st.markdown("Investigaciones, reflexiones y ensayos sobre políticas públicas y gobernanza en el Perú.")
    
    # Texto completo en formato Markdown proporcionado por el usuario
    g_escolar_md = """
**Eje Temático:** 1. Gestión pública y gobernanza **Subeje:** 1.1. Políticas públicas

**1. Introducción**   
¿Qué está haciendo el Estado para formar a sus ciudadanos? El sistema educativo peruano enfrenta en la actualidad uno de los retos más complejos en lo que respecta a la formación ciudadana y la construcción de valores democráticos desde las bases escolares...
*(El sistema educativo no está formando ciudadanos críticos, sino que está entrenando "burócratas escolares", donde los estudiantes aprenden que la participación política se reduce a la emisión de un voto y a la asistencia pasiva a reuniones protocolares dirigidas por adultos).*

**2. Objetivos**
**Objetivo General:** Evaluar la brecha de implementación entre el diseño institucional normativo de los mecanismos de participación escolar en el Perú y su funcionamiento empírico.
    
**3. Metodología**   
Para responder a la complejidad del problema público planteado y capturar las dimensiones tanto estructurales como subjetivas de la gobernanza escolar, la investigación adopta un diseño mixto (cuantitativo y cualitativo). En su vertiente cualitativa, el estudio aplicará la técnica del rastreo de procesos (process tracing). En su vertiente cuantitativa, el estudio se sustentará en la extracción de grandes volúmenes de microdatos longitudinales del Censo Educativo.

**4. Resultados esperados**   
Se proyecta validar empíricamente la hipótesis principal: la mera existencia y reconocimiento jurídico de los Municipios Escolares y los CCONNA no garantiza una participación estudiantil efectiva.

**5. Conclusiones preliminares**   
La investigación conduce a una profunda reflexión crítica sobre el estado de la gobernanza escolar en el Perú. Resulta imperativo reorientar de manera radical estas políticas públicas hacia un modelo de democracia deliberativa.
        La investigación conduce a una profunda reflexión crítica sobre el estado de la gobernanza escolar en el Perú. Resulta imperativo reorientar de manera radical estas políticas públicas hacia un modelo de democracia deliberativa.
    """

    nota_html = """
    <div class="horizontal-note-card">
        <img class="note-img" src="https://placehold.co/600x400/F8FAFC/E11D48?text=Gobernanza+Escolar" alt="Gobernanza">
        <div class="note-content">
            <div class="note-meta">ENSAYO DE INVESTIGACIÓN • GESTIÓN PÚBLICA</div>
            <h3 class="note-title">¿Ciudadanía democrática o burocracia escolar?</h3>
            <p class="note-excerpt">La brecha de implementación y fragmentación institucional de la participación estudiantil en el Perú. Un análisis desde el neoinstitucionalismo sociológico y los microdatos del censo educativo.</p>
        </div>
    </div>
    """
    st.markdown(nota_html, unsafe_allow_html=True)
    
    # El contenido completo se despliega al interactuar
    with st.expander("📖 Leer documento completo (G ESCOLAR.md)"):
        st.markdown(g_escolar_md)

elif menu == "5. Eventos y Congresos":
    st.title("📅 Calendario de Eventos y Publicaciones")
    st.markdown("Revistas académicas y congresos clave para la difusión de investigaciones en gestión y políticas.")
    
    st.subheader("Revistas Académicas (Convocatorias)")
    
    # Dividimos en 3 columnas para organizar las tarjetas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="neon-card purple">
            <div class="card-source">CONVOCATORIA ABIERTA PERMANENTE</div>
            <div class="card-title">Revista Peruana de Investigación Educativa (RPIE - SIEP)</div>
            <p style="font-size: 0.9rem; color: var(--text-main); margin-bottom: 15px;">Gobernanza escolar, gestión educativa, políticas educativas y participación.</p>
            <a href="https://siep.org.pe/rpie" target="_blank">Visitar sitio web ➔</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="neon-card purple" style="margin-top: 15px;">
            <div class="card-source">RECEPCIÓN CONTINUA</div>
            <div class="card-title">Archivos Analíticos de Políticas Educativas (EPAA/AAPE)</div>
            <p style="font-size: 0.9rem; color: var(--text-main); margin-bottom: 15px;">Políticas educativas, gobernanza del sistema escolar y reformas comparadas.</p>
            <a href="https://epaa.asu.edu" target="_blank">Visitar sitio web ➔</a>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="neon-card purple">
            <div class="card-source">RECEPCIÓN CONTINUA</div>
            <div class="card-title">Revista Estado y Políticas Públicas (FLACSO Argentina)</div>
            <p style="font-size: 0.9rem; color: var(--text-main); margin-bottom: 15px;">Gobernanza territorial, ordenamiento territorial, descentralización y gestión pública.</p>
            <a href="https://politicaspublicas.flacso.org.ar" target="_blank">Visitar sitio web ➔</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="neon-card purple" style="margin-top: 15px;">
            <div class="card-source">RECEPCIÓN CONTINUA</div>
            <div class="card-title">Revista Eletrônica de Administração (READ - UFRGS)</div>
            <p style="font-size: 0.9rem; color: var(--text-main); margin-bottom: 15px;">Administración pública comparada, gobernanza y gestión de organizaciones públicas.</p>
            <a href="https://seer.ufrgs.br/read" target="_blank">Visitar sitio web ➔</a>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="neon-card purple">
            <div class="card-source">RECEPCIÓN CONTINUA PERMANENTE</div>
            <div class="card-title">Revista del CLAD Reforma y Democracia</div>
            <p style="font-size: 0.9rem; color: var(--text-main); margin-bottom: 15px;">Formas emergentes de gobernanza, administración pública comparada y gestión.</p>
            <a href="https://clad.org/publicaciones/revista-clad" target="_blank">Visitar sitio web ➔</a>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("🏛️ Espacios y Congresos Recurrentes del Sector")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info("**Macrocoloquio de Estudiantes de Ciencia Política (Perú):** Principal espacio nacional de deliberación estudiantil con mesas dedicadas a Gestión Pública, Gobernanza y Políticas Públicas.")
        st.info("**Seminario Nacional de Investigación Educativa (SIEP - Perú):** Foro nacional bienal enfocado en la presentación y discusión de evidencia empírica sobre gobernanza, reformas y actores escolares.")
    with col_c2:
        st.info("**Congreso Internacional del CLAD:** Abre convocatorias para paneles y ponencias individuales regularmente entre marzo y mayo de cada año sobre innovación pública y gobiernos subnacionales.")
        st.info("**Congreso Latinoamericano de Ciencia Política (ALACIP):** Incluye áreas temáticas periódicas dedicadas a Gobiernos Locales, Descentralización y Políticas Públicas.")
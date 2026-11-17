import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import os
import urllib.parse
import feedparser
import pandas as pd
import requests
import streamlit as st

from components.cards import (
    render_fen_catalog_grid,
    render_fen_hero_grid,
    render_fen_impact_grid,
    render_fen_radar_list,
    render_kpi_ribbon,
)
from sections.fichas_tecnicas import render_ficha_tecnica_detalle
from utils.loaders import load_fen_catalogo, sanitize_slug_param

PREVIEWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fen_previews")


@st.cache_data(show_spinner=False)
def _load_preview_data_uri(filename: str, mtime: float) -> str:
    """Lee la captura real de pantalla desde assets/fen_previews/ y la devuelve como Data URI en caché."""
    filepath = os.path.join(PREVIEWS_DIR, filename)
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def get_preview_uri(filename: str) -> str:
    """Obtiene el Data URI de una captura local invalidando caché solo si el archivo cambia."""
    filepath = os.path.join(PREVIEWS_DIR, filename)
    if os.path.exists(filepath):
        return _load_preview_data_uri(filename, os.path.getmtime(filepath))
    return ""


# ==============================================================================
# BLOQUE 1: CONFIGURACIÓN DEL HERO GRID DE MONITOREO EN TIEMPO REAL (2x2 + 1)
# ==============================================================================
SVG_GOES19 = (
    '<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
    '<rect width="600" height="220" fill="#0B132B"/></svg>'
)

SVG_WINDY = (
    '<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
    '<rect width="600" height="220" fill="#0F172A"/></svg>'
)

SVG_ENFEN = (
    '<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
    '<rect width="600" height="220" fill="#1E3A8A"/></svg>'
)

SVG_SUNASS = (
    '<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
    '<rect width="600" height="220" fill="#064E3B"/></svg>'
)

SVG_SIGRID = (
    '<svg viewBox="0 0 1200 210" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">'
    '<rect width="1200" height="210" fill="#0F172A"/></svg>'
)


def _get_hero_cards() -> tuple[list[dict], dict]:
    """Construye las 5 tarjetas principales inyectando la captura real verificada de cada plataforma."""
    top_four = [
        {
            "entidad": "SENAMHI • PERÚ",
            "estado": "EN VIVO / CADA 10 MIN",
            "titulo": "SENAMHI — Imágenes Satelitales GOES-19 y Monitoreo Hidrometeorológico",
            "descripcion": (
                "Seguimiento satelital multiespectral en tiempo real de topes nubosos, sistemas convectivos "
                "profundos, precipitación estimada y avisos meteorológicos e hidrológicos en el Pacífico y territorio peruano."
            ),
            "preview_url": get_preview_uri("senamhi_goes19.png"),
            "theme_class": "fen-theme-sat",
            "svg_fallback": SVG_GOES19,
            "metricas": ["GOES-19 Banda 13 IR", "Tope Nuboso (°C)", "Precipitación 24h", "Activación de Quebradas"],
            "url": "https://www.senamhi.gob.pe/?p=satelites-goes19",
            "btn_label": "Abrir GOES-19 SENAMHI ↗",
            "enlaces_secundarios": [
                {"label": "Avisos Meteorológicos", "url": "https://www.senamhi.gob.pe/?p=avisos-meteorologicos"},
                {"label": "Monitoreo Hidrológico", "url": "https://www.senamhi.gob.pe/?p=monitoreo-hidrologico"},
            ],
        },
        {
            "entidad": "WINDY • ECMWF / GFS",
            "estado": "TIEMPO REAL / MULTICAPA",
            "titulo": "Windy.com — Foco Perú y Pacífico Oriental (Anomalías Térmicas y Lluvias)",
            "descripcion": (
                "Visualización interactiva de alta resolución para el monitoreo de vientos alisios del Pacífico Sur, "
                "temperatura superficial del mar (SST), acumulado de lluvias a 3-10 días y comparación de modelos ECMWF y GFS."
            ),
            "preview_url": get_preview_uri("windy_peru.png"),
            "theme_class": "fen-theme-windy",
            "svg_fallback": SVG_WINDY,
            "metricas": ["Modelo Europeo ECMWF", "Modelo GFS NOAA", "Anomalía SST / Olas", "Acumulado de Lluvias"],
            "url": "https://www.windy.com/-9.190/-75.015?temp,-9.190,-75.015,5",
            "btn_label": "Abrir Mapa Interactivo Windy ↗",
            "enlaces_secundarios": [],
        },
        {
            "entidad": "ENFEN • IMARPE • NOAA",
            "estado": "ALERTA OFICIAL / EN VIVO",
            "titulo": "ENFEN / IMARPE / NOAA — Estado del Sistema de Alerta y Regiones Niño 1+2 y 3.4",
            "descripcion": (
                "Panel oficial de la Comisión Multisectorial ENFEN e IMARPE junto con el diagnóstico de la NOAA. "
                "Mide el Índice Costero El Niño (ICEN), anomalías térmicas en Niño 1+2 (costa peruana) y Niño 3.4, y arribo de ondas Kelvin."
            ),
            "preview_url": get_preview_uri("enfen_imarpe.png"),
            "theme_class": "fen-theme-enfen",
            "svg_fallback": SVG_ENFEN,
            "metricas": ["Índice ICEN / ONI", "Región Niño 1+2", "Región Niño 3.4", "Ondas Kelvin Subsuperficiales"],
            "url": "https://enfen.imarpe.gob.pe/",
            "btn_label": "Portal Oficial ENFEN / IMARPE ↗",
            "enlaces_secundarios": [
                {"label": "NOAA ENSO Diagnostic", "url": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/"},
            ],
        },
        {
            "entidad": "SUNASS • CAMI YAKU",
            "estado": "MONITOREO HÍDRICO / EPS",
            "titulo": "SUNASS — Centro de Análisis y Monitoreo CAMI Yaku (EPS y Cuencas)",
            "descripcion": (
                "Plataforma geoespacial e hidroclimática de SUNASS para el seguimiento de cuencas aportantes, "
                "vulnerabilidad de infraestructura de agua potable y alcantarillado (EPS), turbidez por huaicos y estrés hídrico."
            ),
            "preview_url": get_preview_uri("sunass_camiyaku.png"),
            "theme_class": "fen-theme-sunass",
            "svg_fallback": SVG_SUNASS,
            "metricas": ["Cuencas Aportantes", "Riesgo en 50 EPS", "Turbidez y Caudales", "Continuidad del Servicio"],
            "url": "https://www.gob.pe/institucion/sunass/campa%C3%B1as/21633-cami-yaku",
            "btn_label": "Abrir CAMI Yaku SUNASS ↗",
            "enlaces_secundarios": [
                {"label": "Portal Institucional SUNASS", "url": "https://www.gob.pe/sunass"},
            ],
        },
    ]

    bottom_wide = {
        "entidad": "CENEPRED • INDECI • COEN • SINPAD",
        "estado": "PLATAFORMA GEOESPACIAL CENTRAL • EN VIVO",
        "titulo": "INDECI / CENEPRED — SIGRID v3 y Monitoreo Nacional de Peligros y Emergencias (SINPAD / COEN)",
        "descripcion": (
            "Infraestructura geoespacial oficial del SINAGERD para consultar escenarios de riesgo por lluvias intensas, "
            "inundaciones, movimientos en masa (huaicos y deslizamientos), elementos expuestos (población, centros de salud, "
            "colegios, vías) y reportes de emergencias activas a nivel distrital, provincial y departamental."
        ),
        "preview_url": get_preview_uri("cenepred_sigrid.png"),
        "theme_class": "fen-theme-sigrid",
        "svg_fallback": SVG_SIGRID,
        "metricas": [
            "Escenarios de Riesgo FEN",
            "Población y Viviendas Expuestas",
            "Quebradas y Fajas Marginales",
            "Emergencias SINPAD / COEN",
            "Cartografía Distrital",
        ],
        "url": "https://sigrid.cenepred.gob.pe/sigridv3/",
        "btn_label": "Abrir Visor Geoespacial SIGRID v3 ↗",
        "enlaces_secundarios": [
            {"label": "INDECI / Reportes COEN", "url": "https://www.gob.pe/indeci"},
            {"label": "Portal CENEPRED", "url": "https://www.gob.pe/cenepred"},
        ],
    }
    return top_four, bottom_wide


HERO_TOP_FOUR_CARDS, HERO_BOTTOM_WIDE_CARD = _get_hero_cards()

# ==============================================================================
# BLOQUE 2: RADAR AUTOMATIZADO DE NOTICIAS Y NORMATIVA SOBRE EL NIÑO
# ==============================================================================
OFFICIAL_RSS_QUERIES = [
    (
        '("El Peruano" OR "Decreto Supremo" OR "Decreto de Urgencia" OR "estado de emergencia") '
        '("El Niño" OR "lluvias" OR "peligro inminente" OR "déficit hídrico" OR "INDECI") Perú',
        "NORMA / EMERGENCIA",
    ),
    (
        '("PCM" OR "ANIN" OR "MIDAGRI" OR "Autoridad Nacional del Agua" OR "MVCS") '
        '("Fenómeno El Niño" OR "prevención lluvias" OR "defensas ribereñas") Perú',
        "SECTOR OFICIAL",
    ),
]

PRESS_RSS_QUERIES = [
    ('"Fenómeno El Niño" Perú', "FENÓMENO EL NIÑO"),
    ('"ENFEN" Perú', "COMUNICADO ENFEN"),
    ('"SENAMHI lluvias" OR "SENAMHI El Niño" Perú', "SENAMHI / CLIMA"),
    ('"declaratoria de emergencia lluvias" OR "COEN INDECI" Perú', "COEN / EMERGENCIAS"),
]

OFFICIAL_KEYWORDS = (
    "el peruano",
    "decreto supremo",
    "decreto de urgencia",
    "resolución ministerial",
    "estado de emergencia",
    "declaratoria de emergencia",
    "pcm",
    "anin",
    "autoridad nacional de infraestructura",
    "autoridad nacional del agua",
    "midagri",
    "indeci",
    "cenepred",
    "gob.pe",
)

FALLBACK_OFFICIAL_ITEMS = [
    {
        "titulo": "Buscador Oficial de Normas Legales: Decretos Supremos de Declaratoria de Estado de Emergencia por Lluvias y Peligro Inminente",
        "fuente": "Diario Oficial El Peruano / PCM",
        "fecha_iso": "2026-11-04T12:00:00+00:00",
        "fecha_legible": "permanente / diario",
        "url": "https://busquedas.elperuano.pe/",
        "etiqueta": "DIARIO OFICIAL",
        "es_oficial": True,
    },
    {
        "titulo": "Comunicados Oficiales de la Comisión Multisectorial ENFEN sobre el Estado del Sistema de Alerta ante El Niño / La Niña",
        "fuente": "Comisión Multisectorial ENFEN / IMARPE",
        "fecha_iso": "2026-11-01T12:00:00+00:00",
        "fecha_legible": "actualización quincenal/mensual",
        "url": "https://enfen.imarpe.gob.pe/",
        "etiqueta": "COMUNICADO OFICIAL",
        "es_oficial": True,
    },
    {
        "titulo": "Intervenciones Estratégicas y Cartera de Proyectos de Drenaje Pluvial y Control de Inundaciones en Cuencas Priorizadas",
        "fuente": "Autoridad Nacional de Infraestructura (ANIN)",
        "fecha_iso": "2026-10-28T12:00:00+00:00",
        "fecha_legible": "portal institucional",
        "url": "https://www.gob.pe/anin",
        "etiqueta": "INFRAESTRUCTURA / ANIN",
        "es_oficial": True,
    },
]

FALLBACK_PRESS_ITEMS = [
    {
        "titulo": "Avisos Meteorológicos e Hidrológicos Vigentes por Precipitaciones, Incremento de Caudales y Activación de Quebradas",
        "fuente": "SENAMHI Perú",
        "fecha_iso": "2026-11-04T10:00:00+00:00",
        "fecha_legible": "monitoreo continuo",
        "url": "https://www.senamhi.gob.pe/?p=avisos-meteorologicos",
        "etiqueta": "ALERTA SENAMHI",
        "es_oficial": False,
    },
    {
        "titulo": "Boletines y Reportes de Emergencias del Centro de Operaciones de Emergencia Nacional (COEN - INDECI)",
        "fuente": "INDECI / COEN",
        "fecha_iso": "2026-11-03T15:00:00+00:00",
        "fecha_legible": "reporte diario",
        "url": "https://www.gob.pe/indeci",
        "etiqueta": "REPORTE COEN",
        "es_oficial": False,
    },
]


def _parse_entry_date(entry: dict) -> tuple[str, str]:
    """Convierte la fecha RSS en una tupla (ISO 8601 ordenable, fecha legible YYYY-MM-DD HH:MM)."""
    raw = entry.get("published") or entry.get("updated") or ""
    if raw:
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_utc = dt.astimezone(timezone.utc)
            return dt_utc.isoformat(), dt_utc.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pass
    now_utc = datetime.now(timezone.utc)
    return now_utc.isoformat(), now_utc.strftime("%Y-%m-%d")


def _extract_source_and_clean_title(entry: dict) -> tuple[str, str]:
    """Extrae el medio o institución de origen y limpia el sufijo del titular RSS."""
    raw_title = (entry.get("title") or "").strip()
    source_obj = entry.get("source")
    source_name = ""
    if isinstance(source_obj, dict):
        source_name = (source_obj.get("title") or "").strip()
    if " - " in raw_title:
        parts = raw_title.rsplit(" - ", 1)
        clean_title = parts[0].strip()
        if not source_name:
            source_name = parts[1].strip()
        return clean_title, (source_name or "Prensa / Portal Nacional")
    return raw_title, (source_name or "Prensa / Portal Nacional")


def _fetch_rss_query(query: str, etiqueta: str, es_oficial_default: bool) -> list[dict]:
    """Consulta un feed abierto de Google News RSS para Perú y devuelve ítems normalizados."""
    encoded = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=es-419&gl=PE&ceid=PE:es-419"
    try:
        resp = requests.get(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ApocunaFENRadar/2.0)"},
            timeout=6,
        )
        if resp.status_code != 200:
            return []
        parsed = feedparser.parse(resp.content)
    except Exception:
        return []

    results = []
    for entry in parsed.entries[:10]:
        link = (entry.get("link") or "").strip()
        if not link.startswith(("http://", "https://")):
            continue
        clean_title, source_name = _extract_source_and_clean_title(entry)
        if not clean_title:
            continue
        fecha_iso, fecha_legible = _parse_entry_date(entry)
        combined_lower = f"{clean_title} {source_name}".lower()
        is_off = es_oficial_default or any(k in combined_lower for k in OFFICIAL_KEYWORDS)
        results.append(
            {
                "titulo": clean_title,
                "fuente": source_name,
                "fecha_iso": fecha_iso,
                "fecha_legible": fecha_legible,
                "url": link,
                "etiqueta": etiqueta,
                "es_oficial": is_off,
            }
        )
    return results


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_fen_radar() -> dict:
    """
    Colector automatizado en vivo (TTL = 30 min) de normas legales, declaratorias de emergencia
    y noticias verificadas sobre el Fenómeno El Niño en el Perú.
    """
    official_map: dict[str, dict] = {}
    press_map: dict[str, dict] = {}

    for query, label in OFFICIAL_RSS_QUERIES:
        for item in _fetch_rss_query(query, label, es_oficial_default=True):
            key = item["titulo"].lower()[:90]
            if key not in official_map:
                official_map[key] = item

    for query, label in PRESS_RSS_QUERIES:
        for item in _fetch_rss_query(query, label, es_oficial_default=False):
            key = item["titulo"].lower()[:90]
            if item["es_oficial"] and key not in official_map:
                official_map[key] = item
            elif key not in press_map and key not in official_map:
                press_map[key] = item

    official_list = sorted(official_map.values(), key=lambda x: x["fecha_iso"], reverse=True)[:10]
    press_list = sorted(press_map.values(), key=lambda x: x["fecha_iso"], reverse=True)[:10]

    if not official_list:
        official_list = FALLBACK_OFFICIAL_ITEMS
    if not press_list:
        press_list = FALLBACK_PRESS_ITEMS

    sync_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "oficial": official_list,
        "prensa": press_list,
        "sync_utc": sync_ts,
    }


# ==============================================================================
# BLOQUE 3: IMPACTO Y CATÁLOGO MAESTRO DE HERRAMIENTAS (DESDE data/fen_catalogo.json)
# ==============================================================================
def _get_fen_catalog_lists() -> tuple[list[dict], list[dict]]:
    """Obtiene tarjetas de impacto y catálogo de herramientas FEN desde JSON cacheado."""
    cat = load_fen_catalogo()
    impact = cat.get("impact_cards", []) if isinstance(cat, dict) else []
    tools = cat.get("master_tools", []) if isinstance(cat, dict) else []
    return impact, tools


CATALOG_CATEGORIES = [
    "Todas",
    "Oceanográfico",
    "Meteorológico",
    "Geoespacial/Riesgos",
    "Hídrico/Saneamiento",
    "Presupuestal/Impacto",
]


def _filter_catalog_tools(tools: list[dict], search_query: str, selected_category: str) -> list[dict]:
    """Filtra el directorio maestro de herramientas del FEN por categoría y término."""
    q = search_query.strip().lower()
    filtered = []
    for tool in tools:
        if selected_category != "Todas" and tool.get("categoria") != selected_category:
            continue
        if q:
            haystack = f"{tool.get('nombre', '')} {tool.get('institucion', '')} {tool.get('categoria', '')} {tool.get('utilidad', '')}".lower()
            if q not in haystack:
                continue
        filtered.append(tool)
    return filtered


def _render_fen_header(tools_count: int):
    """Renderiza el encabezado compacto y la cinta ejecutiva de KPIs de Monitoreo El Niño."""
    st.title("🌊 Monitoreo El Niño (FEN)")
    st.markdown(
        '<p class="hero-subtitle">Vigilancia satelital y oceanográfica en tiempo real, declaratorias de emergencia y presupuesto PP 0068.</p>',
        unsafe_allow_html=True,
    )

    render_kpi_ribbon(
        [
            {
                "icon": "🛰️",
                "value": "5",
                "label": "Visores en Vivo",
                "sub": "GOES-19, Windy, ENFEN, CAMI Yaku y SIGRID",
                "href": "?vista=fen&tab=visores",
            },
            {
                "icon": "📡",
                "value": f"{tools_count}",
                "label": "Herramientas",
                "sub": "Enlaces oficiales auditados",
                "href": "?vista=fen&tab=catalogo#catalogo-fen",
            },
            {
                "icon": "⚖️",
                "value": "TTL 30m",
                "label": "Radar Legal",
                "sub": "El Peruano, PCM, ANIN y COEN",
                "href": "?vista=fen&tab=radar",
            },
            {
                "icon": "💰",
                "value": "PP 0068",
                "label": "Presupuesto FEN",
                "sub": "PREVAED, Contraloría y Salud",
                "href": "?vista=fen&tab=catalogo",
            },
        ]
    )


def _render_block_2_radar():
    """Renderiza el Bloque 2: Radar Automatizado de Noticias y Normativa sobre El Niño."""
    col_title, col_action = st.columns([3.4, 1.1])
    with col_title:
        st.subheader("📡 Radar de Declaratorias y Coyuntura")
        st.caption("Decretos de emergencia, avisos ENFEN/SENAMHI y cobertura verificada en tiempo real.")
    with col_action:
        st.write("")
        if st.button("🔄 Actualizar radar ahora", key="btn_refresh_fen_radar", use_container_width=True):
            fetch_fen_radar.clear()
            st.rerun()

    radar_data = fetch_fen_radar()
    st.markdown(
        f'<div class="fen-radar-status-bar">'
        f'<span><span class="status-dot-live"></span> <strong>Pipeline RSS Activo:</strong> '
        f'<code>El Niño</code> · <code>ENFEN</code> · <code>SENAMHI</code> · <code>COEN INDECI</code></span>'
        f'<span class="fen-radar-sync-pill">Sync: {radar_data["sync_utc"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_oficial, col_prensa = st.columns(2, gap="large")
    with col_oficial:
        st.markdown(
            '<div class="fen-column-header">'
            '<h3>⚖️ A. Normas y Sector Oficial</h3>'
            '<p>El Peruano, PCM, ANIN, ANA, INDECI y ENFEN</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        render_fen_radar_list(
            radar_data["oficial"],
            empty_msg="No se registraron decretos recientes en el feed; consulte el buscador oficial.",
        )

    with col_prensa:
        st.markdown(
            '<div class="fen-column-header">'
            '<h3>📰 B. Prensa Climática</h3>'
            '<p>Reportes de lluvias, caudales y activación de quebradas</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        render_fen_radar_list(
            radar_data["prensa"],
            empty_msg="No se encontraron notas de prensa recientes en el feed.",
        )


def _render_block_3_ecosystem(impact_cards: list[dict], master_tools: list[dict]):
    """Renderiza el Bloque 3: Impacto Socioeconómico/Presupuestal + Catálogo Filtrable."""
    st.subheader("💰 Presupuesto PP 0068 e Impacto Sectorial")
    st.caption("Fuentes oficiales para auditar gasto PREVAED, damnificados SINPAD, control y salud.")
    render_fen_impact_grid(impact_cards)

    st.markdown("---")
    st.markdown('<div id="catalogo-fen"></div>', unsafe_allow_html=True)
    st.subheader(f"🧭 Catálogo de Herramientas FEN ({len(master_tools)})")

    col_search, col_cat = st.columns([2.2, 1.3])
    with col_search:
        search_q = st.text_input(
            "🔎 Buscar herramienta o variable:",
            placeholder="Ej: SENAMHI, ENFEN, NOAA, CamiYaku, SIGRID, ANA, PREVAED...",
            key="fen_catalog_search",
        )
    with col_cat:
        selected_cat = st.selectbox(
            "Categoría:",
            options=CATALOG_CATEGORIES,
            index=0,
            key="fen_catalog_category",
        )

    filtered_tools = _filter_catalog_tools(master_tools, search_q, selected_cat)
    st.caption(f"Mostrando **{len(filtered_tools)}** de **{len(master_tools)}** plataformas verificadas.")

    tab_grid, tab_table = st.tabs(
        [
            f"🗂️ Tarjetas ({len(filtered_tools)})",
            f"📋 Tabla ({len(filtered_tools)})",
        ]
    )
    with tab_grid:
        render_fen_catalog_grid(filtered_tools)
    with tab_table:
        if filtered_tools:
            df = pd.DataFrame(filtered_tools)
            st.dataframe(
                df,
                column_config={
                    "nombre": st.column_config.TextColumn("Herramienta / Plataforma", width="medium"),
                    "institucion": st.column_config.TextColumn("Institución", width="small"),
                    "categoria": st.column_config.TextColumn("Categoría", width="small"),
                    "frecuencia": st.column_config.TextColumn("Actualización", width="small"),
                    "utilidad": st.column_config.TextColumn("Qué mide / Utilidad", width="large"),
                    "url": st.column_config.LinkColumn("Enlace Directo", display_text="Abrir plataforma ↗", width="small"),
                },
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("No hay herramientas que coincidan con el filtro aplicado.")


def render_fen():
    """Punto de entrada principal de la sección Monitoreo El Niño (FEN)."""
    ficha_qp = sanitize_slug_param(st.query_params.get("ficha"), max_len=80)
    if ficha_qp:
        render_ficha_tecnica_detalle(ficha_qp, origen="fen")
        return

    impact_cards, master_tools = _get_fen_catalog_lists()
    _render_fen_header(len(master_tools))

    tab_opts = [
        "🛰️ Visores en Vivo (5)",
        "📡 Radar Legal y Prensa",
        f"💰 Presupuesto y Catálogo ({len(master_tools)})",
    ]
    tab_qp_map = {"visores": tab_opts[0], "radar": tab_opts[1], "catalogo": tab_opts[2]}
    tab_qp = sanitize_slug_param(st.query_params.get("tab"), max_len=30)
    if tab_qp in tab_qp_map and st.session_state.get("_last_tab_qp_fen") != tab_qp:
        st.session_state["fen_active_tab"] = tab_qp_map[tab_qp]
        st.session_state._last_tab_qp_fen = tab_qp

    active_tab = st.segmented_control(
        "Sección de Monitoreo El Niño",
        options=tab_opts,
        default=st.session_state.get("fen_active_tab", tab_opts[0]),
        selection_mode="single",
        label_visibility="collapsed",
        key="fen_active_tab",
        width="stretch",
    )
    if not active_tab:
        active_tab = tab_opts[0]

    st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    if active_tab == tab_opts[0]:
        st.subheader("🛰️ Monitoreo Satelital, Oceanográfico y Geoespacial")
        st.caption("Acceso directo a las 5 plataformas críticas en el Perú y el Pacífico Oriental.")
        top_four, bottom_wide = _get_hero_cards()
        render_fen_hero_grid(top_four, bottom_wide)
    elif active_tab == tab_opts[1]:
        _render_block_2_radar()
    else:
        _render_block_3_ecosystem(impact_cards, master_tools)

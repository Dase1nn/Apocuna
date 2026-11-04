import html
import streamlit as st

FREQ_BADGE_MAP = {
    "diaria": "badge-freq-diaria",
    "semanal": "badge-freq-semanal",
    "mensual": "badge-freq-mensual",
}


def escape(val) -> str:
    """Escapa de manera segura cadenas de texto para inyección HTML."""
    if val is None:
        return ""
    return html.escape(str(val))


def safe_url(val) -> str | None:
    """Valida que una URL comience por http://, https:// o data:image/ y la escapa con quote=True."""
    if not val or not isinstance(val, str):
        return None
    val_clean = val.strip()
    if val_clean.startswith(("http://", "https://", "data:image/")):
        return html.escape(val_clean, quote=True)
    return None


def _action_button(raw_url: str | None, label: str = "Abrir ↗", fallback: str = "Enlace por confirmar") -> str:
    """Genera el HTML estandarizado de un botón de acción externo o su estado deshabilitado."""
    url_s = safe_url(raw_url)
    if url_s:
        return f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">{escape(label)}</a>'
    return f'<span class="btn-demo-disabled">{escape(fallback)}</span>'


def _demo_badge(item: dict) -> str:
    return '<span class="badge-demo">Datos de ejemplo</span>' if item.get("demo") else ""


def _short_date(iso_str: str | None, default: str = "Reciente") -> str:
    if not iso_str:
        return default
    return escape(str(iso_str)[:10])


def render_kpi_ribbon(metrics: list[dict]):
    """Renderiza una cinta ejecutiva de indicadores clave (KPIs) con diseño moderno y sin saltos de layout."""
    if not metrics:
        return
    items_html = []
    for m in metrics:
        icon = escape(m.get("icon", "📊"))
        value = escape(m.get("value", "0"))
        label = escape(m.get("label", ""))
        sub = escape(m.get("sub", ""))
        items_html.append(
            f'<div class="kpi-metric-card">'
            f'<div class="kpi-metric-top"><span class="kpi-metric-icon">{icon}</span><span class="kpi-metric-value">{value}</span></div>'
            f'<div class="kpi-metric-label">{label}</div>'
            f'<div class="kpi-metric-sub">{sub}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="kpi-ribbon-grid">{"".join(items_html)}</div>', unsafe_allow_html=True)


def render_home_radar_and_boletines_split(metrics: list[dict]):
    """
    Renderiza en Inicio la sección combinada:
    - Izquierda: Título Radar de Coyuntura, Normas y Fuentes Oficiales + Grilla 2x2 de KPIs.
    - Derecha (pegada a la derecha y a altura completa): Tarjeta destacada grande de Boletines de Normas Legales con invitación a tomar un café.
    """
    kpi_items = []
    for m in metrics:
        icon = escape(m.get("icon", "📊"))
        value = escape(m.get("value", "0"))
        label = escape(m.get("label", ""))
        sub = escape(m.get("sub", ""))
        kpi_items.append(
            f'<div class="kpi-metric-card">'
            f'<div class="kpi-metric-top"><span class="kpi-metric-icon">{icon}</span><span class="kpi-metric-value">{value}</span></div>'
            f'<div class="kpi-metric-label">{label}</div>'
            f'<div class="kpi-metric-sub">{sub}</div>'
            f'</div>'
        )

    split_html = (
        f'<div class="radar-spotlight-split">'
        f'<div class="radar-split-left">'
        f'<div class="radar-split-header">'
        f'<h2 class="radar-split-title">🌐 Radar de Coyuntura, Normas y Fuentes Oficiales</h2>'
        f'<p class="radar-split-subtitle">Vigilancia continua de políticas públicas, marco regulatorio y portales de datos abiertos del Perú.</p>'
        f'</div>'
        f'<div class="kpi-grid-2x2">{"".join(kpi_items)}</div>'
        f'</div>'
        f'<div class="radar-split-right">'
        f'<div class="boletines-featured-card">'
        f'<div>'
        f'<div class="card-header-meta">'
        f'<span class="badge-freq badge-freq-diaria">DIARIA</span>'
        f'<span class="inst">EL PERUANO / PCM</span>'
        f'</div>'
        f'<div class="coffee-ritual-pill">☕ Tu lectura regulatoria de cada mañana con un café</div>'
        f'<h3 class="boletines-featured-title">Boletines de Normas Legales y Diario Oficial</h3>'
        f'<p class="boletines-featured-desc">'
        f'Acompaña tu primer café del día revisando las normas legales recién publicadas. '
        f'Monitoreo permanente de decretos supremos, resoluciones ministeriales y ordenanzas emitidas por los tres niveles de gobierno.'
        f'</p>'
        f'</div>'
        f'<div class="boletines-featured-footer">'
        f'<a href="https://busquedas.elperuano.pe/" target="_blank" rel="noopener noreferrer" class="btn-open btn-open-featured">'
        f'☕ Abrir recurso y tomar un café ↗'
        f'</a>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(split_html, unsafe_allow_html=True)


def render_card_row(title: str, cards_data: list):
    """Renderiza una fila genérica de tarjetas con scroll horizontal."""
    if not cards_data:
        return
    st.subheader(title)
    cards_list = [
        f'<div class="card"><div>{_demo_badge(c)}<h3>{escape(c.get("title", ""))}</h3>'
        f'<p>{escape(c.get("description", ""))}</p></div></div>'
        for c in cards_data
    ]
    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_noticias_carousel(title: str, noticias: list):
    """Renderiza un carrusel de noticias ordenadas con scroll horizontal."""
    if not noticias:
        st.info(f"No hay noticias disponibles en {title}.")
        return

    cards_list = []
    for item in noticias:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        fecha = _short_date(item.get("fecha_iso"))
        resumen = escape(item.get("resumen", ""))
        resumen_html = f"<p>{resumen}</p>" if resumen else '<p class="card-muted-placeholder">Cobertura periodística verificada en fuente original.</p>'
        btn_html = _action_button(item.get("url"), "Leer nota ↗")

        cards_list.append(
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="card-source">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div>{_demo_badge(item)}<h3>{titulo}</h3>{resumen_html}</div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_normas_carousel(normas: list):
    """Renderiza carrusel de seguimiento regulatorio y normas legales."""
    if not normas:
        st.info("No hay normas registradas en este grupo.")
        return

    cards_list = []
    for item in normas:
        titulo = escape(item.get("titulo", ""))
        tipo_norma = escape(item.get("tipo_norma", "Norma Legal"))
        entidad = escape(item.get("entidad", ""))
        fecha = _short_date(item.get("fecha_iso"))
        btn_html = _action_button(item.get("url"), "Consultar ↗")

        cards_list.append(
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{tipo_norma}</span><span class="card-date">{fecha}</span></div>'
            f'<div>{_demo_badge(item)}<div class="card-entity-subtitle">{entidad}</div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def _render_portales_directos(portales_directos: list):
    cards_list = []
    for item in portales_directos:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        desc = escape(item.get("descripcion_corta", ""))
        btn_html = _action_button(item.get("url"), "Abrir portal ↗", "Portal no disponible")
        cards_list.append(
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{institucion}</span><span class="card-date">Portal Oficial</span></div>'
            f'<div><h3>{nombre}</h3><p>{desc}</p></div>'
            f'{btn_html}'
            f'</div>'
        )
    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_ckan_carousel(ckan_list: list, portales_directos: list = None):
    """Renderiza carrusel de datasets recientes de portales CKAN o accesos directos."""
    if not ckan_list:
        st.info("ℹ️ La consulta automática de API CKAN está restringida por el firewall institucional; acceda directamente a los portales oficiales verificados:")
        if portales_directos:
            _render_portales_directos(portales_directos)
        return

    cards_list = []
    for item in ckan_list:
        titulo = escape(item.get("titulo", ""))
        portal = escape(item.get("portal", "CKAN"))
        fecha = _short_date(item.get("fecha_modificacion_iso"))
        btn_html = _action_button(item.get("url"), "Abrir dataset ↗")
        cards_list.append(
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{portal}</span><span class="card-date">{fecha}</span></div>'
            f'<div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_fuentes_grid(fuentes: list):
    """Renderiza una cuadrícula de tarjetas de fuentes con etiqueta de tipo e institución."""
    if not fuentes:
        st.info("No se encontraron fuentes que coincidan con el criterio seleccionado.")
        return

    cards_list = []
    for item in fuentes:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        desc = escape(item.get("descripcion_corta", ""))
        tipo = escape(item.get("tipo", "recurso")).upper()
        btn_html = _action_button(item.get("url"), "Explorar fuente ↗")

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta"><span class="inst">{institucion}</span><span class="badge-curso">{tipo}</span></div>'
            f'<h4>{nombre}</h4>'
            f'<p>{desc}</p>'
            f'</div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def _resolve_freq_class(frecuencia: str) -> str:
    f_lower = frecuencia.lower()
    for key, css_cls in FREQ_BADGE_MAP.items():
        if key in f_lower:
            return css_cls
    return "badge-freq-permanente"


def render_polity_cards(tarjetas: list):
    """Renderiza tarjetas para las subsecciones de Polity and Policy con etiquetas de frecuencia."""
    if not tarjetas:
        st.info("No hay insumos disponibles con el filtro actual.")
        return

    cards_list = []
    for item in tarjetas:
        titulo = escape(item.get("titulo", ""))
        desc = escape(item.get("descripcion", ""))
        frecuencia = str(item.get("frecuencia", "Permanente"))
        fuente = escape(item.get("fuente", ""))
        freq_class = _resolve_freq_class(frecuencia)
        freq_badge = f'<span class="badge-freq {freq_class}">{escape(frecuencia)}</span>'
        btn_html = _action_button(item.get("url"), "Abrir recurso ↗")

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div><div class="card-header-meta">{freq_badge}<span class="inst">{fuente}</span></div><h4>{titulo}</h4><p>{desc}</p></div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_estudiantes_apuntes(apuntes: list):
    """Renderiza tarjetas de apuntes de sistemas administrativos con etiqueta de curso y enlace normativo."""
    if not apuntes:
        st.info("No hay apuntes disponibles.")
        return

    cards_list = []
    for item in apuntes:
        titulo = escape(item.get("titulo", ""))
        curso = escape(item.get("curso", "Gestión Pública"))
        sistema = escape(item.get("sistema", ""))
        resumen = escape(item.get("resumen", ""))
        normativa = escape(item.get("normativa", ""))
        normativa_btn = _action_button(item.get("url"), "Marco Normativo ↗", "Normativa (Demo)")

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta"><span class="badge-curso">{curso}</span><span class="badge-portal">{normativa}</span></div>'
            f'<div class="inst">{sistema}</div>'
            f'<h4>{titulo}</h4>'
            f'<p>{resumen}</p>'
            f'</div>'
            f'<div class="card-actions-row">'
            f'{normativa_btn}'
            f'<span class="btn-demo-disabled">Ficha PDF (Próximamente)</span>'
            f'</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_nota_horizontal(nota: dict):
    """Renderiza una nota en formato de tarjeta rectangular horizontal con tiempo estimado de lectura y extracto."""
    meta = nota.get("meta", {})
    titulo = escape(meta.get("titulo", "Sin título"))
    tipo = escape(meta.get("tipo", "NOTA DE INVESTIGACIÓN"))
    autor = escape(meta.get("autor", "Apocuna Hub"))
    fecha = escape(meta.get("fecha", "Reciente"))
    lectura_min = escape(meta.get("lectura_min", 3))
    extracto = escape(meta.get("extracto", ""))
    extracto_html = f'<p class="note-excerpt">{extracto}</p>' if extracto else ""

    card_html = (
        f'<div class="horizontal-note-card">'
        f'<div class="note-img-gradient">'
        f'<div class="note-icon-large">📝</div>'
        f'<div class="note-type-badge">{tipo}</div>'
        f'</div>'
        f'<div class="note-content">'
        f'<div class="note-meta">{tipo} • ⏱️ {lectura_min} min de lectura</div>'
        f'<h3 class="note-title">{titulo}</h3>'
        f'{extracto_html}'
        f'<div class="note-author-date">📅 {fecha} &nbsp;•&nbsp; ✍️ {autor}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_eventos_grid(eventos: list):
    """Renderiza tarjetas de eventos y revistas con etiquetas de fecha límite y enlaces oficiales."""
    if not eventos:
        st.info("No hay eventos o convocatorias registradas que coincidan con los filtros.")
        return

    cards_list = []
    for item in eventos:
        titulo = escape(item.get("titulo", ""))
        tipo = escape(item.get("tipo", "evento")).upper()
        tematica = escape(item.get("tematica", ""))
        fecha_limite = escape(item.get("fecha_limite", "Por anunciar"))
        desc = escape(item.get("descripcion", ""))
        is_continua = any(w in fecha_limite.lower() for w in ("continua", "permanente"))
        badge_cls = "badge-continua" if is_continua else "badge-deadline"
        badge_icon = "🟢" if is_continua else "⏳"
        link_html = _action_button(item.get("enlace"), "Sitio oficial ↗")

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta">'
            f'<span class="badge-portal">{tipo}</span>'
            f'<span class="{badge_cls}">{badge_icon} {fecha_limite}</span>'
            f'</div>'
            f'<div class="inst">{tematica}</div>'
            f'<h4>{titulo}</h4>'
            f'<p>{desc}</p>'
            f'</div>'
            f'<div class="card-footer-action">{link_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_academico_carousel(academico: list):
    """Renderiza un carrusel de alertas académicas (OpenAlex, Politai, CLACSO)."""
    if not academico:
        st.info("No hay alertas académicas disponibles.")
        return

    cards_list = []
    for item in academico:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        autores = escape(item.get("autores", "Autor institucional"))
        fecha = _short_date(item.get("fecha_iso"))
        btn_html = _action_button(item.get("url"), "Ver publicación ↗")

        cards_list.append(
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="card-source">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div><div class="card-author-line">{autores}</div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )

    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_polity_alertas_carousel(alertas: list):
    """Renderiza un carrusel de alertas institucionales de Polity and Policy."""
    if not alertas:
        st.info("No hay alertas recientes de instituciones.")
        return

    cards_list = [
        f'<div class="card">'
        f'<div class="card-header-meta"><span class="badge-portal">{escape(item.get("fuente", ""))}</span>'
        f'<span class="card-date">{_short_date(item.get("fecha_iso"))}</span></div>'
        f'<div><h3>{escape(item.get("titulo", ""))}</h3></div>'
        f'{_action_button(item.get("url"), "Leer alerta ↗")}'
        f'</div>'
        for item in alertas
    ]
    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_eventos_alertas_carousel(alertas: list):
    """Renderiza un carrusel de alertas de eventos y convocatorias."""
    if not alertas:
        st.info("No hay convocatorias recientes.")
        return

    cards_list = [
        f'<div class="card">'
        f'<div class="card-header-meta"><span class="badge-portal">{escape(item.get("fuente", ""))}</span>'
        f'<span class="card-date">{_short_date(item.get("fecha_iso"))}</span></div>'
        f'<div><h3>{escape(item.get("titulo", ""))}</h3></div>'
        f'{_action_button(item.get("url"), "Ver novedad ↗")}'
        f'</div>'
        for item in alertas
    ]
    st.markdown(f'<div class="card-container">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def _resolve_costo_badge(costo: str) -> str:
    c_lower = costo.lower()
    if "gratuito" in c_lower and "pago" not in c_lower:
        return f'<span class="badge-continua">{escape(costo)}</span>'
    if "pago" in c_lower:
        return f'<span class="badge-deadline">{escape(costo)}</span>'
    return f'<span class="badge-curso">{escape(costo)}</span>'


def render_cursos_grid(cursos: list):
    """Renderiza tarjetas de cursos con insignias de costo, modalidad, idioma y descripción."""
    if not cursos:
        st.info("No hay cursos disponibles con estos filtros.")
        return

    cards_list = []
    for item in cursos:
        nombre = escape(item.get("nombre", ""))
        proveedor = escape(item.get("proveedor", ""))
        modalidad = escape(item.get("modalidad", "")).upper()
        costo = str(item.get("costo", ""))
        idioma = escape(item.get("idioma", ""))
        tema = escape(item.get("descripcion_corta") or item.get("tema", ""))
        cert = escape(item.get("certificacion", ""))
        verificado_en = _short_date(item.get("verificado_en"))
        btn_html = _action_button(item.get("url"), "Ir al curso ↗")
        costo_badge = _resolve_costo_badge(costo)
        cert_text = f" • Certificación: {cert}" if cert else ""

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta"><span class="badge-curso">{modalidad}</span>{costo_badge}</div>'
            f'<div class="inst">{proveedor} • {idioma}</div>'
            f'<h4>{nombre}</h4>'
            f'<p>{tema}</p>'
            f'<div class="card-verified-meta">✓ Verificado: {verificado_en}{cert_text}</div>'
            f'</div>'
            f'<div class="card-footer-action">{btn_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def render_becas_grid(becas: list):
    """Renderiza tarjetas de becas con aviso accesible en modo claro y oscuro."""
    if not becas:
        st.info("No hay becas disponibles.")
        return

    cards_list = []
    for item in becas:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        tipo = escape(item.get("tipo", "beca")).upper()
        verificado_en = _short_date(item.get("verificado_en"))
        btn_html = _action_button(item.get("url"), "Portal de becas ↗")

        cards_list.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta"><span class="badge-portal">{tipo}</span><span class="card-date">Verificado: {verificado_en}</span></div>'
            f'<div class="inst">{institucion}</div>'
            f'<h4>{nombre}</h4>'
            f'<div class="beca-warning-box">'
            f'⚠️ Confirma plazos, bases y requisitos vigentes en el portal oficial.'
            f'</div>'
            f'</div>'
            f'<div class="card-footer-action">{btn_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="fuentes-grid">{"".join(cards_list)}</div>', unsafe_allow_html=True)


def _build_fen_hero_card_html(item: dict, is_full_width: bool = False) -> str:
    """Construye el HTML de una tarjeta del Hero Grid de monitoreo FEN con vista previa visual y fallback SVG/CSS."""
    card_cls = "fen-hero-full-card" if is_full_width else "fen-hero-card"
    entidad = escape(item.get("entidad", ""))
    estado = escape(item.get("estado", "EN VIVO / TIEMPO REAL"))
    titulo = escape(item.get("titulo", ""))
    descripcion = escape(item.get("descripcion", ""))
    preview_url = safe_url(item.get("preview_url")) or ""
    theme_cls = escape(item.get("theme_class", "fen-theme-sat"))
    svg_art = item.get("svg_fallback", "")
    metricas = item.get("metricas", [])
    url_principal = item.get("url")
    btn_label = item.get("btn_label", "Abrir plataforma en vivo ↗")
    secundarios = item.get("enlaces_secundarios", [])

    pills_html = "".join(
        f'<span class="fen-metric-pill">{escape(m)}</span>' for m in metricas
    )
    sec_btns = "".join(
        f'<a href="{safe_url(sec["url"])}" target="_blank" rel="noopener noreferrer" class="btn-fen-secondary">'
        f'{escape(sec["label"])} ↗</a>'
        for sec in secundarios
        if safe_url(sec.get("url"))
    )
    img_tag = (
        f'<img src="{preview_url}" alt="{titulo}" class="fen-preview-img" loading="lazy" '
        f'onerror="this.style.display=\'none\';" />'
        if preview_url else ""
    )

    return (
        f'<div class="{card_cls}">'
        f'<div class="fen-preview-container {theme_cls}">'
        f'<div class="fen-preview-svg-layer">{svg_art}</div>'
        f'{img_tag}'
        f'<div class="fen-preview-overlay-top">'
        f'<span class="fen-entity-badge">{entidad}</span>'
        f'<span class="fen-live-badge"><span class="status-dot-live"></span>{estado}</span>'
        f'</div>'
        f'<div class="fen-preview-overlay-bottom">'
        f'<div class="fen-metrics-row">{pills_html}</div>'
        f'</div>'
        f'</div>'
        f'<div class="fen-card-body">'
        f'<div>'
        f'<h3 class="fen-card-title">{titulo}</h3>'
        f'<p class="fen-card-desc">{descripcion}</p>'
        f'</div>'
        f'<div class="fen-card-actions">'
        f'{_action_button(url_principal, btn_label)}'
        f'{sec_btns}'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def render_fen_hero_grid(top_four_cards: list[dict], bottom_wide_card: dict):
    """Renderiza el Bloque 1 del FEN: Grilla 2x2 superior + 1 barra horizontal 100% width inferior."""
    cards_2x2 = "".join(_build_fen_hero_card_html(c, is_full_width=False) for c in top_four_cards[:4])
    wide_html = _build_fen_hero_card_html(bottom_wide_card, is_full_width=True)
    full_block = (
        f'<div class="fen-hero-wrapper">'
        f'<div class="fen-hero-grid-2x2">{cards_2x2}</div>'
        f'{wide_html}'
        f'</div>'
    )
    st.markdown(full_block, unsafe_allow_html=True)


def render_fen_radar_list(items: list[dict], empty_msg: str = "No se encontraron reportes recientes."):
    """Renderiza una lista compacta y cronológica de noticias o normas sobre el Fenómeno El Niño."""
    if not items:
        st.info(empty_msg)
        return

    cards_html = []
    for item in items:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", "Fuente verificada"))
        fecha = escape(item.get("fecha_legible") or _short_date(item.get("fecha_iso")))
        categoria = escape(item.get("etiqueta", "MONITOREO FEN"))
        badge_cls = "badge-freq-diaria" if item.get("es_oficial") else "badge-portal"
        btn_html = _action_button(item.get("url"), "Verificar fuente ↗")

        cards_html.append(
            f'<div class="fen-radar-item">'
            f'<div class="card-header-meta">'
            f'<span class="badge-freq {badge_cls}">{categoria}</span>'
            f'<span class="card-date">📅 {fecha}</span>'
            f'</div>'
            f'<div class="fen-radar-source">{fuente}</div>'
            f'<h4 class="fen-radar-title">{titulo}</h4>'
            f'<div class="fen-radar-footer">{btn_html}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="fen-radar-stack">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def render_fen_impact_grid(impact_cards: list[dict]):
    """Renderiza las 4 tarjetas de monitoreo del impacto socioeconómico, presupuestal y sanitario del FEN."""
    if not impact_cards:
        return
    cards_html = []
    for item in impact_cards:
        institucion = escape(item.get("institucion", ""))
        eje = escape(item.get("eje", ""))
        titulo = escape(item.get("titulo", ""))
        desc = escape(item.get("descripcion", ""))
        indicadores = item.get("indicadores", [])
        pills = "".join(f'<span class="fen-impact-tag">{escape(ind)}</span>' for ind in indicadores)
        sec_url = safe_url(item.get("url_secundaria"))
        sec_label = escape(item.get("label_secundaria", "Portal adicional"))
        sec_btn = (
            f'<a href="{sec_url}" target="_blank" rel="noopener noreferrer" class="btn-fen-secondary">{sec_label} ↗</a>'
            if sec_url else ""
        )

        cards_html.append(
            f'<div class="fuente-card fen-impact-card">'
            f'<div>'
            f'<div class="card-header-meta">'
            f'<span class="badge-portal">{eje}</span>'
            f'<span class="badge-continua">DATOS ABIERTOS</span>'
            f'</div>'
            f'<div class="inst">{institucion}</div>'
            f'<h4>{titulo}</h4>'
            f'<p>{desc}</p>'
            f'<div class="fen-impact-tags-row">{pills}</div>'
            f'</div>'
            f'<div class="card-actions-row">'
            f'{_action_button(item.get("url"), item.get("btn_label", "Consultar plataforma ↗"))}'
            f'{sec_btn}'
            f'</div>'
            f'</div>'
        )
    st.markdown(f'<div class="fuentes-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)


def render_fen_catalog_grid(tools: list[dict]):
    """Renderiza el directorio maestro filtrable de herramientas técnicas de monitoreo del FEN."""
    if not tools:
        st.info("No se encontraron herramientas con los criterios de búsqueda seleccionados.")
        return

    cards_html = []
    for item in tools:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        categoria = escape(item.get("categoria", ""))
        frecuencia = escape(item.get("frecuencia", "Tiempo real"))
        utilidad = escape(item.get("utilidad", ""))
        freq_cls = _resolve_freq_class(frecuencia)

        cards_html.append(
            f'<div class="fuente-card">'
            f'<div>'
            f'<div class="card-header-meta">'
            f'<span class="badge-portal">{categoria}</span>'
            f'<span class="badge-freq {freq_cls}">{frecuencia}</span>'
            f'</div>'
            f'<div class="inst">{institucion}</div>'
            f'<h4>{nombre}</h4>'
            f'<p>{utilidad}</p>'
            f'</div>'
            f'<div class="card-footer-action">'
            f'{_action_button(item.get("url"), "Abrir herramienta ↗")}'
            f'</div>'
            f'</div>'
        )
    st.markdown(f'<div class="fuentes-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

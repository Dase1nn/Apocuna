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
    """Valida que una URL comience por http:// o https:// y la escapa con quote=True."""
    if not val or not isinstance(val, str):
        return None
    val_clean = val.strip()
    if val_clean.startswith(("http://", "https://")):
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

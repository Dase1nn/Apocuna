import html
import streamlit as st

def escape(val):
    """Escapa de manera segura cadenas de texto para inyección HTML."""
    if val is None:
        return ""
    return html.escape(str(val))

def safe_url(val):
    """Valida que una URL comience por http:// o https:// y la escapa con quote=True."""
    if not val or not isinstance(val, str):
        return None
    val_clean = val.strip()
    if val_clean.startswith("http://") or val_clean.startswith("https://"):
        return html.escape(val_clean, quote=True)
    return None

def render_card_row(title: str, cards_data: list):
    """
    Renderiza una fila genérica de tarjetas con scroll horizontal (estilo Snowsight).
    """
    if not cards_data:
        return
        
    st.subheader(title)
    cards_list = []
    for card in cards_data:
        title_esc = escape(card.get('title', ''))
        desc_esc = escape(card.get('description', ''))
        demo_badge = '<span class="badge-demo">Datos de ejemplo</span>' if card.get('demo') else ''
        card_html = f'<div class="card"><div>{demo_badge}<h3>{title_esc}</h3><p>{desc_esc}</p></div></div>'
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_noticias_carousel(title: str, noticias: list):
    """
    Renderiza un carrusel de noticias ordenadas con scroll horizontal.
    """
    if not noticias:
        st.info("No hay noticias disponibles en esta categoría.")
        return
        
    cards_list = []
    for item in noticias:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        fecha = escape(item.get("fecha_iso", ""))
        resumen = escape(item.get("resumen", ""))
        url_s = safe_url(item.get("url"))
        demo_badge = '<span class="badge-demo">Datos de ejemplo</span>' if item.get("demo") else ''
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="card-source">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div>{demo_badge}<h3>{titulo}</h3><p>{resumen}</p></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_normas_carousel(normas: list):
    """
    Renderiza carrusel de normas legales de El Peruano.
    """
    if not normas:
        st.info("No hay normas registradas en este grupo.")
        return
        
    cards_list = []
    for item in normas:
        titulo = escape(item.get("titulo", ""))
        tipo_norma = escape(item.get("tipo_norma", ""))
        entidad = escape(item.get("entidad", ""))
        fecha = escape(item.get("fecha_iso", ""))
        url_s = safe_url(item.get("url"))
        demo_badge = '<span class="badge-demo">Datos de ejemplo</span>' if item.get("demo") else ''
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="card-source">{tipo_norma}</span><span class="card-date">{fecha}</span></div>'
            f'<div>{demo_badge}<div style="font-size:0.78rem; font-weight:600; opacity:0.8; margin-bottom:0.3rem;">{entidad}</div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_ckan_carousel(ckan_list: list, portales_directos: list = None):
    """
    Renderiza carrusel de datasets recientes de portales CKAN.
    Si ckan_list está vacío, muestra aviso y tarjetas con enlaces directos a los portales.
    """
    if not ckan_list:
        st.info("ℹ️ La API de este portal no está disponible por ahora.")
        if portales_directos:
            cards_list = []
            for item in portales_directos:
                nombre = escape(item.get("nombre", ""))
                institucion = escape(item.get("institucion", ""))
                desc = escape(item.get("descripcion_corta", ""))
                url_s = safe_url(item.get("url"))
                btn_html = (
                    f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir portal ↗</a>'
                    if url_s else '<span class="btn-demo-disabled">Portal no disponible</span>'
                )
                
                card_html = (
                    f'<div class="card">'
                    f'<div class="card-header-meta"><span class="badge-portal">{institucion}</span><span class="card-date">Portal Oficial</span></div>'
                    f'<div><h3>{nombre}</h3><p style="font-size:0.85rem; margin-top:0.4rem;">{desc}</p></div>'
                    f'{btn_html}'
                    f'</div>'
                )
                cards_list.append(card_html)
            full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
            st.markdown(full_html, unsafe_allow_html=True)
        return
        
    cards_list = []
    for item in ckan_list:
        titulo = escape(item.get("titulo", ""))
        portal = escape(item.get("portal", "CKAN"))
        fecha_raw = item.get("fecha_modificacion_iso", "")
        fecha = escape(fecha_raw[:10] if fecha_raw else "Reciente")
        url_s = safe_url(item.get("url"))
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{portal}</span><span class="card-date">{fecha}</span></div>'
            f'<div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_fuentes_grid(fuentes: list):
    """
    Renderiza una cuadrícula de tarjetas de fuentes con botón Abrir.
    """
    if not fuentes:
        st.info("No hay fuentes en este bloque.")
        return
        
    cards_list = []
    for item in fuentes:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        desc = escape(item.get("descripcion_corta", ""))
        url_s = safe_url(item.get("url"))
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="fuente-card">'
            f'<div><div class="inst">{institucion}</div><h4>{nombre}</h4><p>{desc}</p></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_polity_cards(tarjetas: list):
    """
    Renderiza tarjetas para las subsecciones de Polity and Policy con etiquetas de frecuencia.
    """
    if not tarjetas:
        st.info("No hay insumos disponibles.")
        return
        
    cards_list = []
    for item in tarjetas:
        titulo = escape(item.get("titulo", ""))
        desc = escape(item.get("descripcion", ""))
        frecuencia = item.get("frecuencia", "Permanente")
        fuente = escape(item.get("fuente", ""))
        url_s = safe_url(item.get("url"))
        
        freq_class = "badge-freq-permanente"
        frec_lower = frecuencia.lower()
        if "diaria" in frec_lower:
            freq_class = "badge-freq-diaria"
        elif "semanal" in frec_lower:
            freq_class = "badge-freq-semanal"
        elif "mensual" in frec_lower:
            freq_class = "badge-freq-mensual"
            
        freq_badge = f'<span class="badge-freq {freq_class}">{escape(frecuencia)}</span>'
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Abrir ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="fuente-card">'
            f'<div>{freq_badge}<div class="inst">{fuente}</div><h4>{titulo}</h4><p>{desc}</p></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_estudiantes_apuntes(apuntes: list):
    """
    Renderiza tarjetas de apuntes de sistemas administrativos con etiqueta de curso y botón demo.
    """
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
        url_s = safe_url(item.get("url"))
        
        normativa_btn = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open" style="margin-top:0;">Normativa ↗</a>'
            if url_s else '<span class="btn-demo-disabled" style="margin-top:0;">Normativa (Demo)</span>'
        )
        
        card_html = (
            f'<div class="fuente-card">'
            f'<div>'
            f'<span class="badge-curso">{curso}</span>'
            f'<div class="inst">{sistema} • {normativa}</div>'
            f'<h4>{titulo}</h4>'
            f'<p>{resumen}</p>'
            f'</div>'
            f'<div style="display:flex; gap:0.5rem; align-items:center; margin-top:0.75rem;">'
            f'<span class="btn-demo-disabled">Descargar (Demo)</span>'
            f'{normativa_btn}'
            f'</div>'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_nota_horizontal(nota: dict):
    """
    Renderiza una nota en formato de tarjeta rectangular horizontal con degradado CSS.
    """
    meta = nota.get("meta", {})
    titulo = escape(meta.get("titulo", "Sin título"))
    tipo = escape(meta.get("tipo", "NOTA DE INVESTIGACIÓN"))
    autor = escape(meta.get("autor", "Apocuna Hub"))
    fecha = escape(meta.get("fecha", "Reciente"))
    
    card_html = (
        f'<div class="horizontal-note-card">'
        f'<div class="note-img-gradient">'
        f'<div style="font-size:1.8rem; margin-bottom:0.3rem;">📝</div>'
        f'<div style="font-size:0.85rem; letter-spacing:0.5px;">{tipo}</div>'
        f'</div>'
        f'<div class="note-content">'
        f'<div class="note-meta">{tipo} • {autor}</div>'
        f'<h3 class="note-title">{titulo}</h3>'
        f'<div class="note-author-date">📅 {fecha} &nbsp;•&nbsp; ✍️ {autor}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

def render_eventos_grid(eventos: list):
    """
    Renderiza tarjetas de eventos y revistas con etiquetas de fecha límite y enlaces oficiales.
    """
    if not eventos:
        st.info("No hay eventos registrados que coincidan con los filtros.")
        return
        
    cards_list = []
    for item in eventos:
        titulo = escape(item.get("titulo", ""))
        tipo = escape(item.get("tipo", "evento")).upper()
        tematica = escape(item.get("tematica", ""))
        fecha_limite = escape(item.get("fecha_limite", "Por anunciar"))
        enlace_s = safe_url(item.get("enlace"))
        desc = escape(item.get("descripcion", ""))
        
        f_lower = fecha_limite.lower()
        if "continua" in f_lower or "permanente" in f_lower:
            badge_fecha = f'<span class="badge-continua">🟢 {fecha_limite}</span>'
        else:
            badge_fecha = f'<span class="badge-deadline">⏳ {fecha_limite}</span>'
            
        link_html = (
            f'<a href="{enlace_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Sitio oficial ↗</a>'
            if enlace_s
            else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="fuente-card">'
            f'<div>'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">'
            f'<span class="badge-portal">{tipo}</span>'
            f'{badge_fecha}'
            f'</div>'
            f'<div class="inst">{tematica}</div>'
            f'<h4>{titulo}</h4>'
            f'<p>{desc}</p>'
            f'</div>'
            f'<div style="margin-top:0.75rem;">{link_html}</div>'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_academico_carousel(academico: list):
    """
    Renderiza un carrusel de alertas académicas.
    """
    if not academico:
        st.info("No hay alertas académicas disponibles.")
        return
        
    cards_list = []
    for item in academico:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        autores = escape(item.get("autores", ""))
        fecha_raw = item.get("fecha_iso", "")
        fecha = escape(fecha_raw[:10] if fecha_raw else "Reciente")
        url_s = safe_url(item.get("url"))
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Leer ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="card-source">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div><div style="font-size:0.75rem; font-weight:600; margin-bottom:0.25rem; color:var(--text-accent);">{autores}</div>'
            f'<h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_polity_alertas_carousel(alertas: list):
    """
    Renderiza un carrusel de alertas de polity and policy.
    """
    if not alertas:
        st.info("No hay alertas recientes de instituciones.")
        return
        
    cards_list = []
    for item in alertas:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        fecha_raw = item.get("fecha_iso", "")
        fecha = escape(fecha_raw[:10] if fecha_raw else "Reciente")
        url_s = safe_url(item.get("url"))
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Leer ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_eventos_alertas_carousel(alertas: list):
    """
    Renderiza un carrusel de alertas de eventos y convocatorias.
    """
    if not alertas:
        st.info("No hay convocatorias recientes.")
        return
        
    cards_list = []
    for item in alertas:
        titulo = escape(item.get("titulo", ""))
        fuente = escape(item.get("fuente", ""))
        fecha_raw = item.get("fecha_iso", "")
        fecha = escape(fecha_raw[:10] if fecha_raw else "Reciente")
        url_s = safe_url(item.get("url"))
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Ver ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="card">'
            f'<div class="card-header-meta"><span class="badge-portal">{fuente}</span><span class="card-date">{fecha}</span></div>'
            f'<div><h3>{titulo}</h3></div>'
            f'{btn_html}'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="card-container">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_cursos_grid(cursos: list):
    """
    Renderiza tarjetas de cursos con insignias de costo y modalidad.
    """
    if not cursos:
        st.info("No hay cursos disponibles con estos filtros.")
        return
        
    cards_list = []
    for item in cursos:
        nombre = escape(item.get("nombre", ""))
        proveedor = escape(item.get("proveedor", ""))
        modalidad = escape(item.get("modalidad", ""))
        costo = escape(item.get("costo", ""))
        idioma = escape(item.get("idioma", ""))
        tema = escape(item.get("tema", ""))
        verificado_en = escape(item.get("verificado_en", "")[:10])
        url_s = safe_url(item.get("url"))
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Ver Curso ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        # Color coding cost con badges modernos
        costo_lower = costo.lower()
        if "gratuito" in costo_lower and "pago" not in costo_lower:
            costo_badge = f'<span class="badge-continua" style="margin-bottom:0;">{costo}</span>'
        elif "pago" in costo_lower:
            costo_badge = f'<span class="badge-deadline" style="margin-bottom:0;">{costo}</span>'
        else:
            costo_badge = f'<span class="badge-curso" style="margin-bottom:0;">{costo}</span>'

        card_html = (
            f'<div class="fuente-card">'
            f'<div>'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">'
            f'<span class="badge-curso">{modalidad}</span>'
            f'{costo_badge}'
            f'</div>'
            f'<div class="inst">{proveedor} • {idioma}</div>'
            f'<h4>{nombre}</h4>'
            f'<p>{tema}</p>'
            f'<div style="font-size:0.72rem; color:var(--text-muted); margin-top:0.5rem;">Verificado: {verificado_en}</div>'
            f'</div>'
            f'<div style="margin-top:0.75rem;">{btn_html}</div>'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

def render_becas_grid(becas: list):
    """
    Renderiza tarjetas de becas con el aviso requerido.
    """
    if not becas:
        st.info("No hay becas disponibles.")
        return
        
    cards_list = []
    for item in becas:
        nombre = escape(item.get("nombre", ""))
        institucion = escape(item.get("institucion", ""))
        tipo = escape(item.get("tipo", ""))
        verificado_en = escape(item.get("verificado_en", "")[:10])
        url_s = safe_url(item.get("url"))
        
        btn_html = (
            f'<a href="{url_s}" target="_blank" rel="noopener noreferrer" class="btn-open">Sitio oficial ↗</a>'
            if url_s else '<span class="btn-demo-disabled">Enlace por confirmar</span>'
        )
        
        card_html = (
            f'<div class="fuente-card">'
            f'<div>'
            f'<span class="badge-portal">{tipo}</span>'
            f'<div class="inst" style="margin-top:0.5rem;">{institucion}</div>'
            f'<h4>{nombre}</h4>'
            f'<div style="background:rgba(245, 158, 11, 0.15); color:#FBBF24; border:1px solid rgba(245, 158, 11, 0.35); padding:6px 10px; border-radius:6px; font-size:0.75rem; margin:10px 0; font-weight:500;">'
            f'⚠️ Confirma plazos y requisitos en el sitio oficial.'
            f'</div>'
            f'<div style="font-size:0.72rem; color:var(--text-muted);">Verificado: {verificado_en}</div>'
            f'</div>'
            f'<div style="margin-top:0.75rem;">{btn_html}</div>'
            f'</div>'
        )
        cards_list.append(card_html)
        
    full_html = f'<div class="fuentes-grid">{"".join(cards_list)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

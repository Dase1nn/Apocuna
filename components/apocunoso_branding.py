"""Componentes visuales de identidad para el sistema de diseño `apocunoso-style`.

Combina:
1. Arquitectura de marcos anidados y paleta cálida de `ndebele-mural-art` (#FAF7E9, #171B18, #2775AA, #DF6A90, #F0BB38, #1B8668).
2. Geometría ancestral peruana Shipibo-Konibo *Kené* (caminos maestros *kano*, cruces escalonadas *vero yushin*, semilla *vero*).
3. Tipografía grotesca, retícula modular de 1.5px y neutralidad informativa de `swiss-international`.
"""

import os
import functools


def _compact_svg(raw_svg: str) -> str:
    """Compacta un SVG multilínea en una sola línea sin saltos vacíos para evitar bloques <pre> en Markdown."""
    return " ".join(line.strip() for line in raw_svg.splitlines() if line.strip())


@functools.lru_cache(maxsize=4)
def get_apocuna_logo_svg() -> str:
    """Devuelve el SVG en línea del logo rediseñado de Apocuna (Apu + Kené)."""
    svg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "apocuna_logo.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            return _compact_svg(f.read())
    return ""


@functools.lru_cache(maxsize=4)
def get_kene_mural_banner_svg() -> str:
    """Devuelve el SVG en línea del banner mural tripartito en arte Kené."""
    svg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "kene_banner.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            return _compact_svg(f.read())
    return ""


def build_sidebar_brand_html() -> str:
    """Construye el bloque de identidad del sidebar sin isotipo duplicado, conservando la forma tipográfica del Hero."""
    return (
        '<div class="sidebar-brand-box">'
        '<div class="sidebar-brand-toprow">'
        '<div class="sidebar-brand-textcol">'
        '<div class="sidebar-brand-badge">PERÚ · PUBLIC POLICY HUB</div>'
        '<div class="sidebar-brand-title" role="heading" aria-level="1"><span>APOCUNA</span><span>HUB<b class="apocunoso-period-dot">.</b></span></div>'
        '<div class="sidebar-brand-subtitle">EVIDENCIA, DATOS &amp; GOBERNANZA</div>'
        '</div>'
        '</div>'
        '<div class="sidebar-kene-colorbar" aria-hidden="true">'
        '<span class="kbar-blue"></span>'
        '<span class="kbar-pink"></span>'
        '<span class="kbar-gold"></span>'
        '<span class="kbar-green"></span>'
        '</div>'
        '</div>'
    )


def build_apocunoso_hero_banner_html() -> str:
    """Construye el encabezado arquitectónico `apocunoso-style` (inspirado en COMMON ROOM + arte Kené)."""
    banner_svg = get_kene_mural_banner_svg()
    logo_svg = get_apocuna_logo_svg()
    return (
        '<div class="apocunoso-hero-frame">'
        '<div class="apocunoso-hero-toprow">'
        '<div class="apocunoso-hero-brand">'
        f'<div class="apocunoso-hero-logo">{logo_svg}</div>'
        '<div class="apocunoso-hero-wordmark">'
        '<span>APOCUNA</span>'
        '<span>HUB<b class="apocunoso-period-dot">.</b></span>'
        '</div>'
        '</div>'
        '<div class="apocunoso-hero-motto">'
        '<span>UN ESPACIO DE EVIDENCIA</span>'
        '<span>PARA PENSAR EL PERÚ.</span>'
        '<small class="apocunoso-hero-submotto">ESTILO APOCUNOSO · ARTE KENÉ SHIPIBO-KONIBO × SWISS INTERNATIONAL</small>'
        '</div>'
        '</div>'
        f'<div class="apocunoso-kene-mural-wrap">{banner_svg}</div>'
        '<div class="apocunoso-quiet-reading-panel">'
        '<div class="apocunoso-quiet-eyebrow">PLATAFORMA PERUANA DE EVIDENCIA, MONITOREO CLIMÁTICO Y VIGILANCIA NORMATIVA</div>'
        '<div class="apocunoso-quiet-grid">'
        '<h1 class="apocunoso-quiet-title">¿Qué es APOCUNA y por qué existe?</h1>'
        '<p class="apocunoso-quiet-copy">'
        'Un observatorio cívico y académico que articula seguimiento diario automatizado de <strong>El Peruano</strong>, '
        'monitoreo multi-agencia del <strong>Fenómeno El Niño (FEN)</strong> y bases de datos verificadas para quienes '
        'diseñan, evalúan y estudian las políticas públicas en el Perú.'
        '</p>'
        '</div>'
        '</div>'
        '</div>'
    )

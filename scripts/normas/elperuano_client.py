"""Cliente HTTP respetuoso para busquedas.elperuano.pe (El Peruano - Normas Legales)."""

import hashlib
import html as html_lib
import json
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


USER_AGENT = "ApocunaBot/1.0 (+https://github.com/Dase1nn/Apocuna)"
BASE_URL = "https://busquedas.elperuano.pe"
MIN_INTERVAL_SEC = 2.2

_ULTIMA_PETICION_TS = 0.0


def _esperar_turno(min_intervalo: float = MIN_INTERVAL_SEC) -> None:
    """Garantiza un espaciado mínimo entre solicitudes al mismo dominio."""
    global _ULTIMA_PETICION_TS
    ahora = time.monotonic()
    transcurrido = ahora - _ULTIMA_PETICION_TS
    if _ULTIMA_PETICION_TS > 0 and transcurrido < min_intervalo:
        time.sleep(min_intervalo - transcurrido)
    _ULTIMA_PETICION_TS = time.monotonic()


def _http_get_texto(url: str, timeout: int = 25) -> Tuple[int, str]:
    """Ejecuta GET con User-Agent oficial ApocunaBot."""
    _esperar_turno()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        codigo = int(getattr(resp, "status", 200))
        cuerpo = resp.read().decode("utf-8", errors="replace")
    return codigo, cuerpo


def _extraer_arrays_stream(raw_html: str) -> List[List[Any]]:
    """Extrae arreglos codificados dentro de llamadas `streamController.enqueue(...)`."""
    bloques: List[List[Any]] = []
    for m in re.finditer(r'enqueue\("((?:\\.|[^"\\])*)"\);', raw_html, re.S):
        try:
            decodificado = json.loads('"' + m.group(1) + '"')
            arr = json.loads(decodificado)
            if isinstance(arr, list):
                bloques.append(arr)
        except Exception:
            continue
    return bloques


def _resolver_ref(
    idx: int,
    arr: List[Any],
    memo: Dict[int, Any],
    profundidad: int,
) -> Any:
    """Resuelve una referencia entera de Turbo Stream hacia el arreglo `arr`."""
    if idx < 0:
        return None
    if idx in memo:
        return memo[idx]
    if idx >= len(arr) or profundidad > 30:
        return None
    objetivo = arr[idx]
    if isinstance(objetivo, (dict, list)):
        res = _resolver_nodo_stream(objetivo, arr, memo, profundidad + 1)
    else:
        res = objetivo
    memo[idx] = res
    return res


def _resolver_nodo_stream(
    nodo: Any,
    arr: List[Any],
    memo: Dict[int, Any],
    profundidad: int = 0,
) -> Any:
    """Reconstruye objetos desde el formato indexado de React Router stream."""
    if profundidad > 30:
        return None
    if isinstance(nodo, list):
        salida_lista: List[Any] = []
        for el in nodo:
            if isinstance(el, int):
                salida_lista.append(_resolver_ref(el, arr, memo, profundidad + 1))
            else:
                salida_lista.append(_resolver_nodo_stream(el, arr, memo, profundidad + 1))
        return salida_lista
    if isinstance(nodo, dict):
        salida: Dict[str, Any] = {}
        for k, v in nodo.items():
            clave = k
            if isinstance(k, str) and k.startswith("_") and k[1:].isdigit():
                idx_k = int(k[1:])
                clave = arr[idx_k] if 0 <= idx_k < len(arr) else k
            if isinstance(v, int):
                val = _resolver_ref(v, arr, memo, profundidad + 1)
            else:
                val = _resolver_nodo_stream(v, arr, memo, profundidad + 1)
            salida[str(clave)] = val
        return salida
    return nodo


def _buscar_clave_recursiva(obj: Any, clave_objetivo: str) -> Optional[Any]:
    """Busca recursivamente la primera ocurrencia de una clave en diccionarios/listas."""
    if isinstance(obj, dict):
        if clave_objetivo in obj:
            return obj[clave_objetivo]
        for v in obj.values():
            encontrado = _buscar_clave_recursiva(v, clave_objetivo)
            if encontrado is not None:
                return encontrado
    elif isinstance(obj, list):
        for el in obj:
            encontrado = _buscar_clave_recursiva(el, clave_objetivo)
            if encontrado is not None:
                return encontrado
    return None


def parsear_listado_html(raw_html: str) -> Tuple[List[Dict[str, Any]], int]:
    """Extrae ítems de normas y total reportado desde el HTML SSR de búsqueda."""
    bloques = _extraer_arrays_stream(raw_html)
    for arr in bloques:
        if "hits" not in arr:
            continue
        memo: Dict[int, Any] = {}
        raiz = _resolver_nodo_stream(arr[0], arr, memo) if arr else None
        hits = _buscar_clave_recursiva(raiz, "hits")
        total = _buscar_clave_recursiva(raiz, "totalHits")
        if total is None:
            total = _buscar_clave_recursiva(raiz, "total")
        if isinstance(hits, list):
            limpios = [h for h in hits if isinstance(h, dict) and h.get("op")]
            total_int = int(total) if isinstance(total, (int, float)) else len(limpios)
            return limpios, total_int
    return [], 0


def parsear_texto_norma_html(raw_html: str) -> Tuple[str, str]:
    """Extrae el texto limpio en memoria y calcula su SHA-256 sin guardar el texto."""
    bloques = _extraer_arrays_stream(raw_html)
    html_content = ""
    for arr in bloques:
        for i, el in enumerate(arr):
            if el == "htmlContent" and i + 1 < len(arr) and isinstance(arr[i + 1], str):
                html_content = arr[i + 1]
                break
        if html_content:
            break

    if not html_content:
        return "", ""

    txt = re.sub(r"</?(?:p|div|h\d|br|li|tr)[^>]*>", "\n", html_content, flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html_lib.unescape(txt)
    lineas = [re.sub(r"\s+", " ", ln).strip() for ln in txt.splitlines()]
    texto_limpio = "\n".join(ln for ln in lineas if ln)
    sha256_hex = hashlib.sha256(texto_limpio.encode("utf-8")).hexdigest()
    return texto_limpio, sha256_hex


def listar_normas_fecha(
    fecha_yyyymmdd: str,
    tipo_publicacion: str = "NL",
    max_items: int = 80,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Descarga el listado paginado de normas del día desde busquedas.elperuano.pe."""
    items: List[Dict[str, Any]] = []
    vistos_op: set = set()
    start = 0
    total_reportado: Optional[int] = None
    paginas = 0

    while len(items) < max_items and paginas < 10:
        params = urllib.parse.urlencode(
            {
                "fechaIni": fecha_yyyymmdd,
                "fechaFin": fecha_yyyymmdd,
                "tipoPublicacion": tipo_publicacion,
                "ci": "ONLY",
                "start": start,
            }
        )
        url = f"{BASE_URL}/?{params}"
        codigo, raw_html = _http_get_texto(url)
        paginas += 1
        if codigo != 200:
            raise RuntimeError(f"HTTP {codigo} al consultar listado {url}")

        lote, total_pagina = parsear_listado_html(raw_html)
        if total_reportado is None:
            total_reportado = total_pagina
        if not lote:
            break

        nuevos_en_pagina = 0
        for item in lote:
            op = str(item.get("op") or "").strip()
            if op and op not in vistos_op:
                vistos_op.add(op)
                items.append(item)
                nuevos_en_pagina += 1
                if len(items) >= max_items:
                    break

        if nuevos_en_pagina == 0 or (total_reportado and len(items) >= total_reportado):
            break
        start += 20

    meta_listado = {
        "fecha": fecha_yyyymmdd,
        "tipo_publicacion": tipo_publicacion,
        "total_reportado": total_reportado if total_reportado is not None else len(items),
        "recibidos": len(items),
        "paginas_consultadas": paginas,
    }
    return items, meta_listado


def obtener_texto_norma(op: str, tipo_publicacion: str = "NL") -> Tuple[int, str, str, str]:
    """Obtiene el HTML de una norma individual y devuelve (http_code, texto_limpio, sha256, url)."""
    url = f"{BASE_URL}/dispositivo/{tipo_publicacion}/{op}"
    codigo, raw_html = _http_get_texto(url)
    if codigo != 200:
        raise RuntimeError(f"HTTP {codigo} al consultar norma {url}")
    texto_limpio, sha256_hex = parsear_texto_norma_html(raw_html)
    if not texto_limpio:
        raise RuntimeError(f"No se pudo extraer htmlContent de {url}")
    return codigo, texto_limpio, sha256_hex, url

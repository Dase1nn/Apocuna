"""Verificador estricto de fichas de normas legales generadas o enriquecidas por IA."""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from scripts.normas.clasificador import normalizar_texto


PALABRAS_PROHIBIDAS_JUICIO = {
    "ilegal",
    "inconstitucional",
    "anticonstitucional",
    "arbitrario",
    "arbitraria",
    "abusivo",
    "abusiva",
    "ilegitimo",
    "ilegitima",
    "nefasto",
    "nefasta",
    "excelente",
    "pesimo",
    "pesima",
    "corrupto",
    "corrupta",
    "legalidad",
    "ilegalidad",
    "legal",
    "constitucional",
}

MARCADORES_CONDICIONAL = re.compile(
    r"\b(?:\w*(?:aria|eria|iria|arian|erian|irian)|podria|podrian|deberia|deberian|"
    r"tendria|tendrian|habria|supondria|implicaria|permitiria|permitirian|"
    r"estableceria|establecerian|modificaria|contribuiria|generaria|requeriria|"
    r"aplicaria|alcanzaria|fortaleceria|aseguraria)\b"
)

PATRON_NORMA_CITADA = re.compile(
    r"\b(Ley|Decreto\s+Supremo|Decreto\s+Legislativo|Decreto\s+de\s+Urgencia|"
    r"Resolucion\s+Suprema|Resolución\s+Suprema|Resolucion\s+Ministerial|Resolución\s+Ministerial|"
    r"Resolucion\s+Directoral|Resolución\s+Directoral|Resolucion\s+Jefatural|Resolución\s+Jefatural|"
    r"Decreto\s+de\s+Alcaldia|Decreto\s+de\s+Alcaldía|Ordenanza\s+Regional|Ordenanza\s+Municipal)\s+"
    r"(?:N[°ºo.]*\s*)?([0-9]{1,6}(?:[-/][0-9]{4}(?:[-/][A-Za-z0-9./]+)?)?)",
    re.IGNORECASE,
)


def _slugify(texto: str, max_len: int = 40) -> str:
    """Convierte una cadena en slug ASCII estable con guiones."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")
    limpio = re.sub(r"[^a-zA-Z0-9]+", "-", sin_tildes.lower()).strip("-")
    if len(limpio) > max_len:
        limpio = limpio[:max_len].rstrip("-")
    return limpio or "na"


def generar_id_estable(tipo: str, numero: str, anio: str, entidad: str) -> str:
    """Genera un identificador estable `tipo-numero-anio-entidad`."""
    slug_tipo = _slugify(tipo, max_len=28)
    slug_num = _slugify(numero, max_len=28)
    slug_anio = _slugify(anio, max_len=8)
    slug_ent = _slugify(entidad, max_len=36)
    return f"{slug_tipo}-{slug_num}-{slug_anio}-{slug_ent}"


def extraer_numero_y_anio(titulo_norma: str, fecha_iso: str = "") -> Tuple[str, str]:
    """Extrae el número oficial de norma y su año a partir del encabezado."""
    titulo = (titulo_norma or "").strip()
    m_num = re.search(r"N[°ºo.]*\s*([A-Za-z0-9\-/]+)", titulo, re.IGNORECASE)
    numero = m_num.group(1).strip("-/") if m_num else _slugify(titulo, max_len=20)
    m_anio = re.search(r"(19[89][0-9]|20[0-4][0-9])", numero)
    if m_anio:
        anio = m_anio.group(1)
    elif fecha_iso and re.match(r"^\d{4}", fecha_iso):
        anio = fecha_iso[:4]
    else:
        anio = "0000"
    return numero, anio


def contar_palabras(texto: Optional[str]) -> int:
    """Cuenta las palabras no vacías de un texto."""
    if not texto or not isinstance(texto, str):
        return 0
    return len([w for w in texto.strip().split() if w])


def _normalizar_para_busqueda(texto: str) -> str:
    """Normaliza espacios, tildes y puntuación leve para cotejo de citas."""
    norm = normalizar_texto(texto)
    norm = re.sub(r"[\"'“”«»()\[\].,;:°º\-/]", " ", norm)
    norm = re.sub(r"\s+", " ", norm).strip()
    return norm


def _contiene_cita_literal(cita: str, corpus_normalizado: str) -> bool:
    """Verifica que la cita normalizada aparezca textualmente en el corpus origen."""
    cita_norm = _normalizar_para_busqueda(cita)
    if not cita_norm or len(cita_norm) < 6:
        return False
    return cita_norm in corpus_normalizado


def _contiene_referencia_articulo(articulo: str, corpus_normalizado: str) -> bool:
    """Verifica que el artículo o sección referida exista en el texto de origen."""
    art_norm = _normalizar_para_busqueda(articulo)
    if not art_norm:
        return False
    if art_norm in corpus_normalizado:
        return True
    if art_norm in {"considerando", "considerandos"} and "considerando" in corpus_normalizado:
        return True
    if art_norm in {"visto", "vistos"} and "visto" in corpus_normalizado:
        return True
    if art_norm in {"sumilla", "articulo unico", "disposicion unica"} and (
        "articulo" in corpus_normalizado or "se resuelve" in corpus_normalizado or "decreta" in corpus_normalizado
    ):
        return True
    m_num = re.search(r"\b(\d+|unico|unica|primera|segunda|tercera|cuarta)\b", art_norm)
    if m_num:
        token = m_num.group(1)
        if re.search(rf"\b(?:articulo|art|numeral|disposicion)\s+{re.escape(token)}\b", corpus_normalizado):
            return True
    return False


def _detectar_juicios_prohibidos(texto: str) -> List[str]:
    """Devuelve la lista de palabras de juicio político/jurídico detectadas."""
    norm = _normalizar_para_busqueda(texto)
    tokens = set(norm.split())
    return sorted(tokens.intersection(PALABRAS_PROHIBIDAS_JUICIO))


def _validar_que_dispone(que_dispone: Any, errores: List[str]) -> None:
    if que_dispone is None:
        return
    if not isinstance(que_dispone, str):
        errores.append("'que_dispone' debe ser texto o null.")
        return
    if contar_palabras(que_dispone) > 120:
        errores.append(f"'que_dispone' excede 120 palabras ({contar_palabras(que_dispone)}).")
    juicios = _detectar_juicios_prohibidos(que_dispone)
    if juicios:
        errores.append(f"'que_dispone' contiene juicios prohibidos: {', '.join(juicios)}.")


def _validar_repercusiones(repercusiones: Any, corpus_norm: str, errores: List[str]) -> None:
    if not isinstance(repercusiones, list) or len(repercusiones) > 4:
        errores.append("'repercusiones_esperadas' debe ser una lista de 0 a 4 elementos.")
        return
    for idx, rep in enumerate(repercusiones, start=1):
        if not isinstance(rep, dict):
            errores.append(f"Repercusión #{idx} no es objeto JSON.")
            continue
        efecto = rep.get("efecto") or ""
        articulo = rep.get("articulo") or ""
        cita = rep.get("cita") or ""
        if not isinstance(efecto, str) or not efecto.strip():
            errores.append(f"Repercusión #{idx} carece de 'efecto'.")
            continue
        efecto_norm = normalizar_texto(efecto)
        if not MARCADORES_CONDICIONAL.search(efecto_norm):
            errores.append(f"Repercusión #{idx} no está redactada en modo condicional.")
        juicios = _detectar_juicios_prohibidos(efecto)
        if juicios:
            errores.append(f"Repercusión #{idx} incluye juicios prohibidos: {', '.join(juicios)}.")
        if contar_palabras(cita) == 0 or contar_palabras(cita) > 25:
            errores.append(f"Repercusión #{idx} requiere cita de 1 a 25 palabras.")
        elif not _contiene_cita_literal(cita, corpus_norm):
            errores.append(f"Repercusión #{idx}: cita no encontrada literalmente en texto fuente.")
        if not isinstance(articulo, str) or not _contiene_referencia_articulo(articulo, corpus_norm):
            errores.append(f"Repercusión #{idx}: artículo '{articulo}' no hallado en texto fuente.")


def _validar_politicas(
    politicas: Any, ids_catalogo: set, corpus_norm: str, errores: List[str]
) -> None:
    if not isinstance(politicas, list):
        errores.append("'politica_nacional' debe ser una lista.")
        return
    for idx, pol in enumerate(politicas, start=1):
        if not isinstance(pol, dict):
            errores.append(f"Política #{idx} no es objeto JSON.")
            continue
        pid = pol.get("id")
        tipo_al = pol.get("tipo_alineacion")
        if pid == "ninguna" or tipo_al == "ninguna":
            continue
        if pid not in ids_catalogo:
            errores.append(f"Política #{idx}: id '{pid}' no pertenece al catálogo oficial.")
            continue
        if tipo_al not in {"explicita", "explícita", "sugerida por IA"}:
            errores.append(f"Política #{idx}: tipo_alineacion inválido '{tipo_al}'.")
        cita = pol.get("cita") or ""
        articulo = pol.get("articulo") or ""
        if contar_palabras(cita) == 0 or contar_palabras(cita) > 25:
            errores.append(f"Política #{idx}: requiere cita verificable de 1 a 25 palabras.")
        elif not _contiene_cita_literal(cita, corpus_norm):
            errores.append(f"Política #{idx}: cita de alineación no hallada en texto fuente.")
        if not isinstance(articulo, str) or not _contiene_referencia_articulo(articulo, corpus_norm):
            errores.append(f"Política #{idx}: artículo '{articulo}' no hallado en texto fuente.")


def _validar_normas_citadas(normas_citadas: Any, corpus_norm: str, errores: List[str]) -> None:
    if not isinstance(normas_citadas, list):
        errores.append("'normas_citadas' debe ser una lista.")
        return
    for idx, nc in enumerate(normas_citadas, start=1):
        if not isinstance(nc, dict):
            errores.append(f"Norma citada #{idx} no es objeto JSON.")
            continue
        numero = str(nc.get("numero") or "").strip()
        if not numero:
            errores.append(f"Norma citada #{idx} sin 'numero'.")
            continue
        num_norm = _normalizar_para_busqueda(numero)
        tokens_clave = [t for t in num_norm.split() if any(ch.isdigit() for ch in t)]
        if not num_norm or (num_norm not in corpus_norm and not all(t in corpus_norm for t in tokens_clave)):
            errores.append(f"Norma citada #{idx}: número '{numero}' no hallado en texto fuente.")


def _validar_preguntas(preguntas: Any, errores: List[str]) -> None:
    if not isinstance(preguntas, list) or len(preguntas) > 3:
        errores.append("'preguntas_a_verificar' debe ser una lista de 0 a 3 elementos.")
        return
    for idx, preg in enumerate(preguntas, start=1):
        if not isinstance(preg, str) or not preg.strip():
            errores.append(f"Pregunta #{idx} vacía o no textual.")
            continue
        juicios = _detectar_juicios_prohibidos(preg)
        if juicios:
            errores.append(f"Pregunta #{idx} contiene juicios prohibidos: {', '.join(juicios)}.")


def verificar_salida_ia_contra_texto(
    salida_ia: Dict[str, Any],
    texto_origen: str,
    catalogo_politicas: List[Dict[str, Any]],
    sumilla: str = "",
) -> Tuple[bool, List[str]]:
    """Valida que la salida JSON de la IA cumpla fidelidad estricta al texto fuente."""
    errores: List[str] = []
    if not isinstance(salida_ia, dict):
        return False, ["La salida de IA no es un objeto JSON."]

    claves_req = {
        "que_dispone",
        "repercusiones_esperadas",
        "politica_nacional",
        "normas_citadas",
        "preguntas_a_verificar",
    }
    faltantes = sorted(claves_req - set(salida_ia.keys()))
    if faltantes:
        errores.append(f"Faltan campos requeridos: {', '.join(faltantes)}.")
        return False, errores

    corpus_norm = _normalizar_para_busqueda(f"{sumilla}\n{texto_origen}")
    ids_catalogo = {p["id"] for p in catalogo_politicas if p.get("id")}

    _validar_que_dispone(salida_ia.get("que_dispone"), errores)
    _validar_repercusiones(salida_ia.get("repercusiones_esperadas"), corpus_norm, errores)
    _validar_politicas(salida_ia.get("politica_nacional"), ids_catalogo, corpus_norm, errores)
    _validar_normas_citadas(salida_ia.get("normas_citadas"), corpus_norm, errores)
    _validar_preguntas(salida_ia.get("preguntas_a_verificar"), errores)

    return len(errores) == 0, errores


def extraer_normas_citadas_regex(
    texto: str, sumilla: str = "", excluir_numero: str = ""
) -> List[Dict[str, Optional[str]]]:
    """Extrae menciones explícitas de normas en el texto fuente sin depender de IA."""
    combinado = f"{sumilla}\n{texto}"
    vistas: set = set()
    resultados: List[Dict[str, Optional[str]]] = []
    norm_excluir = re.sub(r"[^a-z0-9]", "", (excluir_numero or "").lower())

    for match in PATRON_NORMA_CITADA.finditer(combinado):
        tipo_raw = re.sub(r"\s+", " ", match.group(1)).strip().title()
        numero = match.group(2).strip(".,;:-/")
        if not numero or len(resultados) >= 12:
            continue
        norm_key = re.sub(r"[^a-z0-9]", "", numero.lower())
        if norm_excluir and norm_key == norm_excluir:
            continue
        llave = (tipo_raw.lower(), norm_key)
        if llave in vistas:
            continue
        vistas.add(llave)
        m_anio = re.search(r"(19[89][0-9]|20[0-4][0-9])", numero)
        resultados.append(
            {
                "tipo": tipo_raw,
                "numero": numero,
                "anio": m_anio.group(1) if m_anio else None,
                "relacion_detectada": "mencionada en el texto",
                "url": None,
            }
        )
    return resultados

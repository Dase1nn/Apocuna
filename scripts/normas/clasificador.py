import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CRITERIOS_PATH = os.path.join(BASE_DIR, "data", "criterios_normas.json")
DEFAULT_POLITICAS_PATH = os.path.join(BASE_DIR, "data", "politicas_nacionales.json")
DEFAULT_POLITICAS_PROPUESTAS_PATH = os.path.join(
    BASE_DIR, "data", "politicas_nacionales_propuestas.json"
)


def normalizar_texto(texto: str) -> str:
    """Normaliza a minúsculas y remueve tildes/diacríticos para comparación robusta."""
    if not texto:
        return ""
    s = unicodedata.normalize("NFD", str(texto))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", s.lower()).strip()


def cargar_criterios(path: Optional[str] = None) -> Dict[str, Any]:
    """Carga data/criterios_normas.json."""
    target = path or DEFAULT_CRITERIOS_PATH
    with open(target, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_catalogo_politicas(
    incluir_propuestas: bool = True,
    path_aprobadas: Optional[str] = None,
    path_propuestas: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Carga políticas aprobadas y opcionalmente propuestas oficiales por verificar."""
    p_aprob = path_aprobadas or DEFAULT_POLITICAS_PATH
    p_prop = path_propuestas or DEFAULT_POLITICAS_PROPUESTAS_PATH
    catalogo: List[Dict[str, Any]] = []
    seen_ids = set()

    if os.path.exists(p_aprob):
        with open(p_aprob, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("id"):
                        catalogo.append(item)
                        seen_ids.add(item["id"])

    if incluir_propuestas and os.path.exists(p_prop):
        with open(p_prop, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("id") and item["id"] not in seen_ids:
                        catalogo.append(item)
                        seen_ids.add(item["id"])

    return catalogo


def sanitizar_texto_sin_nombres(texto: str) -> str:
    """Oculta eventuales nombres propios de personas en sumillas si aparecieran."""
    if not texto:
        return ""
    clean = str(texto)
    patterns = [
        (
            r"\b([Cc]iudadan[oa]\s+(?:peruano|extranjero|de\s+nacionalidad\s+peruana)\s+)[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]{4,60}(?=[,;.]|$|\s+(?:para|formulada|requerid|identificad))",
            r"\1[DATO DE PERSONA OMITIDO]",
        ),
        (
            r"\b(?:[Ss]eñor(?:a)?|[Dd]on|[Dd]oña|[Aa]bogad[oa]|[Mm]ag[ií]ster|[Dd]octor(?:a)?|[Ii]ngenier[oa])\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]+){1,4}",
            "[DATO DE PERSONA OMITIDO]",
        ),
        (
            r"\b((?:[Dd]esignan|[Nn]ombran)\s+a\s+)[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\s]{4,60}(?=\s+(?:en\s+el|como|$|[,;.]))",
            r"\1[DATO DE PERSONA OMITIDO]",
        ),
        (
            r"(?i)\bD\.?N\.?I\.?\s*(?:N\.?[º°]?\s*)?\d{8}\b",
            "DNI [OMITIDO]",
        ),
    ]
    for pat, repl in patterns:
        clean = re.sub(pat, repl, clean)
    return re.sub(r"\s+", " ", clean).strip()


def extraer_segmentos_norma(sumilla: str, texto_completo: str = "") -> List[Tuple[str, str]]:
    """Divide la norma en segmentos etiquetados por sección/artículo."""
    segmentos: List[Tuple[str, str]] = []
    if sumilla:
        segmentos.append(("Sumilla", re.sub(r"\s+", " ", sumilla).strip()))

    if not texto_completo:
        return segmentos

    raw_lines = [re.sub(r"\s+", " ", ln).strip() for ln in str(texto_completo).splitlines()]
    raw_lines = [ln for ln in raw_lines if ln]

    ubicacion_actual = "Cuerpo / Exposición"
    patron_articulo = re.compile(
        r"^(Artículo\s+(?:\d+|Único|[A-Za-zÁÉÍÓÚáéíóú]+)\b|CONSIDERANDO\s*:|VISTO\s*:|DISPOSICI[ÓO]N\s+COMPLEMENTARIA)",
        re.IGNORECASE,
    )
    for ln in raw_lines:
        m = patron_articulo.match(ln)
        if m:
            tag = m.group(1).rstrip(":").strip()
            if tag.lower().startswith("artículo"):
                ubicacion_actual = tag
            elif "considerando" in tag.lower():
                ubicacion_actual = "Considerando"
            elif "visto" in tag.lower():
                ubicacion_actual = "Visto"
            else:
                ubicacion_actual = tag
        segmentos.append((ubicacion_actual, ln))

    return segmentos


def _recortar_extracto_25_palabras(texto_bloque: str, inicio: int, fin: int, max_palabras: int = 25) -> str:
    """Construye un extracto literal continuo de máximo 25 palabras alrededor de [inicio, fin]."""
    palabras_spans = [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"\S+", texto_bloque)]
    if not palabras_spans:
        return ""

    idx_ini = 0
    idx_fin = len(palabras_spans) - 1
    for i, (s, e, _) in enumerate(palabras_spans):
        if s <= inicio < e or s >= inicio:
            idx_ini = i
            break
    for i in range(idx_ini, len(palabras_spans)):
        s, e, _ = palabras_spans[i]
        idx_fin = i
        if e >= fin:
            break

    span_len = idx_fin - idx_ini + 1
    if span_len >= max_palabras:
        seleccion = palabras_spans[idx_ini : idx_ini + max_palabras]
    else:
        margen = max_palabras - span_len
        left = min(idx_ini, margen // 3)
        start_w = idx_ini - left
        end_w = min(len(palabras_spans), start_w + max_palabras)
        if end_w - start_w < max_palabras and start_w > 0:
            start_w = max(0, end_w - max_palabras)
        seleccion = palabras_spans[start_w:end_w]

    return " ".join(w for _, _, w in seleccion)


def detectar_alineacion_explicita(
    sumilla: str,
    texto_completo: str = "",
    catalogo: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Detecta menciones explícitas a políticas nacionales, de Estado, PGG o PEDN.

    Devuelve lista de dicts con id, nombre, tipo_alineacion ('explícita'),
    articulo y extracto literal de máximo 25 palabras.
    """
    catalogo = catalogo if catalogo is not None else cargar_catalogo_politicas(incluir_propuestas=True)
    segmentos = extraer_segmentos_norma(sumilla, texto_completo)
    hallazgos: List[Dict[str, Any]] = []
    vistos = set()

    # 1. Coincidencias exactas/alias contra catálogo oficial
    for pol in catalogo:
        pol_id = pol.get("id", "no_catalogada")
        pol_nombre = pol.get("nombre", "")
        terminos = [pol_nombre] + list(pol.get("alias") or [])
        norma_aprob = pol.get("norma_aprobacion")
        if norma_aprob:
            terminos.append(norma_aprob)
        terminos = [t for t in dict.fromkeys(terminos) if t and len(t.strip()) >= 6]

        encontrado_pol = False
        for ubicacion, bloque in segmentos:
            if encontrado_pol:
                break
            bloque_norm = normalizar_texto(bloque)
            for term in terminos:
                term_norm = normalizar_texto(term)
                if len(term_norm) < 6:
                    continue
                pos = bloque_norm.find(term_norm)
                if pos != -1:
                    extracto = _recortar_extracto_25_palabras(bloque, pos, pos + len(term_norm), max_palabras=25)
                    key = (pol_id, ubicacion)
                    if key not in vistos and extracto:
                        vistos.add(key)
                        hallazgos.append(
                            {
                                "id": pol_id,
                                "nombre": pol_nombre,
                                "tipo_alineacion": "explícita",
                                "articulo": ubicacion,
                                "extracto": extracto,
                            }
                        )
                        encontrado_pol = True
                        break

    # 2. Patrón textual abierto ("Política Nacional ...", "Plan Estratégico de Desarrollo Nacional ...", etc.)
    patron_abierto = re.compile(
        r"(Política\s+Nacional\s+(?:Multisectorial\s+)?(?:de|del|para|contra)\s+[^,;\.\(\)\n]{4,85}"
        r"|Plan\s+Estratégico\s+de\s+Desarrollo\s+Nacional[^,;\.\(\)\n]{0,45}"
        r"|Política\s+General\s+de\s+Gobierno[^,;\.\(\)\n]{0,45}"
        r"|Política\s+de\s+Estado\s+(?:N[°º]\s*\d+|sobre\s+[^,;\.\(\)\n]{4,60}))",
        re.IGNORECASE,
    )
    for ubicacion, bloque in segmentos:
        for m in patron_abierto.finditer(bloque):
            frase = re.sub(r"\s+", " ", m.group(1)).strip()
            frase_norm = normalizar_texto(frase)
            # Evitar duplicar si ya hizo match exacto con el catálogo
            ya_en_catalogo = any(
                normalizar_texto(h["nombre"]) in frase_norm or frase_norm in normalizar_texto(h["nombre"])
                for h in hallazgos
            )
            if ya_en_catalogo:
                continue
            extracto = _recortar_extracto_25_palabras(bloque, m.start(1), m.end(1), max_palabras=25)
            key = ("patron:" + frase_norm[:60], ubicacion)
            if key not in vistos and extracto:
                vistos.add(key)
                hallazgos.append(
                    {
                        "id": "no_catalogada",
                        "nombre": frase,
                        "tipo_alineacion": "explícita",
                        "articulo": ubicacion,
                        "extracto": extracto,
                    }
                )

    return hallazgos


def _puntaje_eje(
    eje_cfg: Dict[str, Any],
    sumilla_norm: str,
    texto_norm: str,
    entidad_norm: str,
) -> Tuple[float, Optional[str], List[str]]:
    """Calcula el puntaje del eje y determina el subtema ganador."""
    subtemas = eje_cfg.get("subtemas", [])
    mejor_score = 0.0
    mejor_subtema = None
    mejores_hits: List[str] = []
    total_eje = 0.0

    for sub in subtemas:
        score_sub = 0.0
        hits_sub: List[str] = []
        for kw in sub.get("palabras_clave", []):
            kw_norm = normalizar_texto(kw)
            if not kw_norm:
                continue
            patron = r"(?<!\w)" + re.escape(kw_norm) + r"(?!\w)"
            if re.search(patron, sumilla_norm):
                score_sub += 3.0
                hits_sub.append(kw)
            elif texto_norm and re.search(patron, texto_norm[:6000]):
                score_sub += 1.0
                hits_sub.append(f"{kw} (texto)")

        for sec in sub.get("sectores_asociados", []):
            sec_norm = normalizar_texto(sec)
            if sec_norm and sec_norm == entidad_norm:
                score_sub += 0.5
                hits_sub.append(f"sector:{sec}")

        if score_sub >= 1.0:
            total_eje += score_sub
        if score_sub > mejor_score:
            mejor_score = score_sub
            mejor_subtema = sub.get("nombre")
            mejores_hits = hits_sub

    # Si solo hubo match por sector (0.5) sin palabra clave temática, no forzar eje
    if mejor_score < 1.0:
        return 0.0, None, []

    return total_eje, mejor_subtema, mejores_hits


def clasificar_norma(
    item: Dict[str, Any],
    criterios: Optional[Dict[str, Any]] = None,
    catalogo: Optional[List[Dict[str, Any]]] = None,
    texto_completo: str = "",
) -> Dict[str, Any]:
    """Clasifica una norma sin IA aplicando reglas de exclusión, prioridad y ejes Polity/Policy."""
    criterios = criterios or cargar_criterios()
    catalogo = catalogo if catalogo is not None else cargar_catalogo_politicas(incluir_propuestas=True)

    tipo = (item.get("tipoDispositivo") or item.get("tipo") or "").strip()
    numero = (item.get("numeroDispositivo") or item.get("numero") or "").strip()
    entidad = (item.get("distributor") or item.get("entidad") or "").strip()
    sumilla = (item.get("sumilla") or item.get("titulo") or "").strip()
    op = (item.get("op") or "").strip()

    sumilla_lower = sumilla.lower()
    sumilla_norm = normalizar_texto(sumilla)
    entidad_norm = normalizar_texto(entidad)
    tipo_upper = tipo.upper()
    texto_norm = normalizar_texto(texto_completo)

    # 1. Validar tipo de norma si tipos_norma_incluidos está poblado
    tipos_incluidos = [t.upper() for t in criterios.get("tipos_norma_incluidos", [])]
    if tipos_incluidos and tipo_upper and not any(t in tipo_upper for t in tipos_incluidos):
        return {
            "op": op,
            "tipo": tipo,
            "numero": numero,
            "entidad": entidad,
            "sumilla_segura": sanitizar_texto_sin_nombres(sumilla),
            "decision": "excluida",
            "prioridad": "excluida",
            "motivo": f"Tipo de dispositivo fuera de catálogo ({tipo})",
            "eje": None,
            "subtema": None,
            "alineacion": [],
        }

    # 2. Reglas de exclusión
    for regla in criterios.get("patrones_exclusion", []):
        for pat in regla.get("patrones_regex", []):
            if re.search(pat, sumilla_lower, re.IGNORECASE):
                return {
                    "op": op,
                    "tipo": tipo,
                    "numero": numero,
                    "entidad": entidad,
                    "sumilla_segura": sanitizar_texto_sin_nombres(sumilla),
                    "decision": "excluida",
                    "prioridad": "excluida",
                    "motivo": regla.get("motivo", f"Excluida por regla {regla.get('id')}"),
                    "regla_exclusion": regla.get("id"),
                    "eje": None,
                    "subtema": None,
                    "alineacion": [],
                }

    # 3. Transferencias de partidas / financieras -> NO excluidas, marcadas "baja prioridad"
    reglas_esp = criterios.get("reglas_prioridad_especial", {})
    transf_cfg = reglas_esp.get("transferencias_partidas", {})
    for pat in transf_cfg.get("patrones_regex", []):
        if re.search(pat, sumilla_lower, re.IGNORECASE):
            alineacion = detectar_alineacion_explicita(sumilla, texto_completo, catalogo)
            return {
                "op": op,
                "tipo": tipo,
                "numero": numero,
                "entidad": entidad,
                "sumilla_segura": sanitizar_texto_sin_nombres(sumilla),
                "decision": "incluida",
                "prioridad": transf_cfg.get("prioridad", "baja prioridad"),
                "motivo": transf_cfg.get(
                    "motivo",
                    "Incluida con baja prioridad: transferencia de partidas/financiera",
                ),
                "eje": transf_cfg.get("eje_forzado", "policy"),
                "subtema": transf_cfg.get(
                    "subtema_forzado", "Presupuesto, Hacienda Pública y Transferencias"
                ),
                "alineacion": alineacion,
            }

    ent_prioritarias = {normalizar_texto(e) for e in criterios.get("entidades_prioritarias", [])}
    prioridad = "alta" if entidad_norm in ent_prioritarias else "normal"

    # 3b. Reglas prioritarias Polity para instrumentos internos de gestión administrativa
    for regla_pol in reglas_esp.get("instrumentos_gestion_polity", []):
        for pat in regla_pol.get("patrones", []):
            pat_norm = normalizar_texto(pat)
            if pat_norm and re.search(r"(?<!\w)" + re.escape(pat_norm) + r"(?!\w)", sumilla_norm):
                alineacion = detectar_alineacion_explicita(sumilla, texto_completo, catalogo)
                return {
                    "op": op,
                    "tipo": tipo,
                    "numero": numero,
                    "entidad": entidad,
                    "sumilla_segura": sanitizar_texto_sin_nombres(sumilla),
                    "decision": "incluida",
                    "prioridad": prioridad,
                    "motivo": f"Regla Polity prioritaria (instrumento de gestión institucional): {pat}",
                    "eje": "polity",
                    "subtema": regla_pol.get("subtema", "Sistemas Administrativos, Planeamiento y Modernización"),
                    "alineacion": alineacion,
                }

    # 4. Scoring Polity vs Policy
    ejes_cfg = criterios.get("ejes", {})
    score_polity, sub_polity, hits_polity = _puntaje_eje(
        ejes_cfg.get("polity", {}), sumilla_norm, texto_norm, entidad_norm
    )
    score_policy, sub_policy, hits_policy = _puntaje_eje(
        ejes_cfg.get("policy", {}), sumilla_norm, texto_norm, entidad_norm
    )

    if score_polity > 0 and score_policy > 0 and (
        min(score_polity, score_policy) / max(score_polity, score_policy) >= 0.6
    ):
        eje = "mixto"
        subtema = f"{sub_polity} / {sub_policy}"
        motivo = f"Reglas mixtas Polity ({', '.join(hits_polity[:3])}) y Policy ({', '.join(hits_policy[:3])})"
    elif score_polity > score_policy and score_polity > 0:
        eje = "polity"
        subtema = sub_polity
        motivo = f"Reglas Polity: {', '.join(hits_polity[:4])}"
    elif score_policy > score_polity and score_policy > 0:
        eje = "policy"
        subtema = sub_policy
        motivo = f"Reglas Policy: {', '.join(hits_policy[:4])}"
    elif score_polity > 0:
        eje = "polity"
        subtema = sub_polity
        motivo = f"Reglas Polity: {', '.join(hits_polity[:4])}"
    else:
        eje = "otro"
        subtema = "General / Otros"
        motivo = "Incluida por no caer en exclusiones; sin coincidencia directa de palabras clave"

    alineacion = detectar_alineacion_explicita(sumilla, texto_completo, catalogo)

    return {
        "op": op,
        "tipo": tipo,
        "numero": numero,
        "entidad": entidad,
        "sumilla_segura": sanitizar_texto_sin_nombres(sumilla),
        "decision": "incluida",
        "prioridad": prioridad,
        "motivo": motivo,
        "eje": eje,
        "subtema": subtema,
        "alineacion": alineacion,
    }

"""Orquestador diario de Normas Legales (El Peruano) con radar, verificación y fail-safe."""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

import config
from scripts.normas.clasificador import (
    cargar_catalogo_politicas,
    cargar_criterios,
    clasificar_norma,
)
from scripts.normas.elperuano_client import listar_normas_fecha, obtener_texto_norma
from scripts.normas.generador_ia import (
    ErrorVerificacionIA,
    GestorLlamadasIA,
    generar_y_verificar_ia,
)
from scripts.normas.verificador_ia import (
    extraer_normas_citadas_regex,
    extraer_numero_y_anio,
    generar_id_estable,
)


TZ_LIMA = timezone(timedelta(hours=-5))
DIR_DATA = os.path.join(RAIZ_PROYECTO, "data")
DIR_GENERATED = os.path.join(DIR_DATA, "generated")
DIR_NORMAS_OFICIALES = os.path.join(DIR_GENERATED, "normas_oficiales")
DIR_COMENTADAS = os.path.join(DIR_DATA, "normas_comentadas")
RUTA_ESTADO = os.path.join(DIR_GENERATED, "estado.json")


def _ahora_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fecha_lima_hoy() -> str:
    return datetime.now(TZ_LIMA).strftime("%Y%m%d")


def _formatear_fecha_iso_lima(fecha_yyyymmdd: str) -> str:
    dt = datetime.strptime(fecha_yyyymmdd, "%Y%m%d").replace(tzinfo=TZ_LIMA)
    return dt.isoformat()


def _formatear_fecha_corta(fecha_yyyymmdd: str) -> str:
    return f"{fecha_yyyymmdd[:4]}-{fecha_yyyymmdd[4:6]}-{fecha_yyyymmdd[6:8]}"


def _leer_json(ruta: str, default: Any) -> Any:
    if not os.path.exists(ruta):
        return default
    try:
        with open(ruta, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def _escribir_json_atomico(ruta: str, datos: Any) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    temporal = f"{ruta}.tmp"
    with open(temporal, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(temporal, ruta)


def _combinar_politicas(
    alineacion_reglas: List[Dict[str, Any]],
    politicas_ia: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Normaliza la lista `politica_nacional` uniendo reglas explícitas y sugerencias IA."""
    combinadas: List[Dict[str, Any]] = []
    vistas: set = set()

    for al in alineacion_reglas or []:
        pid = al.get("id") or "no_catalogada"
        key = (pid, al.get("articulo") or "")
        if key in vistas:
            continue
        vistas.add(key)
        combinadas.append(
            {
                "id": pid,
                "nombre": al.get("nombre"),
                "tipo_alineacion": al.get("tipo_alineacion", "explícita"),
                "evidencia": {
                    "articulo": al.get("articulo"),
                    "cita": al.get("extracto"),
                },
            }
        )

    for pol in politicas_ia or []:
        pid = pol.get("id")
        tipo_al = pol.get("tipo_alineacion")
        if not pid or pid == "ninguna" or tipo_al == "ninguna":
            continue
        if any(c.get("id") == pid for c in combinadas):
            continue
        combinadas.append(
            {
                "id": pid,
                "tipo_alineacion": tipo_al or "sugerida por IA",
                "evidencia": {
                    "articulo": pol.get("articulo"),
                    "cita": pol.get("cita"),
                },
            }
        )

    if not combinadas:
        return [
            {
                "id": "ninguna",
                "tipo_alineacion": "ninguna",
                "evidencia": None,
            }
        ]
    return combinadas


def _combinar_normas_citadas(
    citadas_regex: List[Dict[str, Any]],
    citadas_ia: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Une normas detectadas por regex e IA evitando duplicados."""
    salida: List[Dict[str, Any]] = []
    vistas: set = set()
    for fuente in (citadas_ia or []) + (citadas_regex or []):
        tipo = (fuente.get("tipo") or "").strip()
        numero = (fuente.get("numero") or "").strip()
        if not numero:
            continue
        clave = f"{tipo.lower()}::{numero.lower()}"
        if clave in vistas:
            continue
        vistas.add(clave)
        salida.append(
            {
                "tipo": tipo or None,
                "numero": numero,
                "anio": fuente.get("anio"),
                "relacion_detectada": fuente.get("relacion_detectada") or "mencionada en el texto",
                "url": fuente.get("url"),
            }
        )
    return salida[:12]


def _construir_ficha(
    norma_id: str,
    item: Dict[str, Any],
    res_clas: Dict[str, Any],
    sha256_texto: str,
    url_oficial: str,
    fecha_yyyymmdd: str,
    citadas_regex: List[Dict[str, Any]],
    salida_ia_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Ensambla la ficha JSON final cumpliendo el esquema de Etapa 3."""
    numero, anio = extraer_numero_y_anio(res_clas.get("numero") or "", fecha_yyyymmdd)
    analisis_ia = salida_ia_info["analisis"] if salida_ia_info else {}
    tiene_revision_humana = os.path.exists(os.path.join(DIR_COMENTADAS, f"{norma_id}.md"))

    if tiene_revision_humana:
        estado = "revisado por persona"
    elif salida_ia_info:
        estado = "borrador IA"
    else:
        estado = "radar sin IA"

    politica_nacional = _combinar_politicas(
        res_clas.get("alineacion", []),
        analisis_ia.get("politica_nacional"),
    )
    normas_citadas = _combinar_normas_citadas(
        citadas_regex,
        analisis_ia.get("normas_citadas"),
    )

    return {
        "id": norma_id,
        "op": res_clas.get("op"),
        "tipo": res_clas.get("tipo") or item.get("tipoDispositivo"),
        "numero": numero,
        "numero_raw": res_clas.get("numero") or item.get("numeroDispositivo"),
        "anio": anio,
        "entidad": res_clas.get("entidad") or item.get("distributor"),
        "fecha": _formatear_fecha_iso_lima(fecha_yyyymmdd),
        "fecha_publicacion": _formatear_fecha_corta(fecha_yyyymmdd),
        "sumilla": res_clas.get("sumilla_segura") or "",
        "url_oficial": url_oficial,
        "eje": res_clas.get("eje"),
        "subtema": res_clas.get("subtema"),
        "prioridad": res_clas.get("prioridad"),
        "motivo_clasificacion": res_clas.get("motivo"),
        "politica_nacional": politica_nacional,
        "normas_citadas": normas_citadas,
        "que_dispone": analisis_ia.get("que_dispone") if salida_ia_info else None,
        "repercusiones_esperadas": (
            analisis_ia.get("repercusiones_esperadas", []) if salida_ia_info else []
        ),
        "preguntas_a_verificar": (
            analisis_ia.get("preguntas_a_verificar", []) if salida_ia_info else []
        ),
        "estado": estado,
        "modelo": salida_ia_info.get("modelo") if salida_ia_info else None,
        "fecha_ia": _ahora_utc_iso() if salida_ia_info else None,
        "version_instrucciones": (
            salida_ia_info.get("version_instrucciones") if salida_ia_info else None
        ),
        "hash_texto": sha256_texto,
        "revision_humana_archivo": (
            f"data/normas_comentadas/{norma_id}.md" if tiene_revision_humana else None
        ),
    }


def _registrar_estado(
    estado_actual: Dict[str, Any],
    payload_normas: Dict[str, Any],
) -> None:
    """Guarda el estado operativo del pipeline en data/generated/estado.json."""
    if not isinstance(estado_actual, dict):
        estado_actual = {}
    fuentes = estado_actual.setdefault("fuentes", {})
    fuentes["normas_diario"] = payload_normas
    estado_actual["last_run"] = _ahora_utc_iso()
    _escribir_json_atomico(RUTA_ESTADO, estado_actual)


def ejecutar_pipeline_normas(
    fecha_yyyymmdd: str,
    tope: Optional[int] = None,
    usar_ia: Optional[bool] = None,
    simular_fallo_ia: bool = False,
    forzar: bool = False,
    cache_listado: Optional[str] = None,
    cliente_ia: Optional[Any] = None,
) -> Dict[str, Any]:
    """Ejecuta recolección, filtrado, obtención de texto en memoria, IA opcional y publicación atómica."""
    inicio_ts = time.monotonic()
    ia_activa = bool(getattr(config, "NORMAS_IA_HABILITADA", False) if usar_ia is None else usar_ia)
    tope_items = int(tope if tope is not None else getattr(config, "NORMAS_TOPE_EJECUCION", 80))

    estado = _leer_json(RUTA_ESTADO, default={"fuentes": {}})
    mes_str = f"{fecha_yyyymmdd[:4]}-{fecha_yyyymmdd[4:6]}"
    ruta_indice_mes = os.path.join(DIR_NORMAS_OFICIALES, f"{mes_str}.json")
    indice_previo = _leer_json(ruta_indice_mes, default={"mes": mes_str, "normas": []})
    normas_previas: List[Dict[str, Any]] = indice_previo.get("normas", [])
    mapa_previo: Dict[str, Dict[str, Any]] = {
        n["id"]: n for n in normas_previas if isinstance(n, dict) and n.get("id")
    }

    criterios = cargar_criterios()
    catalogo = cargar_catalogo_politicas(incluir_propuestas=True)
    gestor_ia = GestorLlamadasIA()

    try:
        if cache_listado:
            raw_cache = _leer_json(cache_listado, default={})
            listado_nl = (raw_cache.get("NL") or [])[:tope_items]
            meta_listado = {
                "fecha": fecha_yyyymmdd,
                "fuente": "cache_local",
                "total_reportado": len(listado_nl),
            }
        else:
            listado_nl, meta_listado = listar_normas_fecha(
                fecha_yyyymmdd, tipo_publicacion="NL", max_items=tope_items
            )

        nuevas_por_id: Dict[str, Dict[str, Any]] = {}
        conteo = {
            "total_listado": len(listado_nl),
            "excluidas_reglas": 0,
            "incluidas_radar": 0,
            "omitidas_idempotentes": 0,
            "revisadas_por_persona": 0,
        }

        for item in listado_nl:
            pre_clas = clasificar_norma(item, criterios=criterios, catalogo=catalogo, texto_completo="")
            if pre_clas["decision"] != "incluida":
                conteo["excluidas_reglas"] += 1
                continue

            conteo["incluidas_radar"] += 1
            numero, anio = extraer_numero_y_anio(pre_clas.get("numero") or "", fecha_yyyymmdd)
            norma_id = generar_id_estable(
                pre_clas.get("tipo") or "",
                numero,
                anio,
                pre_clas.get("entidad") or "",
            )

            existente = mapa_previo.get(norma_id)
            tiene_md = os.path.exists(os.path.join(DIR_COMENTADAS, f"{norma_id}.md"))
            if existente and not forzar:
                ya_tiene_ia = existente.get("estado") in {"borrador IA", "revisado por persona"}
                if not ia_activa or ya_tiene_ia:
                    if tiene_md and existente.get("estado") != "revisado por persona":
                        existente["estado"] = "revisado por persona"
                        existente["revision_humana_archivo"] = f"data/normas_comentadas/{norma_id}.md"
                    elif not tiene_md and existente.get("revision_humana_archivo"):
                        existente["revision_humana_archivo"] = None
                    conteo["omitidas_idempotentes"] += 1
                    continue

            op = pre_clas.get("op")
            if not op:
                continue

            _, texto_limpio, sha256_texto, url_oficial = obtener_texto_norma(op)
            res_full = clasificar_norma(
                item, criterios=criterios, catalogo=catalogo, texto_completo=texto_limpio
            )
            citadas_regex = extraer_normas_citadas_regex(
                texto_limpio, sumilla=res_full.get("sumilla_segura") or "", excluir_numero=numero
            )

            if simular_fallo_ia:
                raise ErrorVerificacionIA(
                    f"Fallo simulado de verificación IA en ficha '{norma_id}': "
                    "cita o número de norma inexistente en el texto de origen."
                )

            salida_ia_info = None
            if ia_activa and gestor_ia.puede_procesar_norma():
                meta_ficha = {
                    "tipo": res_full.get("tipo"),
                    "numero": res_full.get("numero"),
                    "entidad": res_full.get("entidad"),
                    "fecha": _formatear_fecha_corta(fecha_yyyymmdd),
                    "sumilla": res_full.get("sumilla_segura"),
                }
                salida_ia_info = generar_y_verificar_ia(
                    meta_ficha,
                    texto_limpio,
                    catalogo,
                    gestor=gestor_ia,
                    cliente=cliente_ia,
                )

            ficha = _construir_ficha(
                norma_id=norma_id,
                item=item,
                res_clas=res_full,
                sha256_texto=sha256_texto,
                url_oficial=url_oficial,
                fecha_yyyymmdd=fecha_yyyymmdd,
                citadas_regex=citadas_regex,
                salida_ia_info=salida_ia_info,
            )
            nuevas_por_id[norma_id] = ficha

        # Sincronizar overrides de revisión humana para todo el mes antes de publicar
        mapa_final = {**mapa_previo, **nuevas_por_id}
        for nid, ficha in mapa_final.items():
            ruta_md = os.path.join(DIR_COMENTADAS, f"{nid}.md")
            if os.path.exists(ruta_md):
                ficha["estado"] = "revisado por persona"
                ficha["revision_humana_archivo"] = f"data/normas_comentadas/{nid}.md"
                conteo["revisadas_por_persona"] += 1

        lista_ordenada = sorted(
            mapa_final.values(),
            key=lambda x: (x.get("fecha_publicacion") or "", x.get("op") or ""),
            reverse=True,
        )

        # Publicación atómica únicamente si toda la corrida y verificaciones fueron exitosas
        indice_nuevo = {
            "mes": mes_str,
            "actualizado_en": _ahora_utc_iso(),
            "total_normas": len(lista_ordenada),
            "normas": lista_ordenada,
        }
        _escribir_json_atomico(ruta_indice_mes, indice_nuevo)

        duracion_seg = round(time.monotonic() - inicio_ts, 2)
        payload_ok = {
            "last_success": _ahora_utc_iso(),
            "ultimo_intento": _ahora_utc_iso(),
            "ultimo_estado": "ok",
            "publicado": True,
            "fecha_objetivo": _formatear_fecha_corta(fecha_yyyymmdd),
            "archivo_indice": f"data/generated/normas_oficiales/{mes_str}.json",
            "listado": meta_listado,
            "conteo": {
                **conteo,
                "publicadas_nuevas": len(nuevas_por_id),
                "total_mes": len(lista_ordenada),
            },
            "ia": {
                "habilitada": ia_activa,
                "modelo": getattr(config, "GEMINI_MODELO_NORMAS", None),
                "version_instrucciones": getattr(config, "NORMAS_PROMPT_VERSION", None),
                **gestor_ia.resumen_consumo(),
            },
            "duracion_seg": duracion_seg,
            "errores": [],
        }
        _registrar_estado(estado, payload_ok)
        return payload_ok

    except Exception as exc:
        duracion_seg = round(time.monotonic() - inicio_ts, 2)
        previo_normas = estado.get("fuentes", {}).get("normas_diario", {})
        mensaje_err = f"{type(exc).__name__}: {exc}"
        payload_err = {
            "last_success": previo_normas.get("last_success"),
            "ultimo_intento": _ahora_utc_iso(),
            "ultimo_estado": "error",
            "publicado": False,
            "fecha_objetivo": _formatear_fecha_corta(fecha_yyyymmdd),
            "ia": {
                "habilitada": ia_activa,
                **gestor_ia.resumen_consumo(),
            },
            "duracion_seg": duracion_seg,
            "errores": [mensaje_err],
        }
        _registrar_estado(estado, payload_err)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline diario idempotente para Normas Legales de El Peruano."
    )
    parser.add_argument(
        "--fecha",
        default=_fecha_lima_hoy(),
        help="Fecha objetivo AAAAMMDD en zona America/Lima (por defecto hoy).",
    )
    parser.add_argument("--tope", type=int, default=None, help="Tope máximo de normas del listado.")
    parser.add_argument("--con-ia", action="store_true", help="Fuerza habilitar análisis IA.")
    parser.add_argument("--sin-ia", action="store_true", help="Fuerza deshabilitar análisis IA.")
    parser.add_argument(
        "--simular-fallo-ia",
        action="store_true",
        help="Simula fallo de verificación IA para probar bloqueo de publicación.",
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Reprocesa normas ya existentes en el índice mensual.",
    )
    parser.add_argument(
        "--cache-listado",
        default=None,
        help="Ruta opcional a caché JSON de listado (solo pruebas locales).",
    )
    args = parser.parse_args()

    usar_ia: Optional[bool] = None
    if args.con_ia:
        usar_ia = True
    elif args.sin_ia:
        usar_ia = False

    try:
        resumen = ejecutar_pipeline_normas(
            fecha_yyyymmdd=args.fecha,
            tope=args.tope,
            usar_ia=usar_ia,
            simular_fallo_ia=args.simular_fallo_ia,
            forzar=args.forzar,
            cache_listado=args.cache_listado,
        )
        print(json.dumps(resumen, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"[ERROR] Publicación abortada de forma segura: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

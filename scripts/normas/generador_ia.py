"""Cliente Gemini (SDK oficial google-genai) con control de topes, reintentos y verificación."""

import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import config
from scripts.normas.clasificador import sanitizar_texto_sin_nombres
from scripts.normas.verificador_ia import verificar_salida_ia_contra_texto


class ErrorVerificacionIA(RuntimeError):
    """Error bloqueante al generar o verificar análisis con IA; impide publicar fichas."""


class GestorLlamadasIA:
    """Controla el tope diario de normas y llamadas al modelo Gemini."""

    def __init__(
        self,
        tope_normas: Optional[int] = None,
        tope_llamadas: Optional[int] = None,
        max_reintentos: Optional[int] = None,
    ) -> None:
        self.tope_normas = (
            config.NORMAS_TOPE_DIARIO_IA if tope_normas is None else max(0, int(tope_normas))
        )
        self.tope_llamadas = (
            config.NORMAS_TOPE_LLAMADAS_IA if tope_llamadas is None else max(0, int(tope_llamadas))
        )
        self.max_reintentos = (
            config.NORMAS_MAX_REINTENTOS_IA if max_reintentos is None else max(1, int(max_reintentos))
        )
        self.normas_procesadas = 0
        self.llamadas_realizadas = 0
        self.tokens_entrada = 0
        self.tokens_salida = 0

    def puede_procesar_norma(self) -> bool:
        """Indica si aún hay cupo diario de normas y llamadas disponible."""
        return (
            self.normas_procesadas < self.tope_normas
            and self.llamadas_realizadas < self.tope_llamadas
        )

    def resumen_consumo(self) -> Dict[str, int]:
        """Devuelve métricas agregadas de consumo sin credenciales."""
        return {
            "normas_ia_procesadas": self.normas_procesadas,
            "llamadas_ia_realizadas": self.llamadas_realizadas,
            "tokens_entrada": self.tokens_entrada,
            "tokens_salida": self.tokens_salida,
        }


def cargar_instrucciones_prompt(version: Optional[str] = None) -> str:
    """Lee el archivo Markdown versionado de instrucciones en scripts/prompts/."""
    ver = version or getattr(config, "NORMAS_PROMPT_VERSION", "norma_v1")
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta = os.path.join(raiz, "prompts", f"{ver}.md")
    with open(ruta, "r", encoding="utf-8") as fh:
        return fh.read()


def _limpiar_json_crudo(texto: str) -> str:
    """Elimina envoltorios Markdown opcionales alrededor de un JSON."""
    limpio = (texto or "").strip()
    limpio = re.sub(r"^```(?:json)?\s*", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\s*```$", "", limpio)
    return limpio.strip()


def _construir_prompt_usuario(
    ficha_meta: Dict[str, Any],
    texto_origen: str,
    catalogo_politicas: List[Dict[str, Any]],
) -> str:
    """Construye la entrada del usuario sanitizada y acotada en longitud."""
    catalogo_compacto = [
        {
            "id": p.get("id"),
            "nombre": p.get("nombre"),
            "tipo": p.get("tipo"),
        }
        for p in catalogo_politicas
        if p.get("id")
    ]
    texto_limpio = sanitizar_texto_sin_nombres(texto_origen)[:28000]
    cabecera = {
        "tipo": ficha_meta.get("tipo"),
        "numero": ficha_meta.get("numero"),
        "entidad": ficha_meta.get("entidad"),
        "fecha": ficha_meta.get("fecha"),
        "sumilla": sanitizar_texto_sin_nombres(ficha_meta.get("sumilla") or ""),
    }
    return (
        "CATÁLOGO OFICIAL DE POLÍTICAS (usa solo estos ids):\n"
        f"{json.dumps(catalogo_compacto, ensure_ascii=False)}\n\n"
        "METADATOS DE LA NORMA:\n"
        f"{json.dumps(cabecera, ensure_ascii=False)}\n\n"
        "TEXTO OFICIAL DE LA NORMA:\n"
        f"{texto_limpio}\n"
    )


def _crear_cliente_gemini():
    """Instancia el cliente oficial `google.genai` leyendo solo `GEMINI_API_KEY`."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ErrorVerificacionIA(
            "La variable de entorno GEMINI_API_KEY no está configurada para ejecutar síntesis con IA."
        )
    try:
        from google import genai
    except ImportError as exc:
        raise ErrorVerificacionIA(
            "El paquete oficial 'google-genai' no está instalado en este entorno."
        ) from exc
    return genai.Client(api_key=api_key)


def _invocar_modelo_gemini(
    cliente: Any,
    modelo: str,
    instrucciones: str,
    contenido_usuario: str,
) -> Tuple[str, int, int]:
    """Ejecuta una llamada al SDK `google-genai` y extrae texto y conteo de tokens."""
    config_genai: Any
    try:
        from google.genai import types

        config_genai = types.GenerateContentConfig(
            system_instruction=instrucciones,
            response_mime_type="application/json",
            temperature=0.1,
        )
    except ImportError:
        config_genai = {
            "system_instruction": instrucciones,
            "response_mime_type": "application/json",
            "temperature": 0.1,
        }

    respuesta = cliente.models.generate_content(
        model=modelo,
        contents=contenido_usuario,
        config=config_genai,
    )
    texto = getattr(respuesta, "text", None) or ""
    uso = getattr(respuesta, "usage_metadata", None)
    tok_in = int(getattr(uso, "prompt_token_count", 0) or 0)
    tok_out = int(getattr(uso, "candidates_token_count", 0) or 0)
    return texto, tok_in, tok_out


def generar_y_verificar_ia(
    ficha_meta: Dict[str, Any],
    texto_origen: str,
    catalogo_politicas: List[Dict[str, Any]],
    gestor: Optional[GestorLlamadasIA] = None,
    cliente: Optional[Any] = None,
    modelo: Optional[str] = None,
    version_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Genera el análisis estructurado con Gemini y lo valida contra el texto origen."""
    if gestor is None:
        gestor = GestorLlamadasIA()
    if not gestor.puede_procesar_norma():
        raise ErrorVerificacionIA("Tope diario de normas o llamadas a IA alcanzado.")

    modelo_activo = modelo or getattr(config, "GEMINI_MODELO_NORMAS", "gemini-3.8-flash")
    modelos_respaldo = (
        []
        if modelo
        else list(getattr(config, "GEMINI_MODELOS_RESPALDO_NORMAS", []))
    )
    candidatos_modelo = [modelo_activo] + [m for m in modelos_respaldo if m and m != modelo_activo]
    ver_prompt = version_prompt or getattr(config, "NORMAS_PROMPT_VERSION", "norma_v1")
    instrucciones = cargar_instrucciones_prompt(ver_prompt)
    contenido_usuario = _construir_prompt_usuario(ficha_meta, texto_origen, catalogo_politicas)

    cliente_activo = cliente if cliente is not None else _crear_cliente_gemini()
    errores_ultimos: List[str] = []

    for intento in range(1, gestor.max_reintentos + 1):
        if gestor.llamadas_realizadas >= gestor.tope_llamadas:
            raise ErrorVerificacionIA("Tope máximo de llamadas a IA agotado durante reintento.")
        modelo_intento = candidatos_modelo[min(intento - 1, len(candidatos_modelo) - 1)]
        gestor.llamadas_realizadas += 1
        try:
            crudo, tok_in, tok_out = _invocar_modelo_gemini(
                cliente_activo, modelo_intento, instrucciones, contenido_usuario
            )
            gestor.tokens_entrada += tok_in
            gestor.tokens_salida += tok_out
            salida_json = json.loads(_limpiar_json_crudo(crudo))
        except ErrorVerificacionIA:
            raise
        except Exception as exc:
            cod = getattr(exc, "code", None)
            est = getattr(exc, "status", None)
            msg = str(getattr(exc, "message", "") or "")
            if msg:
                msg = re.sub(r"AIza[0-9A-Za-z_-]+", "[REDACTED]", msg)[:140]
            detalle = " ".join(str(x) for x in (cod, est, msg) if x)
            etiq = f"{type(exc).__name__} {detalle}".strip()
            errores_ultimos = [f"Intento {intento} ({modelo_intento}): error de respuesta o JSON ({etiq})."]
            if intento < gestor.max_reintentos:
                time.sleep(2.5)
            continue

        es_valida, errs = verificar_salida_ia_contra_texto(
            salida_json,
            texto_origen,
            catalogo_politicas,
            sumilla=ficha_meta.get("sumilla") or "",
        )
        if es_valida:
            gestor.normas_procesadas += 1
            return {
                "analisis": salida_json,
                "modelo": modelo_intento,
                "version_instrucciones": ver_prompt,
            }
        errores_ultimos = errs
        if intento < gestor.max_reintentos:
            time.sleep(1.5)

    raise ErrorVerificacionIA(
        "Verificación automática de salida IA fallida tras reintentos: "
        + "; ".join(errores_ultimos[:4])
    )

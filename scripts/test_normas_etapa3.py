"""Pruebas unitarias y de integración sin red externa para la Etapa 3 (Normas Legales)."""

import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from scripts import actualizar_normas_diario as diario
from scripts.normas.elperuano_client import parsear_listado_html, parsear_texto_norma_html
from scripts.normas.generador_ia import (
    ErrorVerificacionIA,
    GestorLlamadasIA,
    generar_y_verificar_ia,
)
from scripts.normas.verificador_ia import (
    extraer_normas_citadas_regex,
    extraer_numero_y_anio,
    generar_id_estable,
    verificar_salida_ia_contra_texto,
)
from sections.normas_comentadas import (
    _render_banner_ia_html,
    _render_enlaces_ficha_html,
    construir_tarjeta_norma_html,
    filtrar_normas,
    validar_url_http,
)
from utils import loaders


TEXTO_BASE_NORMA = """
DECRETO SUPREMO N° 250-2026-EF
CONSIDERANDO:
Que, mediante la Ley N° 32513 se aprueba el Presupuesto del Sector Público para el Año Fiscal 2026;
Que, resulta necesario autorizar una Transferencia de Partidas en concordancia con la Política Nacional del Ambiente al 2030;
DECRETA:
Artículo 1. Objeto
Autorízase una Transferencia de Partidas en el Presupuesto del Sector Público para el Año Fiscal 2026 hasta por la suma de S/ 4 500 000,00 a favor de la entidad ambiental.
Artículo 2. Procedimiento para la aprobación institucional
El titular del pliego habilitado aprueba mediante resolución la desagregación de los recursos autorizados dentro de los cinco días calendario.
"""

CATALOGO_TEST = [
    {"id": "pn_ambiente_2030", "nombre": "Política Nacional del Ambiente al 2030", "tipo": "Política Nacional"}
]


def _salida_ia_valida() -> dict:
    return {
        "que_dispone": (
            "Autoriza una transferencia presupuestaria de partidas hasta por S/ 4 500 000,00 "
            "a favor de la entidad ambiental para el año fiscal 2026 y establece el plazo institucional "
            "para aprobar la desagregación de recursos."
        ),
        "repercusiones_esperadas": [
            {
                "efecto": "Permitiría ejecutar el monto transferido conforme al procedimiento de desagregación institucional.",
                "articulo": "Artículo 1",
                "cita": "Autorízase una Transferencia de Partidas en el Presupuesto del Sector Público",
            }
        ],
        "politica_nacional": [
            {
                "id": "pn_ambiente_2030",
                "tipo_alineacion": "sugerida por IA",
                "articulo": "Considerandos",
                "cita": "en concordancia con la Política Nacional del Ambiente al 2030",
            }
        ],
        "normas_citadas": [
            {
                "tipo": "Ley",
                "numero": "32513",
                "anio": "2025",
                "relacion_detectada": "base legal presupuestaria",
            }
        ],
        "preguntas_a_verificar": [
            "¿Qué partidas programáticas específicas detalla el anexo del Decreto Supremo?"
        ],
    }


class TestNormasEtapa3(unittest.TestCase):
    """Cubre esquema, verificador anti-alucinación, fail-safe IA, stream parser y UI."""

    def test_id_estable_y_extraccion_numero(self):
        num, anio = extraer_numero_y_anio("N° 250-2026-EF", "2026-11-13")
        self.assertEqual(num, "250-2026-EF")
        self.assertEqual(anio, "2026")
        nid = generar_id_estable("DECRETO SUPREMO", num, anio, "ECONOMÍA Y FINANZAS")
        self.assertEqual(nid, "decreto-supremo-250-2026-ef-2026-economia-y-finanzas")

    def test_verificador_acepta_salida_fiel(self):
        ok, errores = verificar_salida_ia_contra_texto(
            _salida_ia_valida(), TEXTO_BASE_NORMA, CATALOGO_TEST, sumilla="Transferencia ambiental"
        )
        self.assertTrue(ok, f"Errores inesperados: {errores}")

    def test_verificador_rechaza_cita_inventada_o_juicio_o_norma_falsa(self):
        # 1) Cita inexistente
        mal1 = _salida_ia_valida()
        mal1["repercusiones_esperadas"][0]["cita"] = "Frase totalmente inventada que no existe"
        ok1, _ = verificar_salida_ia_contra_texto(mal1, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok1)

        # 2) Norma citada inventada
        mal2 = _salida_ia_valida()
        mal2["normas_citadas"][0]["numero"] = "99999-2026"
        ok2, _ = verificar_salida_ia_contra_texto(mal2, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok2)

        # 3) Juicio político/jurídico prohibido
        mal3 = _salida_ia_valida()
        mal3["que_dispone"] = "Esta medida es inconstitucional e ilegal para el sector."
        ok3, _ = verificar_salida_ia_contra_texto(mal3, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok3)

        # 4) Política fuera de catálogo
        mal4 = _salida_ia_valida()
        mal4["politica_nacional"][0]["id"] = "pn_inexistente"
        ok4, _ = verificar_salida_ia_contra_texto(mal4, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok4)

        # 5) Repercusión sin modo condicional
        mal5 = _salida_ia_valida()
        mal5["repercusiones_esperadas"][0]["efecto"] = "Logró un beneficio inmediato en la entidad."
        ok5, _ = verificar_salida_ia_contra_texto(mal5, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok5)

        # 6) Más de 120 palabras en que_dispone
        mal6 = _salida_ia_valida()
        mal6["que_dispone"] = " ".join(["palabra"] * 125)
        ok6, _ = verificar_salida_ia_contra_texto(mal6, TEXTO_BASE_NORMA, CATALOGO_TEST)
        self.assertFalse(ok6)

    def test_extraer_normas_citadas_regex(self):
        citadas = extraer_normas_citadas_regex(TEXTO_BASE_NORMA, excluir_numero="250-2026-EF")
        numeros = [c["numero"] for c in citadas]
        self.assertIn("32513", numeros)
        self.assertNotIn("250-2026-EF", numeros)

    def test_generador_ia_con_cliente_mockeado_y_fallo(self):
        respuesta_ok = SimpleNamespace(
            text=json.dumps(_salida_ia_valida(), ensure_ascii=False),
            usage_metadata=SimpleNamespace(prompt_token_count=310, candidates_token_count=120),
        )
        cliente_ok = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: respuesta_ok))
        gestor = GestorLlamadasIA(tope_normas=3, tope_llamadas=5, max_reintentos=2)
        res = generar_y_verificar_ia(
            {"tipo": "Decreto Supremo", "numero": "N° 250-2026-EF", "entidad": "MEF", "fecha": "2026-11-13", "sumilla": "Transferencia"},
            TEXTO_BASE_NORMA,
            CATALOGO_TEST,
            gestor=gestor,
            cliente=cliente_ok,
        )
        self.assertEqual(res["version_instrucciones"], "norma_v1")
        self.assertEqual(gestor.llamadas_realizadas, 1)
        self.assertEqual(gestor.tokens_entrada, 310)

        # Mock que siempre inventa cita -> debe fallar tras max_reintentos=2
        bad_payload = _salida_ia_valida()
        bad_payload["repercusiones_esperadas"][0]["cita"] = "Cita inventada inexistente"
        respuesta_bad = SimpleNamespace(text=json.dumps(bad_payload), usage_metadata=None)
        cliente_bad = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: respuesta_bad))
        gestor_bad = GestorLlamadasIA(tope_normas=3, tope_llamadas=5, max_reintentos=2)
        with self.assertRaises(ErrorVerificacionIA):
            generar_y_verificar_ia(
                {"tipo": "Decreto Supremo", "numero": "N° 250-2026-EF", "entidad": "MEF", "fecha": "2026-11-13", "sumilla": "Transferencia"},
                TEXTO_BASE_NORMA,
                CATALOGO_TEST,
                gestor=gestor_bad,
                cliente=cliente_bad,
            )
        self.assertEqual(gestor_bad.llamadas_realizadas, 2)

    def test_pipeline_aborta_sin_publicar_en_fallo_ia_y_override_humano(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_of = os.path.join(tmp, "normas_oficiales")
            dir_com = os.path.join(tmp, "normas_comentadas")
            os.makedirs(dir_com, exist_ok=True)
            ruta_est = os.path.join(tmp, "estado.json")
            ruta_cache = os.path.join(tmp, "cache.json")
            with open(ruta_cache, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "NL": [
                            {
                                "op": "2574516-1",
                                "tipoDispositivo": "DECRETO SUPREMO",
                                "numeroDispositivo": "N° 250-2026-EF",
                                "distributor": "ECONOMÍA Y FINANZAS",
                                "sumilla": "Autorizan Transferencia de Partidas a favor del sector ambiental",
                            }
                        ]
                    },
                    fh,
                )

            with (
                patch.object(diario, "DIR_NORMAS_OFICIALES", dir_of),
                patch.object(diario, "DIR_COMENTADAS", dir_com),
                patch.object(diario, "RUTA_ESTADO", ruta_est),
                patch.object(diario, "obtener_texto_norma", return_value=(200, TEXTO_BASE_NORMA, "a" * 64, "https://busquedas.elperuano.pe/dispositivo/NL/2574516-1")),
            ):
                # 1) Simular fallo IA -> no debe crear 2026-11.json y sí registrar estado.json error
                with self.assertRaises(ErrorVerificacionIA):
                    diario.ejecutar_pipeline_normas(
                        fecha_yyyymmdd="20261113",
                        usar_ia=True,
                        simular_fallo_ia=True,
                        cache_listado=ruta_cache,
                    )
                self.assertFalse(os.path.exists(os.path.join(dir_of, "2026-11.json")))
                with open(ruta_est, encoding="utf-8") as fh:
                    est = json.load(fh)
                self.assertEqual(est["fuentes"]["normas_diario"]["ultimo_estado"], "error")
                self.assertFalse(est["fuentes"]["normas_diario"]["publicado"])

                # 2) Crear revisión humana en normas_comentadas/<id>.md y correr sin IA
                nid_esperado = "decreto-supremo-250-2026-ef-2026-economia-y-finanzas"
                with open(os.path.join(dir_com, f"{nid_esperado}.md"), "w", encoding="utf-8") as fh:
                    fh.write("# Comentario verificado por persona\n\nTexto revisado.")

                res = diario.ejecutar_pipeline_normas(
                    fecha_yyyymmdd="20261113",
                    usar_ia=False,
                    cache_listado=ruta_cache,
                )
                self.assertTrue(res["publicado"])
                ruta_mes = os.path.join(dir_of, "2026-11.json")
                self.assertTrue(os.path.exists(ruta_mes))
                with open(ruta_mes, encoding="utf-8") as fh:
                    mes_data = json.load(fh)
                self.assertEqual(mes_data["normas"][0]["estado"], "revisado por persona")

    def test_parsers_react_router_stream(self):
        stream_listado = json.dumps(
            [{"_1": 2, "_3": 4}, "hits", [5], "totalHits", 1, {"_6": 7, "_8": 9}, "op", "2574506-1", "sumilla", "Norma demo"]
        )
        raw_list = f'<script>enqueue({json.dumps(stream_listado)});</script>'
        hits, total = parsear_listado_html(raw_list)
        self.assertEqual(total, 1)
        self.assertEqual(hits[0]["op"], "2574506-1")

        stream_norm = json.dumps(["root", "htmlContent", "<p>Artículo 1.- Objeto</p><p>Texto oficial.</p>"])
        raw_norm = f'<script>enqueue({json.dumps(stream_norm)});</script>'
        texto, sha = parsear_texto_norma_html(raw_norm)
        self.assertEqual(texto, "Artículo 1.- Objeto\nTexto oficial.")
        self.assertEqual(len(sha), 64)

    def test_ui_helpers_seguridad_y_filtros(self):
        self.assertEqual(validar_url_http("https://busquedas.elperuano.pe/dispositivo/NL/1"), "https://busquedas.elperuano.pe/dispositivo/NL/1")
        self.assertIsNone(validar_url_http("javascript:alert(1)"))
        self.assertIsNone(validar_url_http("data:text/html,<script>alert(1)</script>"))
        self.assertIsNone(loaders.load_norma_comentada_md("../config.py"))
        self.assertIsInstance(loaders.load_normas_oficiales(), list)

        ficha_xss = {
            "id": "norma-1",
            "numero": "<script>alert(1)</script>",
            "url_oficial": "javascript:alert(2)",
            "modelo": "<img src=x>",
            "fecha_ia": "2026-11-13",
            "eje": "polity",
            "subtema": "Reforma",
            "entidad": "PCM",
            "fecha_publicacion": "2026-11-13",
            "prioridad": "normal",
            "politica_nacional": [{"id": "pn_modernizacion_2030", "tipo_alineacion": "explícita"}],
        }
        enlaces = _render_enlaces_ficha_html(ficha_xss)
        self.assertNotIn("javascript:", enlaces)
        self.assertIn('rel="noopener noreferrer"', enlaces)

        banner = _render_banner_ia_html(ficha_xss)
        self.assertNotIn("<img", banner)
        self.assertIn("Generado con IA", banner)

        filtradas = filtrar_normas([ficha_xss], eje="polity", politica_id="pn_modernizacion_2030")
        self.assertEqual(len(filtradas), 1)
        self.assertEqual(filtrar_normas([ficha_xss], eje="policy"), [])

        tarjeta_html = construir_tarjeta_norma_html(ficha_xss, catalogo_map={"pn_modernizacion_2030": "PN Modernización"})
        self.assertIn("norma-eje-polity", tarjeta_html)
        self.assertIn('href="?vista=normas_comentadas&amp;norma=norma-1"', tarjeta_html)
        self.assertIn("PN Modernización", tarjeta_html)
        self.assertNotIn("javascript:", tarjeta_html)
        self.assertNotIn("<script>", tarjeta_html)

    def test_rastrea_la_norma_sidebar_y_diagrama(self):
        from components.sidebar import OPTIONS_LIST
        from sections.rastrea_la_norma import construir_diagrama_flujo_normas_html

        self.assertIn("Rastrea la Norma", OPTIONS_LIST)
        self.assertEqual(OPTIONS_LIST.index("Inicio") + 1, OPTIONS_LIST.index("Rastrea la Norma"))
        self.assertEqual(OPTIONS_LIST.index("Rastrea la Norma") + 1, OPTIONS_LIST.index("Polity and Policy"))

        flujo_html = construir_diagrama_flujo_normas_html(
            ia_habilitada=True,
            modelo_ia="gemini-2.5-flash",
            ultimo_estado="ok",
            ultimo_intento="<script>bad</script>2026-11-14",
            total_fichas=11,
        )
        self.assertIn("¿Cómo seguimos la norma?", flujo_html)
        self.assertIn("PASO 01", flujo_html)
        self.assertIn("PASO 05", flujo_html)
        self.assertIn("flow-connector-svg", flujo_html)
        self.assertIn("11 fichas", flujo_html)
        self.assertNotIn("\n    <div", flujo_html)
        self.assertNotIn("<script>", flujo_html)


if __name__ == "__main__":
    unittest.main()

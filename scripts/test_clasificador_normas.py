import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.normas.clasificador import (
    cargar_criterios,
    clasificar_norma,
    detectar_alineacion_explicita,
    sanitizar_texto_sin_nombres,
)


class TestClasificadorNormas(unittest.TestCase):
    def setUp(self):
        self.criterios = cargar_criterios()
        self.catalogo_mock = [
            {
                "id": "pn_modernizacion_2030",
                "nombre": "Política Nacional de Modernización de la Gestión Pública al 2030",
                "alias": ["PNMGP", "Política Nacional de Modernización de la Gestión Pública"],
                "tipo": "Política Nacional",
                "norma_aprobacion": "D.S. N° 103-2022-PCM",
                "entidad_rectora": "PCM",
                "url_oficial": "https://busquedas.elperuano.pe/",
                "estado": "por verificar a mano",
            },
            {
                "id": "pn_ambiente_2030",
                "nombre": "Política Nacional del Ambiente al 2030",
                "alias": ["PNA al 2030", "Política Nacional del Ambiente"],
                "tipo": "Política Nacional",
                "norma_aprobacion": "D.S. N° 023-2021-MINAM",
                "entidad_rectora": "MINAM",
                "url_oficial": "https://busquedas.elperuano.pe/",
                "estado": "por verificar a mano",
            },
        ]

    def test_exclusiones_principales(self):
        casos = [
            ("viajes", "RESOLUCIÓN SUPREMA", "Autorizan viaje de Ministro a China en comisión de servicios"),
            ("designaciones_nombramientos", "RESOLUCIÓN MINISTERIAL", "Designan Asesor II del Despacho Viceministerial"),
            ("encargos", "RESOLUCIÓN MINISTERIAL", "Encargan el despacho de la Secretaría General"),
            ("renuncias", "RESOLUCIÓN MINISTERIAL", "Aceptan renuncia de Directora General"),
            ("extradiciones", "RESOLUCIÓN SUPREMA", "Acceden a solicitud de extradición activa de ciudadano peruano"),
            ("expropiaciones", "RESOLUCIÓN JEFATURAL", "Aprueban ejecución de expropiación de área afectada de inmueble"),
            ("traslados_oficinas", "RESOLUCIÓN", "Autorizan traslado de la Oficina Receptora de Challhuahuacho"),
            ("edictos_matrimoniales", "ORDENANZA", "Disponen dispensar de la publicación de edicto matrimonial"),
            ("proteccion_provisional_arqueologica", "RESOLUCIÓN DIRECTORAL", "Determinan la Protección Provisional del sitio arqueológico Los Pacaes"),
            ("actos_jurisdiccionales_y_particulares", "RESOLUCIÓN", "Confirman la Resolución N.° 03074-2026-JEE-MAYN/JNE"),
            ("actos_jurisdiccionales_y_particulares", "RESOLUCIÓN DIRECTORAL", "Autorizan a la empresa Demo S.A.C. para operar como Centro de Inspección Técnica Vehicular"),
        ]
        for expected_rule, tipo, sumilla in casos:
            with self.subTest(rule=expected_rule, sumilla=sumilla):
                res = clasificar_norma(
                    {"tipoDispositivo": tipo, "numeroDispositivo": "N° 001-2026", "distributor": "ENTIDAD", "sumilla": sumilla},
                    criterios=self.criterios,
                    catalogo=self.catalogo_mock,
                )
                self.assertEqual(res["decision"], "excluida")
                self.assertEqual(res["prioridad"], "excluida")
                self.assertEqual(res.get("regla_exclusion"), expected_rule)

    def test_tipo_fuera_de_catalogo_excluido(self):
        res = clasificar_norma(
            {
                "tipoDispositivo": "Decretos de Alcaldía",
                "numeroDispositivo": "N° 014-2026",
                "distributor": "MUNICIPALIDAD",
                "sumilla": "Disponen medidas de trámite administrativo local",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res["decision"], "excluida")
        self.assertIn("fuera de catálogo", res["motivo"])

    def test_transferencias_baja_prioridad_no_excluidas(self):
        res = clasificar_norma(
            {
                "tipoDispositivo": "DECRETO SUPREMO",
                "numeroDispositivo": "N° 252-2026-EF",
                "distributor": "ECONOMÍA Y FINANZAS",
                "sumilla": "Decreto Supremo que autoriza Transferencia de Partidas en el Presupuesto del Sector Público para el Año Fiscal 2026",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res["decision"], "incluida")
        self.assertEqual(res["prioridad"], "baja prioridad")
        self.assertEqual(res["eje"], "policy")

    def test_ejes_polity_policy_mixto_otro(self):
        # Polity prioritario por POI aunque entidad sea sectorial
        res_poi = clasificar_norma(
            {
                "tipoDispositivo": "RESOLUCIÓN MINISTERIAL",
                "numeroDispositivo": "N° 421-2026-MINCETUR",
                "distributor": "COMERCIO EXTERIOR Y TURISMO",
                "sumilla": "Aprueban el Plan Operativo Institucional (POI) Anual 2026 Actualizado Versión 2 del Ministerio de Comercio Exterior y Turismo",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res_poi["decision"], "incluida")
        self.assertEqual(res_poi["eje"], "polity")
        self.assertEqual(res_poi["subtema"], "Sistemas Administrativos, Planeamiento y Modernización")

        # Polity prioritario por MCC aunque entidad sea Universidad
        res_mcc = clasificar_norma(
            {
                "tipoDispositivo": "RESOLUCIÓN",
                "numeroDispositivo": "N° 39-2026-CCO-UNFAY",
                "distributor": "INSTITUCIONES EDUCATIVAS",
                "sumilla": "Aprueban el Manual de Clasificador de Cargos de la Universidad Nacional Fronteriza Autónoma de Yunguyo (MCC)",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res_mcc["decision"], "incluida")
        self.assertEqual(res_mcc["eje"], "polity")
        self.assertEqual(res_mcc["subtema"], "Servicio Civil y Recursos Humanos del Estado")

        # Policy
        res_policy = clasificar_norma(
            {
                "tipoDispositivo": "RESOLUCIÓN MINISTERIAL",
                "numeroDispositivo": "N° 481-2026-MINEM/DM",
                "distributor": "ENERGÍA Y MINAS",
                "sumilla": "Modifican magnitud de la capacidad adicional de generación eléctrica de naturaleza temporal",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res_policy["decision"], "incluida")
        self.assertEqual(res_policy["eje"], "policy")

        # Mixto
        res_mixto = clasificar_norma(
            {
                "tipoDispositivo": "DECRETO SUPREMO",
                "numeroDispositivo": "N° 010-2026-PCM",
                "distributor": "PRESIDENCIA DEL CONSEJO DE MINISTROS",
                "sumilla": "Crean Comisión Multisectorial de simplificación administrativa para el cambio climático y residuos sólidos",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res_mixto["decision"], "incluida")
        self.assertEqual(res_mixto["eje"], "mixto")

        # Otro (sin keywords pero no excluido)
        res_otro = clasificar_norma(
            {
                "tipoDispositivo": "RESOLUCIÓN",
                "numeroDispositivo": "N° 001-2026-DEMO",
                "distributor": "ORGANISMO DEMO",
                "sumilla": "Disponen publicación de fe de erratas y tabla de códigos referenciales",
            },
            criterios=self.criterios,
            catalogo=self.catalogo_mock,
        )
        self.assertEqual(res_otro["decision"], "incluida")
        self.assertEqual(res_otro["eje"], "otro")

    def test_alineacion_explicita_catalogo_y_patron_y_limite_25_palabras(self):
        texto = (
            "CONSIDERANDO:\n"
            "Que, en concordancia con la Política Nacional de Modernización de la Gestión Pública al 2030, "
            "las entidades públicas implementan mejoras continuas orientadas a resultados.\n"
            "Artículo 1.- Aprobar la actualización sectorial conforme a la Política Nacional de Educación Ambiental vigente."
        )
        hallazgos = detectar_alineacion_explicita("Aprobación de lineamientos", texto, catalogo=self.catalogo_mock)
        ids = {h["id"] for h in hallazgos}
        self.assertIn("pn_modernizacion_2030", ids)
        self.assertIn("no_catalogada", ids)
        for h in hallazgos:
            self.assertEqual(h["tipo_alineacion"], "explícita")
            self.assertTrue(h["articulo"])
            self.assertLessEqual(len(h["extracto"].split()), 25)

    def test_sanitizacion_sin_nombres(self):
        s1 = sanitizar_texto_sin_nombres("Designan a JUAN CARLOS PÉREZ LÓPEZ en el cargo de Asesor")
        self.assertNotIn("JUAN CARLOS", s1)
        self.assertIn("[DATO DE PERSONA OMITIDO]", s1)

        s2 = sanitizar_texto_sin_nombres("Acceden a extradición de ciudadano peruano JUAN PÉREZ, identificado con DNI N° 12345678")
        self.assertNotIn("JUAN PÉREZ", s2)
        self.assertNotIn("12345678", s2)


if __name__ == "__main__":
    unittest.main()

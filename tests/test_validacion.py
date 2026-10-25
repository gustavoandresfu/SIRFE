import unittest
from modelos import SemanticUnit, TraceabilityMetadata, Cluster
from generar_json_negocio import generar_especificacion
from validar_metodologia import validar_metodologia

class TestValidacionMetodologia(unittest.TestCase):

    def test_validar_metodologia_metricas(self):
        u1 = SemanticUnit(
            traceability=TraceabilityMetadata(
                file_path="auth.py",
                class_name="AuthManager",
                name="check_permiso",
                start_line=1,
                end_line=20,
                node_type="FunctionDef"
            ),
            roles=[{"role": "VALIDATOR", "confidence": 0.85}],
            actions=[{"action": "CheckPermiso", "confidence": 0.8}],
            inputs=["user_id"],
            outputs=["bool"],
            dependencies=[],
            calls=[],
            state_changes={"persistent": False, "memory": False, "external": False},
            exceptions=[],
            preconditions=["user_id > 0"],
            postconditions=["Retorna valor del tipo bool"],
            domain="IDENTITY"
        )

        cluster = Cluster(id=0, units=[u1])
        especificacion = generar_especificacion([cluster])
        reporte = validar_metodologia([u1], especificacion)

        self.assertIn("resumen_estadistico", reporte)
        resumen = reporte["resumen_estadistico"]
        self.assertEqual(resumen["total_unidades_analizadas"], 1)
        self.assertEqual(resumen["unidades_mapeadas_exitosamente"], 1)
        self.assertEqual(resumen["cobertura_unidades"], "100.00%")
        self.assertEqual(resumen["lineas_codigo_totales"], 20)

        honestidad = reporte["evaluacion_honestidad_sir"]
        self.assertEqual(honestidad["confianza_promedio_general"], "0.85")

    def test_validar_metodologia_lista_vacia(self):
        reporte = validar_metodologia([], None)
        self.assertEqual(reporte["resumen_estadistico"]["total_unidades_analizadas"], 0)

if __name__ == "__main__":
    unittest.main()

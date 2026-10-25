import unittest
from modelos import SemanticUnit, TraceabilityMetadata, Cluster
from generar_json_negocio import generar_especificacion

class TestSintesisNegocio(unittest.TestCase):

    def test_generar_especificacion_gherkin(self):
        u1 = SemanticUnit(
            traceability=TraceabilityMetadata(
                file_path="modulo.py",
                class_name="ServicioAuth",
                name="validar_acceso",
                start_line=10,
                end_line=25,
                node_type="FunctionDef"
            ),
            roles=[{"role": "VALIDATOR", "confidence": 0.95}],
            actions=[{"action": "ValidarAcceso", "confidence": 0.9}],
            inputs=["token"],
            outputs=["bool"],
            dependencies=["auth_provider"],
            calls=["check_token"],
            state_changes={"persistent": False, "memory": False, "external": False},
            exceptions=["AuthError"],
            preconditions=["token is not None"],
            postconditions=["Retorna valor del tipo bool"],
            domain="IDENTITY"
        )

        cluster = Cluster(id=0, units=[u1])
        especificacion = generar_especificacion([cluster])

        self.assertIsNotNone(especificacion)
        self.assertEqual(len(especificacion.capacidades_funcionales), 1)

        cap = especificacion.capacidades_funcionales[0]
        self.assertEqual(cap.id, "CAP-000")
        self.assertIn("IDENTITY", cap.titulo)
        self.assertIn("Como componente de negocio", cap.historia_usuario)

        # Verificar escenario Gherkin
        escenario = cap.escenario_gherkin_sintetizado
        self.assertIn("IDENTITY", escenario.dado)
        self.assertIn("token is not None", escenario.dado)
        self.assertIn("ValidarAcceso", escenario.cuando)
        self.assertIn("token", escenario.cuando)
        self.assertIn("AuthError", escenario.y)

        # Verificar sustento técnico
        self.assertEqual(cap.sustento_tecnico.cantidad_unidades, 1)
        self.assertIn("ServicioAuth.validar_acceso", cap.sustento_tecnico.unidades[0])

if __name__ == "__main__":
    unittest.main()

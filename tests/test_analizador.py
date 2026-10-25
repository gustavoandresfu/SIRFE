import unittest
import ast
import tempfile
import os
from analizar_codigo_legacy import UniversalIRAnalyzer, analizar

class TestUniversalIRAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_code = """
class UserManager:
    def __init__(self):
        self.activo = True

    def auth_user(self, user, password):
        if not user or not password:
            raise ValueError("Credenciales invalidas")
        return True

    def guardar_perfil(self, usuario_id, datos):
        assert usuario_id > 0
        self.usuario_actual = usuario_id
        resultado = []
        for clave, valor in datos.items():
            resultado.append((clave, valor))
        self.user_repo.write(datos)
        return resultado
"""

    def test_extraccion_roles_heuristicos(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(self.sample_code)
            temp_path = temp_file.name

        try:
            unidades = analizar(temp_path)
            # Buscar metodo auth_user
            autenticar = next((u for u in unidades if u.traceability.name == "auth_user"), None)
            self.assertIsNotNone(autenticar)
            
            roles_autenticar = [r["role"] for r in autenticar.roles]
            self.assertIn("VALIDATOR", roles_autenticar)
            self.assertIn("EXTRACTOR", roles_autenticar)
            self.assertEqual(autenticar.domain, "IDENTITY")
            self.assertTrue(len(autenticar.preconditions) > 0)

            # Buscar metodo guardar_perfil
            guardar = next((u for u in unidades if u.traceability.name == "guardar_perfil"), None)
            self.assertIsNotNone(guardar)
            roles_guardar = [r["role"] for r in guardar.roles]
            self.assertIn("VALIDATOR", roles_guardar)
            self.assertIn("PERSISTER", roles_guardar)
            self.assertIn("TRANSFORMER", roles_guardar)
            self.assertTrue(guardar.state_changes["persistent"])
            self.assertTrue(guardar.state_changes["memory"])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_filtro_por_metodo(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(self.sample_code)
            temp_path = temp_file.name

        try:
            unidades = analizar(temp_path, filter_method="auth_user")
            self.assertEqual(len(unidades), 1)
            self.assertEqual(unidades[0].traceability.name, "auth_user")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()

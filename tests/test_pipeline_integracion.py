import unittest
import tempfile
import os
from analizar_codigo_legacy import analizar
from clustering_ir import clusterizar
from generar_json_negocio import generar_especificacion
from validar_metodologia import validar_metodologia

class TestPipelineIntegracion(unittest.TestCase):

    def test_pipeline_completo_en_memoria(self):
        codigo = """
class FacturacionService:
    def emitir_factura(self, cliente_id, monto):
        if monto <= 0:
            raise ValueError("Monto invalido")
        self.ultima_operacion = cliente_id
        items = []
        for i in range(1):
            items.append(monto)
        self.db.write(items)
        return True

    def consultar_saldo(self, cliente_id):
        if not cliente_id:
            return None
        return 100.0
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(codigo)
            tmp_path = tmp.name

        try:
            # 1. Analizar AST -> SIR
            metodos = analizar(tmp_path)
            self.assertEqual(len(metodos), 2)

            # 2. Clustering
            clusters = clusterizar(metodos)
            self.assertGreater(len(clusters), 0)

            # 3. Síntesis de especificación funcional
            especificacion = generar_especificacion(clusters)
            self.assertGreater(len(especificacion.capacidades_funcionales), 0)

            # 4. Validación de KPIs
            reporte = validar_metodologia(metodos, especificacion)
            self.assertEqual(reporte["resumen_estadistico"]["total_unidades_analizadas"], 2)
            self.assertEqual(reporte["resumen_estadistico"]["unidades_mapeadas_exitosamente"], 2)
            self.assertEqual(reporte["resumen_estadistico"]["cobertura_unidades"], "100.00%")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()

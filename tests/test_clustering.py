import unittest
from modelos import SemanticUnit, TraceabilityMetadata
from clustering_ir import FeatureExtractor, KMeansAlgorithm, AgglomerativeAlgorithm, DBSCANAlgorithm, clusterizar

class TestClusteringIR(unittest.TestCase):

    def _crear_unidad(self, name, role, domain, persistent=False, memory=False):
        return SemanticUnit(
            traceability=TraceabilityMetadata(
                file_path="dummy.py",
                class_name="DummyClass",
                name=name,
                start_line=1,
                end_line=10,
                node_type="FunctionDef"
            ),
            roles=[{"role": role, "confidence": 0.9}],
            actions=[{"action": name.capitalize(), "confidence": 0.8}],
            inputs=["arg1"],
            outputs=["bool"],
            dependencies=["repo" if persistent else "logger"],
            calls=["write" if persistent else "log"],
            state_changes={"persistent": persistent, "memory": memory, "external": False},
            exceptions=["ValueError"],
            preconditions=["arg1 is not None"],
            postconditions=["Retorna valor del tipo bool"],
            domain=domain
        )

    def test_feature_extractor_dimensiones(self):
        u1 = self._crear_unidad("validar", "VALIDATOR", "IDENTITY")
        u2 = self._crear_unidad("guardar", "PERSISTER", "STORAGE", persistent=True)
        
        X = FeatureExtractor.extract_features([u1, u2])
        self.assertEqual(X.shape[0], 2)
        self.assertGreater(X.shape[1], 0)

    def test_clusterizar_retorna_clusters(self):
        units = [
            self._crear_unidad("val1", "VALIDATOR", "IDENTITY"),
            self._crear_unidad("trans1", "TRANSFORMER", "UI_CONFIG", memory=True),
            self._crear_unidad("save1", "PERSISTER", "STORAGE", persistent=True),
            self._crear_unidad("ext1", "EXTRACTOR", "GENERIC"),
        ]
        clusters = clusterizar(units)
        self.assertIsInstance(clusters, list)
        self.assertGreater(len(clusters), 0)
        # La suma de las unidades en los clusters debe ser igual al total original
        total_en_clusters = sum(len(c.units) for c in clusters)
        self.assertEqual(total_en_clusters, len(units))

    def test_clusterizar_lista_vacia(self):
        clusters = clusterizar([])
        self.assertEqual(clusters, [])

if __name__ == "__main__":
    unittest.main()

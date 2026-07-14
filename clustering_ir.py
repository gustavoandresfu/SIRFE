import json
import os
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from modelos import SemanticUnit, Cluster

# 1. Definición de la interfaz del algoritmo de agrupamiento
class ClusterAlgorithm(ABC):
    @abstractmethod
    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        pass

class KMeansAlgorithm(ClusterAlgorithm):
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        n_cl = min(self.n_clusters, len(X))
        if n_cl <= 1:
            return np.zeros(len(X), dtype=int)
        kmeans = KMeans(n_clusters=n_cl, random_state=42, n_init=10)
        return kmeans.fit_predict(X)

class AgglomerativeAlgorithm(ClusterAlgorithm):
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        n_cl = min(self.n_clusters, len(X))
        if n_cl <= 1:
            return np.zeros(len(X), dtype=int)
        agg = AgglomerativeClustering(n_clusters=n_cl)
        return agg.fit_predict(X)

class DBSCANAlgorithm(ClusterAlgorithm):
    def __init__(self, eps: float = 0.5, min_samples: int = 2):
        self.eps = eps
        self.min_samples = min_samples

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        if len(X) < self.min_samples:
            return np.zeros(len(X), dtype=int)
        dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        labels = dbscan.fit_predict(X)
        # Reasignar ruido (-1) al cluster 0 para evitar errores en flujo posterior
        labels = np.where(labels == -1, 0, labels)
        return labels

# 2. Generador de la Representación de Características (Feature Representation)
class FeatureExtractor:
    @staticmethod
    def extract_features(units: List[SemanticUnit], confidence_threshold: float = 0.0) -> np.ndarray:
        if not units:
            return np.empty((0, 0))

        # Encontrar vocabulario de características únicas
        all_roles = set()
        all_domains = set()
        all_dependencies = set()
        all_exceptions = set()

        for u in units:
            for r_entry in u.roles:
                if r_entry.get("confidence", 1.0) >= confidence_threshold:
                    all_roles.add(r_entry["role"])
            all_domains.add(u.domain)
            for dep in u.dependencies:
                all_dependencies.add(dep)
            for exc in u.exceptions:
                all_exceptions.add(exc)

        roles_list = sorted(list(all_roles))
        domains_list = sorted(list(all_domains))
        dependencies_list = sorted(list(all_dependencies))
        exceptions_list = sorted(list(all_exceptions))

        # Construir matriz
        X_rows = []
        for u in units:
            row = []
            
            # Roles con pesos de confianza
            for role in roles_list:
                weight = 0.0
                for r_entry in u.roles:
                    if r_entry["role"] == role and r_entry.get("confidence", 1.0) >= confidence_threshold:
                        weight = r_entry.get("confidence", 1.0)
                row.append(weight)

            # Dominios (One-Hot)
            for dom in domains_list:
                row.append(1.0 if u.domain == dom else 0.0)

            # Cambios de estado (Boleanos mapeados a float)
            row.append(1.0 if u.state_changes.get("persistent") else 0.0)
            row.append(1.0 if u.state_changes.get("memory") else 0.0)
            row.append(1.0 if u.state_changes.get("external") else 0.0)

            # Dependencias (Multi-Hot)
            for dep in dependencies_list:
                row.append(1.0 if dep in u.dependencies else 0.0)

            # Excepciones (Multi-Hot)
            for exc in exceptions_list:
                row.append(1.0 if exc in u.exceptions else 0.0)

            X_rows.append(row)

        return np.array(X_rows)

def clusterizar(units: List[SemanticUnit], config_path: str = "config_analizador.json") -> List[Cluster]:
    if not units:
        return []

    # Cargar configuración de algoritmo
    alg_type = "kmeans"
    n_clusters = 4
    eps = 0.5
    min_samples = 2
    confidence_threshold = 0.0

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                profile = config.get("profiles", {}).get(config.get("active_profile", ""), {})
                # Cargar opciones de clustering específicas
                alg_type = config.get("clustering_algorithm", alg_type).lower()
                n_clusters = config.get("n_clusters", n_clusters)
                eps = config.get("eps", eps)
                min_samples = config.get("min_samples", min_samples)
                confidence_threshold = config.get("confidence_threshold", confidence_threshold)
        except Exception:
            pass

    # Extraer matriz de características
    X = FeatureExtractor.extract_features(units, confidence_threshold=confidence_threshold)
    
    # Seleccionar algoritmo
    if alg_type == "kmeans":
        alg = KMeansAlgorithm(n_clusters=n_clusters)
    elif alg_type == "agglomerative":
        alg = AgglomerativeAlgorithm(n_clusters=n_clusters)
    elif alg_type == "dbscan":
        alg = DBSCANAlgorithm(eps=eps, min_samples=min_samples)
    else:
        alg = KMeansAlgorithm(n_clusters=n_clusters)

    labels = alg.fit_predict(X)
    unique_labels = sorted(list(set(labels)))

    # Organizar resultados
    result_clusters = {label: [] for label in unique_labels}
    for idx, label in enumerate(labels):
        result_clusters[label].append(units[idx])

    output_clusters = []
    for label in unique_labels:
        output_clusters.append(Cluster(id=int(label), units=result_clusters[label]))

    return output_clusters

if __name__ == "__main__":
    try:
        with open("representacion_intermedia_semantica.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        units = [SemanticUnit.from_dict(u) for u in data]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error al cargar la representación intermedia semántica.")
        units = []

    clusters = clusterizar(units)

    print("=== CLUSTERING POR COMPORTAMIENTO (SIR SEMÁNTICA) ===\n")
    for cl in clusters:
        print(f"CLUSTER #{cl.id}:")
        for u in cl.units[:5]:
            roles_str = ", ".join(r["role"] for r in u.roles)
            print(f"  -> {u.traceability.class_name}.{u.traceability.name} [{roles_str} | {u.domain}]")
        print("-" * 50)

    output = {
        "clusters": [cl.to_dict() for cl in clusters]
    }
    with open("clusters_ir.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

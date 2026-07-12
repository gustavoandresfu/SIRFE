import json
from typing import List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder
from modelos import MethodMetadata, Cluster

def clusterizar(metodos: List[MethodMetadata]) -> List[Cluster]:
    if not metodos:
        return []

    # Preparar datos para OneHot
    features = []
    for m in metodos:
        features.append([m.ir.role, m.ir.effect, m.ir.op_type, m.ir.context])

    # Encoding
    encoder = OneHotEncoder()
    X = encoder.fit_transform(features).toarray()
    
    # Determinar número de clusters (máximo el número de métodos si son muy pocos, o 4 por defecto)
    n_clusters = min(4, len(metodos))
    if n_clusters == 0:
        return []

    # Clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters_labels = kmeans.fit_predict(X)

    # Organizar resultados
    result_clusters = {i: [] for i in range(n_clusters)}
    for idx, cluster_id in enumerate(clusters_labels):
        result_clusters[cluster_id].append(metodos[idx])

    # Convertir a objetos Cluster
    output_clusters = []
    for i in range(n_clusters):
        output_clusters.append(Cluster(id=i, methods=result_clusters[i]))

    return output_clusters

if __name__ == "__main__":
    try:
        with open("representacion_intermedia_semantica.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        metodos = [MethodMetadata.from_dict(m) for m in data]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error al cargar la representación intermedia semántica.")
        metodos = []

    clusters = clusterizar(metodos)

    # Mostrar ADN de cada Cluster en consola
    print("=== CLUSTERING POR COMPORTAMIENTO (IR SEMÁNTICA) ===\n")
    for cl in clusters:
        print(f"CLUSTER #{cl.id}:")
        # Mostrar los 5 métodos más representativos
        for m in cl.methods[:5]:
            print(f"  -> {m.class_name}.{m.method} [{m.ir.role} | {m.ir.effect} | {m.ir.context}]")
        print("-" * 50)

    # Guardar en clusters_ir.json para mantener compatibilidad
    output = {
        "clusters": [cl.to_dict() for cl in clusters]
    }
    with open("clusters_ir.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

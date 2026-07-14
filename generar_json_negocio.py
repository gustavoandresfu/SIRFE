import json
import os
from typing import List
from modelos import Cluster, FunctionalSpecification, FunctionalCapability, GherkinScenario, TechnicalSupport

def generar_especificacion(
    clusters: List[Cluster], 
    proyecto: str = "Análisis de Sistema Legado (Reingeniería)",
    metodologia: str = "Análisis Semántico por Representación Intermedia"
) -> FunctionalSpecification:
    
    capacidades_funcionales = []
    
    for cluster in clusters:
        if not cluster.units:
            continue
            
        cluster_id = cluster.id
        
        # 1. Agregación de características semánticas del cluster
        preconditions = set()
        actions = set()
        postconditions = set()
        exceptions = set()
        inputs = set()
        outputs = set()
        domains = set()
        roles = set()
        
        for u in cluster.units:
            preconditions.update(u.preconditions)
            for a_entry in u.actions:
                actions.add(a_entry["action"])
            postconditions.update(u.postconditions)
            exceptions.update(u.exceptions)
            inputs.update(u.inputs)
            outputs.update(u.outputs)
            domains.add(u.domain)
            for r_entry in u.roles:
                roles.add(r_entry["role"])

        # Convertir a listas ordenadas para estabilidad en la generación
        preconditions = sorted(list(preconditions))
        actions = sorted(list(actions))
        postconditions = sorted(list(postconditions))
        exceptions = sorted(list(exceptions))
        inputs = sorted(list(inputs))
        outputs = sorted(list(outputs))
        domains = sorted(list(domains))
        roles = sorted(list(roles))

        # Determinar el dominio funcional predominante
        domain_str = domains[0] if domains else "GENERIC"
        
        # 2. Generación dinámica de la capacidad de negocio
        id_cap = f"CAP-{cluster_id:03d}"
        titulo_cap = f"Capacidad Funcional en Dominio {domain_str} ({', '.join(roles)})"
        
        historia = (
            f"Como componente de negocio, quiero ejecutar las acciones ({', '.join(actions)}) "
            f"en el dominio de {domain_str} para procesar las entradas ({', '.join(inputs)}) "
            f"y retornar ({', '.join(outputs)}) garantizando las políticas semánticas."
        )

        # 3. Construcción del Escenario Gherkin Dinámico
        dado_str = "Que el sistema está inicializado en el dominio " + domain_str
        if preconditions:
            dado_str += " y se validan las precondiciones: " + ", ".join(preconditions)
            
        cuando_str = "Se ejecutan las acciones de " + ", ".join(actions)
        if inputs:
            cuando_str += " con los parámetros de entrada: " + ", ".join(inputs)
            
        entonces_list = []
        if postconditions:
            for post in postconditions:
                entonces_list.append(f"Se garantiza que: {post.lower()}")
        else:
            entonces_list.append("Se ejecuta el procesamiento lógico sin inconsistencias de estado")
            
        y_str = "Garantizar la estabilidad transaccional"
        if exceptions:
            y_str += " y mitigar la excepción " + ", ".join(exceptions)

        escenario = GherkinScenario(
            dado=dado_str,
            cuando=cuando_str,
            entonces=entonces_list,
            y=y_str
        )

        # 4. Sustento Técnico (Trazabilidad)
        unidades_sustento = [
            f"{u.traceability.class_name + '.' if u.traceability.class_name else ''}{u.traceability.name} "
            f"(L{u.traceability.start_line}-{u.traceability.end_line} en {os.path.basename(u.traceability.file_path)})"
            for u in cluster.units
        ]
        
        sustento = TechnicalSupport(
            cantidad_unidades=len(unidades_sustento),
            unidades=unidades_sustento
        )

        func_cap = FunctionalCapability(
            id=id_cap,
            titulo=titulo_cap,
            historia_usuario=historia,
            escenario_gherkin_sintetizado=escenario,
            sustento_tecnico=sustento
        )
        
        capacidades_funcionales.append(func_cap)
        
    return FunctionalSpecification(
        proyecto=proyecto,
        metodologia=metodologia,
        capacidades_funcionales=capacidades_funcionales
    )

if __name__ == "__main__":
    import os
    try:
        with open("clusters_ir.json", "r", encoding="utf-8") as f:
            clusters_data = json.load(f)
        clusters = [Cluster.from_dict(c) for c in clusters_data["clusters"]]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error al cargar los clusters.")
        clusters = []

    especificacion = generar_especificacion(clusters)

    with open("especificacion_funcional.json", "w", encoding="utf-8") as g:
        json.dump(especificacion.to_dict(), g, indent=4, ensure_ascii=False)
                
    print("Especificación FUNCIONAL dinámica en JSON generada exitosamente.")

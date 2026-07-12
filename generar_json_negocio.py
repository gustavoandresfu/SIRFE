import json
from typing import List
from modelos import Cluster, FunctionalSpecification, FunctionalCapability, GherkinScenario, TechnicalSupport

# Definición de Capacidades de Negocio
BUSINESS_CAPABILITIES = {
    0: {
        "id": "UX-001",
        "titulo": "Personalización y Experiencia del Usuario",
        "historia": "Como usuario, quiero que el sistema adapte la interfaz y mis preferencias para trabajar de forma eficiente.",
        "objetivos": [
            "Adaptar el idioma y la dirección de la interfaz según el perfil",
            "Mantener la persistencia de las preferencias de visualización",
            "Personalizar el acceso a menús y funciones rápidas"
        ]
    },
    1: {
        "id": "DATA-001",
        "titulo": "Gobierno y Ciclo de Vida de los Datos",
        "historia": "Como administrador de datos, quiero asegurar que la información se cree, actualice y elimine bajo estrictas reglas de integridad.",
        "objetivos": [
            "Garantizar la consistencia atómica en la creación y modificación de registros",
            "Asegurar la trazabilidad total de los cambios (Auditoría)",
            "Gestionar la sincronización del modelo de datos con el almacenamiento"
        ]
    },
    2: {
        "id": "SEC-001",
        "titulo": "Control de Acceso y Gestión de Sesiones",
        "historia": "Como oficial de seguridad, quiero controlar quién y desde dónde se accede al sistema para prevenir intrusiones.",
        "objetivos": [
            "Validar las opciones de inicio de sesión (IP, dispositivos, cookies)",
            "Controlar el umbral de intentos fallidos para mitigar ataques",
            "Gestionar la vigencia y renovación de los tokens de acceso"
        ]
    },
    3: {
        "id": "SEC-002",
        "titulo": "Seguridad Criptográfica de la Identidad",
        "historia": "Como sistema seguro, quiero que la información sensible sea irreversible y protegida ante ingeniería inversa.",
        "objetivos": [
            "Transformar credenciales en huellas digitales seguras (Hashing)",
            "Validar la integridad de las claves sin exponer su contenido original",
            "Aplicar políticas de retardo para dificultar ataques automatizados"
        ]
    }
}

def generar_especificacion(
    clusters: List[Cluster], 
    proyecto: str = "Análisis de Sistema Legado (Reingeniería)",
    metodologia: str = "Análisis Semántico por Representación Intermedia"
) -> FunctionalSpecification:
    
    capacidades_funcionales = []
    
    for cluster in clusters:
        cluster_id = cluster.id
        cap = BUSINESS_CAPABILITIES.get(cluster_id)
        
        if not cap:
            continue
        
        # Enriquecemos la capacidad con los datos del cluster
        roles = list(set(m.ir.role for m in cluster.methods))
        contexts = list(set(m.ir.context for m in cluster.methods))
        metodos_sustento = [f"{m.class_name}.{m.method}" for m in cluster.methods]
        
        escenario = GherkinScenario(
            dado=f"Que el sistema requiere {cap['titulo'].lower()} con políticas de {', '.join(roles).lower()}",
            cuando=f"Se procesan solicitudes en el dominio de {', '.join(contexts).lower()}",
            entonces=cap["objetivos"],
            y="Garantizar la resiliencia ante estados inconsistentes"
        )
        
        sustento = TechnicalSupport(
            cantidad_metodos=len(metodos_sustento),
            metodos=metodos_sustento
        )
        
        func_cap = FunctionalCapability(
            id=cap["id"],
            titulo=cap["titulo"],
            historia_usuario=cap["historia"],
            escenario_gherkin_sintetizado=escenario,
            sustento_tecnico=sustro if (sustro := sustento) else sustento
        )
        
        capacidades_funcionales.append(func_cap)
        
    return FunctionalSpecification(
        proyecto=proyecto,
        metodologia=metodologia,
        capacidades_funcionales=capacidades_funcionales
    )

if __name__ == "__main__":
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
                
    print("Especificación FUNCIONAL en JSON generada exitosamente.")

import json
import os
from typing import List, Dict, Any
from modelos import SemanticUnit, FunctionalSpecification

def validar_metodologia(units: List[SemanticUnit], especificacion: FunctionalSpecification) -> Dict[str, Any]:
    total_unidades = len(units)
    if total_unidades == 0:
        return {
            "resumen_estadistico": {
                "total_unidades_analizadas": 0,
                "unidades_unicas_mapeadas": 0,
                "cobertura_unidades": "0.00%",
                "lineas_codigo_totales": 0
            },
            "evaluacion_honestidad_sir": {
                "confianza_promedio_general": 0.0,
                "roles_alta_confianza_pct": "0.00%",
                "posibles_falsos_positivos": 0
            },
            "distribucion_roles": {},
            "conclusiones_tesis": ["No se analizaron unidades."]
        }

    # 1. Trazabilidad de unidades y líneas de código
    unidades_mapeadas = set()
    for cap in especificacion.capacidades_funcionales:
        # Extraer el identificador limpio del sustento técnico
        # El sustento técnico tiene cadenas como "Clase.metodo (L10-20 en archivo.py)"
        # Podemos rastrear coincidencia simple buscando el nombre del método
        for u_sustento in cap.sustento_tecnico.unidades:
            parts = u_sustento.split(" ")
            if parts:
                name_part = parts[0]
                unidades_mapeadas.add(name_part)

    # Coincidencia con trazabilidad
    mapeadas_count = 0
    lineas_totales = 0
    for u in units:
        full_name = f"{u.traceability.class_name + '.' if u.traceability.class_name else ''}{u.traceability.name}"
        if full_name in unidades_mapeadas:
            mapeadas_count += 1
        lineas_totales += (u.traceability.end_line - u.traceability.start_line + 1)

    cobertura_unidades = (mapeadas_count / total_unidades) * 100

    # 2. Honestidad Metodológica (Análisis de Confidence Scores de la SIR)
    total_roles = 0
    suma_confianza = 0.0
    roles_alta_confianza = 0
    posibles_falsos_positivos = 0
    
    roles_dist = {}
    roles_conf_sum = {}
    roles_conf_count = {}

    for u in units:
        for r_entry in u.roles:
            role = r_entry["role"]
            conf = r_entry["confidence"]
            
            total_roles += 1
            suma_confianza += conf
            
            if conf >= 0.8:
                roles_alta_confianza += 1
            if conf < 0.6:
                posibles_falsos_positivos += 1
                
            roles_dist[role] = roles_dist.get(role, 0) + 1
            roles_conf_sum[role] = roles_conf_sum.get(role, 0.0) + conf
            roles_conf_count[role] = roles_conf_count.get(role, 0) + 1

    confianza_promedio = suma_confianza / total_roles if total_roles > 0 else 0.0
    alta_confianza_pct = (roles_alta_confianza / total_roles) * 100 if total_roles > 0 else 0.0

    roles_conf_promedio = {}
    for role in roles_dist:
        roles_conf_promedio[role] = f"{roles_conf_sum[role] / roles_conf_count[role]:.2f}"

    # 3. Métricas de Estructura e Inferencias de Flujo
    unidades_con_precondiciones = sum(1 for u in units if u.preconditions)
    cobertura_precondiciones = (unidades_con_precondiciones / total_unidades) * 100

    # 4. Reporte y Conclusiones para la Tesis
    reporte = {
        "resumen_estadistico": {
            "total_unidades_analizadas": total_unidades,
            "unidades_mapeadas_exitosamente": mapeadas_count,
            "cobertura_unidades": f"{cobertura_unidades:.2f}%",
            "lineas_codigo_totales": lineas_totales
        },
        "evaluacion_honestidad_sir": {
            "confianza_promedio_general": f"{confianza_promedio:.2f}",
            "roles_alta_confianza_pct": f"{alta_confianza_pct:.2f}%",
            "posibles_falsos_positivos": posibles_falsos_positivos,
            "roles_conf_promedio": roles_conf_promedio
        },
        "indicadores_de_flujo": {
            "unidades_con_precondiciones": unidades_con_precondiciones,
            "cobertura_precondiciones_gherkin": f"{cobertura_precondiciones:.2f}%"
        },
        "distribucion_roles": roles_dist,
        "conclusiones_tesis": [
            f"La SIR demuestra una trazabilidad del {cobertura_unidades:.2f}% de las unidades de código sobre las capacidades identificadas.",
            f"El {alta_confianza_pct:.2f}% de las asignaciones de roles cumple con el criterio de alta confianza (>= 0.80).",
            f"Se extrajeron condiciones de guarda (precondiciones) para el {cobertura_precondiciones:.2f}% de la base de código legacy.",
            f"Se identificaron {posibles_falsos_positivos} roles con baja confianza (< 0.60), candidatos a refinamiento de heurísticas."
        ]
    }
    return reporte

if __name__ == "__main__":
    ir_path = "representacion_intermedia_semantica.json"
    spec_path = "especificacion_funcional.json"
    
    if not os.path.exists(ir_path) or not os.path.exists(spec_path):
        print("Error: Faltan archivos de datos para la validación.")
    else:
        with open(ir_path, "r", encoding="utf-8") as f:
            units_data = json.load(f)
            units = [SemanticUnit.from_dict(u) for u in units_data]
            
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_data = json.load(f)
            especificacion = FunctionalSpecification.from_dict(spec_data)

        reporte = validar_metodologia(units, especificacion)

        with open("reporte_validacion_tesis.json", "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=4, ensure_ascii=False)
        
        print("-" * 50)
        print("REPORTE DE VALIDACIÓN METODOLÓGICA PARA TESIS GENERADO")
        print(f"Cobertura Unidades: {reporte['resumen_estadistico']['cobertura_unidades']}")
        print(f"Confianza Promedio: {reporte['evaluacion_honestidad_sir']['confianza_promedio_general']}")
        print(f"Cobertura Precondiciones: {reporte['indicadores_de_flujo']['cobertura_precondiciones_gherkin']}")
        print("-" * 50)

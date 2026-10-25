import os
import json
import argparse
from typing import List

# Importar funciones refactorizadas
from analizar_codigo_legacy import analizar
from clustering_ir import clusterizar
from generar_json_negocio import generar_especificacion
from validar_metodologia import validar_metodologia

def main():
    parser = argparse.ArgumentParser(description="Orquestador del Pipeline SIR-FE (Semantic Intermediate Representation for Functional Extraction)")
    parser.add_argument("path", help="Ruta al archivo .py o directorio de la aplicación legacy")
    parser.add_argument("--method", help="Filtrar análisis por un método específico", default=None)
    parser.add_argument("--config", help="Ruta al archivo de configuración del analizador", default="config_analizador.json")
    parser.add_argument("--output-dir", help="Directorio donde guardar los reportes JSON", default=".")
    parser.add_argument("--no-write", help="Ejecutar pipeline completamente en memoria sin escribir JSONs", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("INICIANDO PIPELINE SIR-FE")
    print(f"Ruta objetivo: {args.path}")
    print(f"Configuración: {args.config}")
    print("=" * 60)

    # 1. Abstracción Sintáctica y Semántica (AST -> IR)
    print("\n[Paso 1/4] Analizando código fuente y abstrayendo AST a IR...")
    metodos = analizar(args.path, config_path=args.config, filter_method=args.method)
    print(f"-> Se extrajeron {len(metodos)} métodos con representaciones semánticas.")

    if not metodos:
        print("No se encontraron métodos para procesar. Abortando pipeline.")
        return

    # 2. Clustering de Comportamiento (K-Means)
    print("\n[Paso 2/4] Agrupando comportamientos similares (Clustering K-Means)...")
    clusters = clusterizar(metodos)
    print(f"-> Se generaron {len(clusters)} clusters basados en firmas semánticas.")

    # 3. Síntesis Funcional de Negocio (Generación Gherkin / Historias)
    print("\n[Paso 3/4] Sintetizando capacidades funcionales e historias de usuario...")
    especificacion = generar_especificacion(clusters)
    print(f"-> Se sintetizaron {len(especificacion.capacidades_funcionales)} capacidades funcionales.")

    # 4. Auditoría y Métricas para Tesis (Validación)
    print("\n[Paso 4/4] Validando metodología y calculando KPIs...")
    reporte = validar_metodologia(metodos, especificacion)

    # Escribir archivos si no se especificó --no-write
    if not args.no_write:
        os.makedirs(args.output_dir, exist_ok=True)
        
        ir_out = os.path.join(args.output_dir, "representacion_intermedia_semantica.json")
        clusters_out = os.path.join(args.output_dir, "clusters_ir.json")
        spec_out = os.path.join(args.output_dir, "especificacion_funcional.json")
        reporte_out = os.path.join(args.output_dir, "reporte_validacion_tesis.json")

        with open(ir_out, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in metodos], f, indent=4, ensure_ascii=False)
            
        with open(clusters_out, "w", encoding="utf-8") as f:
            json.dump({"clusters": [c.to_dict() for c in clusters]}, f, indent=4, ensure_ascii=False)
            
        with open(spec_out, "w", encoding="utf-8") as f:
            json.dump(especificacion.to_dict(), f, indent=4, ensure_ascii=False)
            
        with open(reporte_out, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=4, ensure_ascii=False)

        print(f"\n[OK] Archivos de salida escritos exitosamente en '{args.output_dir}':")
        print(f"  - Representación Semántica: {ir_out}")
        print(f"  - Clusters de Comportamiento: {clusters_out}")
        print(f"  - Especificación Funcional (Gherkin): {spec_out}")
        print(f"  - Reporte de Tesis (KPIs): {reporte_out}")

    # Mostrar reporte consolidado en consola
    print("\n" + "=" * 50)
    print("REPORTE CONSOLIDADO DE VALIDACIÓN (SIR-FE)")
    print("=" * 50)
    resumen = reporte["resumen_estadistico"]
    honestidad = reporte["evaluacion_honestidad_sir"]
    flujo = reporte["indicadores_de_flujo"]
    print(f"Total unidades analizadas  : {resumen['total_unidades_analizadas']}")
    print(f"Unidades mapeadas a caps   : {resumen['unidades_mapeadas_exitosamente']}")
    print(f"Cobertura de Unidades      : {resumen['cobertura_unidades']}")
    print(f"Confianza Promedio (SIR)   : {honestidad['confianza_promedio_general']}")
    print(f"Líneas de Código Totales   : {resumen['lineas_codigo_totales']}")
    print(f"Cobertura Precondiciones   : {flujo['cobertura_precondiciones_gherkin']}")
    print("-" * 50)
    print("Distribución de Roles Semánticos:")
    for role, count in reporte["distribucion_roles"].items():
        print(f"  - {role:12}: {count}")
    print("=" * 50)

if __name__ == "__main__":
    main()

# SIR-FE: Semantic Intermediate Representation for Functional Extraction

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-research--prototype-yellow.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-9%20passed-success.svg)](tests/)

> **Aviso de alcance**: **SIR-FE es un prototipo experimental de investigación académica (Proof of Concept - PoC)** desarrollado en el contexto de una tesis de grado en Reingeniería de Software. **No es una herramienta lista para producción** ni un generador automático de suites de pruebas ejecutables.

---

## 📌 Contexto del Proyecto

El proyecto explora la viabilidad de una metodología asistida para analizar código fuente heredado (*legacy*) en Python y extraer, mediante análisis estático y agrupamiento algorítmico, candidatos estructurados de especificaciones funcionales en formato Gherkin.

El objetivo central de la investigación es evaluar si una **Representación Intermedia Semántica (SIR)** basada en roles y patrones sintácticos puede servir como punto de partida útil para que un auditor o analista de software documente y comprenda sistemas legados con menor esfuerzo cognitivo.

---

## ⚙️ ¿Qué hace actualmente el prototipo?

El sistema implementa un pipeline de cuatro pasos secuenciales:

```
Código Python (.py) ──> [1. AST a SIR] ──> [2. Vectorización y Clustering] ──> [3. Síntesis Textual] ──> [4. Telemetría]
```

1. **Análisis Sintáctico y Extracción de IR (`analizar_codigo_legacy.py`)**:
   * Recorre el Árbol de Sintaxis Abstracta (AST) con `ast.NodeVisitor`.
   * Extrae atributos locales de funciones y métodos: nombres de argumentos, retornos, excepciones lanzadas/capturadas, condiciones en sentencias `If` y `Assert`, y llamadas a métodos.
   * Asigna roles heurísticos preliminares (`VALIDATOR`, `PERSISTER`, `EXTRACTOR`, `TRANSFORMER`) según patrones sintácticos predefinidos.
2. **Vectorización y Agrupamiento (`clustering_ir.py`)**:
   * Convierte los atributos extraídos en vectores numéricos mediante codificación *one-hot* / *multi-hot* y pesos asignados por configuración.
   * Agrupa métodos con firmas de comportamiento similares utilizando algoritmos de clustering no supervisado (`K-Means`, `Agglomerative`, `DBSCAN`) de `scikit-learn`.
3. **Síntesis Funcional Preliminar (`generar_json_negocio.py`)**:
   * Ensambla plantillas textuales declarativas con formato de Historia de Usuario y escenarios tipo Gherkin (`Dado / Cuando / Entonces / Y`) agregando las acciones, precondiciones y postcondiciones detectadas en cada cluster.
4. **Métricas Internas de Auditoría (`validar_metodologia.py`)**:
   * Calcula indicadores cuantitativos simples sobre los métodos analizados, líneas de código cubiertas y estadísticas de las heurísticas ejecutadas.

---

## 📦 Artefactos que produce

Al ejecutar el pipeline, se generan cuatro archivos JSON estructurados:

| Archivo Generado | Contenido y Propósito |
| :--- | :--- |
| `representacion_intermedia_semantica.json` | Lista detallada de cada método analizado con su trazabilidad (archivo, líneas), roles asignados, precondiciones textuales, entradas, salidas y efectos de estado detectados. |
| `clusters_ir.json` | Agrupamiento de las unidades semánticas organizadas por identificador de cluster numérico. |
| `especificacion_funcional.json` | Especificación funcional preliminar con historias de usuario y escenarios Gherkin generados a partir de plantillas parametrizadas. |
| `reporte_validacion_tesis.json` | Reporte cuantitativo con el total de métodos procesados, líneas analizadas, porcentaje de métodos vinculados a clusters y promedios de las puntuaciones heurísticas. |

---

## 🚫 ¿Qué NO resuelve todavía el proyecto? (Límites Técnicos)

Para una evaluación técnica honesta, es importante señalar los límites actuales del prototipo:

* **No genera pruebas automatizadas ejecutables**: Los escenarios Gherkin generados son plantillas textuales descriptivas. No contienen código ejecutable (*step definitions*) ni interactúan con motores como *Behave* o *pytest-bdd*. Para convertirlos en pruebas reales, un ingeniero debe programar los pasos y aserciones.
* **No comprende la semántica profunda del negocio**: El análisis se basa estrictamente en la sintaxis del código y en coincidencia de cadenas de texto (nombres de funciones, llamadas a `.write()`, verbos comunes). Si el código usa identificadores genéricos o no estándar, la inferencia semántica se degrada a valores por defecto (`GENERIC`).
* **Análisis estrictamente intraprocedural**: Cada método se analiza de forma aislada. El prototipo no construye grafos de llamadas entre métodos (*call graphs*), no analiza flujo de datos entre módulos (*data-flow*) ni resuelve alias de variables o herencias complejas.
* **El clustering es sintáctico, no conceptual**: El algoritmo agrupa métodos basándose en la similitud de sus vectores de características sintácticas; no garantiza que los métodos agrupados correspondan a un mismo caso de uso o proceso de negocio real.
* **Exclusivo para Python 3**: La extracción depende directamente del módulo nativo `ast` de Python, por lo que no analiza aplicaciones escritas en otros lenguajes.

---

## 🔬 Distinción Metodológica: Resultados Medidos, Heurísticas e Hipótesis

Para evitar afirmaciones desmedidas sobre validación o novedad, se distinguen explícitamente tres niveles en el proyecto:

### 1. Resultados Medidos (Métricas empíricas del analizador)
* **Cantidad de unidades procesadas**: Recuento de métodos y funciones exitosamente parseados por el AST.
* **Volumen de código analizado**: Líneas de código (LoC) comprendidas entre el inicio y fin de cada nodo analizado.
* **Cobertura sintáctica de asignación**: Porcentaje de métodos del código fuente analizado que fueron incorporados en algún cluster de la especificación final.
* **Tasa de precondiciones detectadas**: Proporción de métodos que contienen sentencias `If` con cortes o `Assert`.

### 2. Heurísticas Implementadas (Reglas prefijadas en código)
* **Puntuaciones de "Confianza" (`confidence`)**: Los valores numéricos (ej. `0.95` para persistencia al detectar `.write()`, `0.80` para validadores con `raise`, `0.50` por defecto) **son pesos asignados por reglas fijas en el código**, no probabilidades estadísticas ni precisiones calculadas empíricamente.
* **Detección de roles por subcadenas**: Identificación de verbos y palabras clave mediante expresiones regulares y diccionarios estáticos definidos en `config_analizador.json`.
* **Asignación de dominio funcional**: Clasificación heurística basada en palabras clave en el nombre del método o clase (`identity`, `storage`, `ui_config`).

### 3. Hipótesis de Investigación (Pendientes de validación empírica formal)
* **Hipótesis 1**: Una representación intermedia estructurada (SIR) reduce el tiempo que requiere un desarrollador para comprender la lógica de métodos legados desconocidos.
* **Hipótesis 2**: Las firmas de comportamiento sintáctico permiten agrupar métodos de forma coherente con la arquitectura funcional del sistema.
* **Hipótesis 3**: Las plantillas Gherkin sintetizadas sirven como un borrador útil para que analistas y equipos de QA diseñen especificaciones funcionales formales.

> *Nota metodológica: La validación formal de estas hipótesis requiere futuros estudios empíricos con desarrolladores humanos y benchmarks anotados manualmente con ground truth.*

---

## 🚀 Instalación y Ejemplo Reproducible

### Requisitos Previos
* **Python 3.10** o superior.
* `git` y `pip`.

### 1. Clonar e Instalar Entorno
```bash
# Clonar el repositorio
git clone https://github.com/gustavoandresfu/SIRFE.git
cd SIRFE

# Crear y activar entorno virtual
# En Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias requeridas (numpy, scikit-learn, scipy)
pip install -r requirements.txt
```

### 2. Ejecutar Ejemplo de Demostración
El repositorio incluye un archivo de muestra en [`ejemplos/servicio_autenticacion.py`](ejemplos/servicio_autenticacion.py).

> **Sobre este ejemplo**: Es un módulo sintético diseñado a propósito para ilustrar cómo el analizador reacciona ante diferentes estructuras sintácticas (una guarda con `raise`, una mutación de diccionario en `self`, una llamada a `.write()` simulada y un retorno booleano). Permite verificar el pipeline de principio a fin de manera controlada y en menos de dos segundos.

```bash
python orquestador.py ejemplos/servicio_autenticacion.py --output-dir salida_demo
```

**Salida en consola:**
```text
============================================================
INICIANDO PIPELINE SIR-FE
Ruta objetivo: ejemplos/servicio_autenticacion.py
Configuración: config_analizador.json
============================================================

[Paso 1/4] Analizando código fuente y abstrayendo AST a IR...
-> Se extrajeron 5 métodos con representaciones semánticas.

[Paso 2/4] Agrupando comportamientos similares (Clustering K-Means)...
-> Se generaron 4 clusters basados en firmas semánticas.

[Paso 3/4] Sintetizando capacidades funcionales e historias de usuario...
-> Se sintetizaron 4 capacidades funcionales.

[Paso 4/4] Validando metodología y calculando KPIs...

[OK] Archivos de salida escritos exitosamente en 'salida_demo':
  - Representación Semántica: salida_demo/representacion_intermedia_semantica.json
  - Clusters de Comportamiento: salida_demo/clusters_ir.json
  - Especificación Funcional (Gherkin): salida_demo/especificacion_funcional.json
  - Reporte de Tesis (KPIs): salida_demo/reporte_validacion_tesis.json

==================================================
REPORTE CONSOLIDADO DE VALIDACIÓN (SIR-FE)
==================================================
Total unidades analizadas  : 5
Unidades mapeadas a caps   : 5
Cobertura de Unidades      : 100.00%
Confianza Promedio (SIR)   : 0.86
Líneas de Código Totales   : 34
Cobertura Precondiciones   : 80.00%
--------------------------------------------------
Distribución de Roles Semánticos:
  - EXTRACTOR   : 5
  - VALIDATOR   : 4
  - PERSISTER   : 1
  - TRANSFORMER : 1
==================================================
```

### 3. Ejecución en Memoria (Sin escribir archivos)
Para inspeccionar un archivo sin generar archivos JSON en disco:
```bash
python orquestador.py ejemplos/servicio_autenticacion.py --no-write
```

---

## 🧪 Suite de Pruebas

El repositorio incluye un conjunto de pruebas unitarias y de integración implementado con el framework nativo `unittest`, sin herramientas externas adicionales:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Casos Cubiertos:
* [`tests/test_analizador.py`](tests/test_analizador.py): Verifica la extracción de nodos AST, asignación de roles heurísticos, detección de guardas condicionales y cambios de estado en memoria y persistencia.
* [`tests/test_clustering.py`](tests/test_clustering.py): Comprueba la consistencia del vectorizador `FeatureExtractor` y el comportamiento de los algoritmos de clustering con listas normales y vacías.
* [`tests/test_sintesis_negocio.py`](tests/test_sintesis_negocio.py): Valida la generación de estructuras `FunctionalCapability`, campos Gherkin (`Dado`, `Cuando`, `Entonces`, `Y`) y metadatos de trazabilidad.
* [`tests/test_validacion.py`](tests/test_validacion.py): Evalúa el cómputo de métricas metodológicas internas.
* [`tests/test_pipeline_integracion.py`](tests/test_pipeline_integracion.py): Ejecuta el flujo completo de las cuatro etapas en memoria de principio a fin.

---

## 📂 Estructura del Repositorio

```text
SIRFE/
├── orquestador.py                  # CLI y coordinador del pipeline
├── analizar_codigo_legacy.py       # Extractor estático de AST a SIR
├── clustering_ir.py                # Vectorización de características y clustering
├── generar_json_negocio.py         # Generación de historias y plantillas Gherkin
├── validar_metodologia.py          # Cálculo de métricas y telemetría interna
├── modelos.py                      # Clases de datos tipadas (Dataclasses)
├── config_analizador.json          # Perfiles de palabras clave y heurísticas
├── requirements.txt                # Dependencias (numpy, scikit-learn, scipy)
├── LICENSE                         # Licencia de código abierto MIT
├── ejemplos/
│   └── servicio_autenticacion.py   # Módulo sintético de muestra para pruebas
├── tests/                          # Suite de pruebas unitarias e integración
│   ├── test_analizador.py
│   ├── test_clustering.py
│   ├── test_pipeline_integracion.py
│   ├── test_sintesis_negocio.py
│   └── test_validacion.py
└── documentacion/                  # Documentación teórica y estado del arte
    ├── ESTADO_DEL_ARTE.md
    ├── MARCO_TEORICO.md
    └── METODOLOGIA.md
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

# Extracción de casos de prueba en formato Gherkin a partir de código fuente de aplicaciones legacy
## Metodología SIR-FE: Semantic Intermediate Representation for Functional Extraction

## 1. Introducción
La metodología SIR-FE propone un marco de trabajo para la reingeniería de software legado, centrándose en la extracción automática de requerimientos funcionales a partir del análisis semántico del código fuente.

## 2. Fases de la Metodología

### Fase I: Abstracción Sintáctica (AST)
*   **Acción**: Transformación del código fuente en un Árbol de Sintaxis Abstracta (AST).
*   **Propósito**: Eliminar la dependencia de la sintaxis del lenguaje y permitir un análisis estructural puro.

### Fase II: Clasificación Semántica Intermedia (IR)
Se define una representación intermedia basada en cuatro dimensiones:
1.  **Rol Estructural**: Clasificación por intención (GUARD, PERSISTER, TRANSFORMER, EXTRACTOR).
2.  **Efecto Sistémico**: Impacto en el estado (MUTABLE, STABLE, SIGNAL).
3.  **Tipo de Operación**: Complejidad lógica (SEQUENTIAL, BRANCHING).
4.  **Contexto de Dominio**: Área de impacto (IDENTITY, STORAGE, UI).

### Fase III: Clustering de Comportamiento Algorítmico
*   **Técnica**: Vectorización de la IR y agrupamiento mediante K-Means.
*   **Hipótesis**: Los métodos que comparten una firma semántica idéntica o similar pertenecen a la misma capacidad funcional de negocio, independientemente de su ubicación física en los archivos.

### Fase IV: Síntesis Funcional de Negocio
*   **Acción**: Mapeo de clusters a Historias de Usuario y Escenarios Gherkin.
*   **Entregable**: Especificación Funcional Estructurada (JSON).

## 3. Métricas de Evaluación (KPIs)
Para validar la efectividad de la metodología, se proponen:
1.  **Índice de Cobertura Funcional**: Porcentaje de lógica de impacto capturada.
2.  **Precisión de Clasificación**: Validación contra el criterio de un experto humano.
3.  **Eficiencia Temporal**: Reducción del tiempo de documentación comparado con métodos manuales.

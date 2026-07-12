# Extracción de casos de prueba en formato Gherkin a partir de código fuente de aplicaciones legacy

Este proyecto implementa la metodología **SIR-FE** (*Semantic Intermediate Representation for Functional Extraction*), diseñada para la extracción automática de inteligencia de negocio a partir de sistemas legados.

## 🎯 Propósito Académico
Este prototipo sirve como base para la investigación en Reingeniería de Software, centrada en eliminar la brecha semántica entre el código fuente y las especificaciones funcionales.

## ⚙️ Arquitectura de la Metodología
El sistema opera en cuatro capas jerárquicas:
1.  **Sintáctica**: Extracción de AST en JSON.
2.  **Semántica**: Clasificación por Roles (GUARD, PERSISTER, etc.).
3.  **Algorítmica**: Clustering por ADN de comportamiento (K-Means).
4.  **Funcional**: Síntesis de Historias de Usuario en JSON.

## 📊 Evaluación y Métricas de Tesis
Para validar la eficacia de la metodología, el sistema incluye un módulo de auditoría (`validar_metodologia.py`) que mide los siguientes KPIs:

### 1. Índice de Cobertura Total
Mide el porcentaje de métodos del código fuente que han sido exitosamente sintetizados en capacidades de negocio. 
*   **Significado**: Un alto porcentaje garantiza que no hay "lagunas de conocimiento" en la documentación generada.

### 2. Cobertura Crítica (Lógica de Impacto)
Se centra exclusivamente en los métodos con efecto **MUTABLE** (los que alteran el estado del sistema).
*   **Significado**: Asegura que el 100% de las acciones que modifican datos han sido capturadas y explicadas funcionalmente.

### 3. Densidad de Roles Semánticos
Provee una radiografía de la naturaleza del software:
*   **GUARDS**: Puntos de control y seguridad.
*   **TRANSFORMERS**: Motores de cálculo y reglas de negocio.
*   **PERSISTERS**: Operaciones de almacenamiento.

## 🚀 Guía de Uso (CLI)

El motor ahora soporta ejecución dinámica desde la terminal:

### Modo Masivo (Toda una carpeta)
```bash
python analizar_codigo_legacy.py trytond/trytond/res/
```

### Modo Quirúrgico (Un solo archivo)
```bash
python analizar_codigo_legacy.py trytond/trytond/res/user.py
```

### Modo Ultra-Específico (Solo un método)
```bash
python analizar_codigo_legacy.py trytond/trytond/res/user.py --method set_password
```

## 📂 Estructura de Archivos
*   `METODOLOGIA.md`: Marco teórico y formalización académica.
*   `analizar_codigo_legacy.py`: Motor de análisis universal.
*   `validar_metodologia.py`: Generador de métricas para la tesis.
*   `especificacion_funcional.json`: El producto final de negocio.
*   `reporte_validacion_tesis.json`: Datos cuantitativos para la defensa.

---
*Documentación generada automáticamente mediante el análisis de ADN de código.*

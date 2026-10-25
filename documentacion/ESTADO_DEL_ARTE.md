# Estado del Arte: Recuperación de Especificaciones y Casos de Prueba

Este documento resume investigaciones y marcos teóricos de referencia relacionados con la extracción de conocimiento desde sistemas legados, situando la propuesta metodológica de SIR-FE en el contexto académico contemporáneo.

## 1. Ingeniería Inversa Clásica y Recuperación de Lógica
La extracción de lógica de negocio desde el código fuente es un área clásica de estudio en la ingeniería de software:
*   **Sneed, H. M. (2004):** En *"Reverse Engineering of Business Logic from Source Code"*, Sneed establece pautas para identificar reglas de negocio dispersas en sistemas heredados. SIR-FE explora esta dirección sustituyendo la inspección manual por una aproximación asistida basada en clasificación heurística de roles semánticos en el AST.
*   **Chikofsky & Cross (1990):** Definieron la Ingeniería Inversa como el proceso de identificar componentes y sus interrelaciones para crear representaciones en niveles de abstracción más altos. En este trabajo, el formato Gherkin se investiga como una representación declarativa intermedia en ese nivel superior de abstracción.

## 2. Recuperación de Especificaciones (Specification Recovery)
El área de recuperación de especificaciones busca aproximar el comportamiento de un sistema a partir de sus artefactos de implementación:
*   **Ammons, G., et al. (2002):** En *"Mining Specifications"*, se propone el aprendizaje de protocolos de interacción a partir de trazas de ejecución. SIR-FE explora una variante estática complementaria mediante **Clustering de Firmas Semánticas**, agrupando métodos que exhiben perfiles sintácticos similares.
*   **Ernst, M. D., et al. (2001):** Con la herramienta **Daikon**, introdujeron la detección dinámica de invariantes en tiempo de ejecución. SIR-FE plantea una alternativa preliminar basada exclusivamente en **Análisis Estático (AST)** para extraer condiciones de guardia sin requerir la ejecución del sistema legado, lo cual es útil en entornos donde preparar el entorno de ejecución resulta costoso o inviable.

## 3. Generación y Recuperación de Pruebas en Sistemas Legados
*   **Michael Feathers (2004):** En *"Working Effectively with Legacy Code"*, Feathers conceptualiza los **Characterization Tests** (Pruebas de Caracterización) como el mecanismo para documentar el comportamiento observable de un sistema antes de refactorizarlo.
    *   *Hipótesis de SIR-FE:* Mientras que la práctica tradicional de caracterización es eminentemente manual, este proyecto investiga la viabilidad de generar **candidatos preliminares de escenarios de caracterización** en formato Gherkin para acelerar la labor del ingeniero.
*   **Tonella, P. (2005):** En *"Recent Advances in Software Testing"*, revisa los avances en ingeniería inversa orientada al testing. SIR-FE busca explorar la articulación entre el análisis sintáctico técnico y los formatos orientados a comportamiento (BDD).

## 4. Oportunidad en la Literatura: El Salto a Formatos Declarativos BDD
La revisión de la literatura indica que la mayor parte de las herramientas de generación y recuperación de pruebas (como Randoop o EvoSuite) se concentran en pruebas unitarias técnicas (assertions a bajo nivel) y no en la legibilidad conceptual para analistas funcionales:
*   Existe una oportunidad de investigación en la síntesis asistida de representaciones en formato **BDD (Behavior-Driven Development)** a partir de código legacy.
*   SIR-FE se plantea como una **hipótesis de contribución metodológica**: evaluar en qué medida el uso de Gherkin como lenguaje puente declarativo facilita la comunicación entre auditores técnicos y analistas de negocio, requiriendo validación empírica posterior para medir su eficacia real frente a métodos manuales.

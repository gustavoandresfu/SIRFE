# Estado del Arte: Recuperación de Especificaciones y Casos de Prueba

Este documento resume las investigaciones y marcos teóricos existentes relacionados con la extracción de conocimiento desde sistemas legados, situando la metodología SIR-FE en el contexto académico actual.

## 1. Ingeniería Inversa Clásica y Recuperación de Lógica
La extracción de lógica de negocio desde el código fuente no es un problema nuevo, pero ha evolucionado en sus objetivos:
*   **Sneed, H. M. (2004):** En *"Reverse Engineering of Business Logic from Source Code"*, Sneed establece las bases para identificar reglas de negocio dispersas. SIR-FE hereda esta visión, pero reemplaza los modelos manuales por una clasificación automática basada en roles semánticos.
*   **Chikofsky & Cross (1990):** Definieron la Ingeniería Inversa como el proceso de identificar componentes y sus relaciones para crear representaciones en niveles de abstracción más altos. SIR-FE utiliza el formato Gherkin como ese "nivel de abstracción superior".

## 2. Recuperación de Especificaciones (Specification Recovery)
El campo que busca deducir qué "debería" hacer un sistema basándose en lo que "hace" actualmente:
*   **Ammons, G., et al. (2002):** En *"Mining Specifications"*, se propone el aprendizaje de protocolos de interacción. SIR-FE aplica un concepto similar mediante **Clustering Semántico**, buscando no solo protocolos, sino intenciones funcionales.
*   **Ernst, M. D., et al. (2001):** Con la herramienta **Daikon**, introdujeron la detección dinámica de invariantes. SIR-FE propone una alternativa mediante **Análisis Estático (AST)**, eliminando la necesidad de ejecutar el sistema legado, lo cual suele ser una barrera en entornos obsoletos.

## 3. Generación de Casos de Prueba desde Sistemas Legados
*   **Michael Feathers (2004):** En su obra fundamental *"Working Effectively with Legacy Code"*, Feathers introduce los **Characterization Tests** (Pruebas de Caracterización) como el método para documentar el comportamiento actual de un sistema. 
    *   *Aporte de SIR-FE:* Mientras Feathers propone un proceso manual y artesanal, esta tesis propone la **automatización de la caracterización** exportando los resultados directamente a Gherkin.
*   **Tonella, P. (2005):** En *"Recent Advances in Software Testing"*, explora la ingeniería inversa aplicada al testing. La metodología SIR-FE cierra la brecha entre el testing técnico y el testing de negocio (BDD).

## 4. El Vacío en la Literatura: El Salto a Gherkin/BDD
La búsqueda bibliográfica confirma que existe un vacío en la generación automática de formatos **BDD (Behavior-Driven Development)** a partir de código legacy. 
*   La mayoría de las herramientas de generación de pruebas se enfocan en *Unit Testing* técnico (JUnit, PyTest) y no en la legibilidad funcional.
*   SIR-FE se posiciona como una **contribución original** al utilizar Gherkin como lenguaje puente, facilitando la comunicación entre el equipo de modernización y los expertos de dominio (Business Analysts).

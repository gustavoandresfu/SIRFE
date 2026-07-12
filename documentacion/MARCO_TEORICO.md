# Extracción de casos de prueba en formato Gherkin a partir de código fuente de aplicaciones legacy
## Marco Teórico: Metodología SIR-FE

## 1. Ingeniería Inversa y Mantenimiento de Sistemas Legados
El mantenimiento de sistemas legados representa uno de los mayores desafíos en la ingeniería de software actual. Según **Parnas (1994)**, el "Software Aging" ocurre debido a la falta de actualización de los requerimientos y la pérdida de conocimiento sobre la arquitectura original.

*   **Ingeniería Inversa:** Proceso de análisis de un sistema para identificar sus componentes y sus interrelaciones, creando representaciones en un nivel de abstracción más alto (Chikofsky & Cross).
*   **Recuperación de Conceptos (Concept Location):** Técnica para identificar qué partes del código fuente implementan un concepto específico del dominio de negocio.

## 2. Análisis Estático y Abstracción Sintáctica
La base técnica de SIR-FE reside en el análisis estático de código, que permite examinar el comportamiento del software sin ejecutarlo.

*   **Abstract Syntax Tree (AST):** Una representación jerárquica de la estructura sintáctica del código fuente. El AST permite una navegación estructural que trasciende la simple lectura de texto, facilitando la identificación de patrones lógicos como estructuras de control (`If`, `For`), llamadas a funciones y retornos de datos.
*   **Análisis de Flujo de Datos:** El estudio de cómo los valores se mueven a través del programa. SIR-FE utiliza esta técnica para determinar la naturaleza de un método (ej. si produce efectos colaterales o si es una función pura de extracción).

## 3. Representación Intermedia Semántica (SIR)
La metodología propone una **Capa Intermedia (IR)** para cerrar la "Brecha Semántica" (*Semantic Gap*) entre las instrucciones de bajo nivel y la lógica de negocio.

### 3.1. Taxonomía de Roles Funcionales (Estructurales)
SIR-FE clasifica cada método del sistema según su intención lógica predominante, utilizando heurísticas basadas en la estructura del AST:

| Rol | Definición Técnica | Heurística en el AST | Intención Funcional (Negocio) |
| :--- | :--- | :--- | :--- |
| **GUARD** | Lógica de control de precondiciones. | Presencia de nodos `Raise`, `Assert` o retornos tempranos condicionales. | Validación de reglas de negocio y seguridad. |
| **PERSISTER** | Operación orientada a efectos colaterales. | Ausencia de valor de retorno (`Return`) combinado con lógica de control o llamadas a servicios externos. | Persistencia de datos o cambio de estado en el sistema. |
| **TRANSFORMER** | Operación de procesamiento y cálculo. | Presencia de valor de retorno y lógica de control interna (`If`, `For`, `While`). | Aplicación de algoritmos, cálculos o transformación de entidades. |
| **EXTRACTOR** | Operación de recuperación simple. | Presencia de valor de retorno con baja complejidad algorítmica (acceso directo). | Consulta de información o recuperación de atributos. |

### 3.2. Dimensiones Semánticas Complementarias
Para enriquecer el perfil del método, se añaden tres dimensiones adicionales que permiten el clustering preciso:

*   **Efecto Sistémico (Side-Effects):**
    *   **MUTABLE:** El método altera el estado global o de base de datos (ej. `update`, `delete`).
    *   **STABLE:** El método es de "solo lectura", garantizando la integridad del estado sistémico.
    *   **SIGNAL:** El método dispara eventos o notificaciones a otros sistemas (ej. `send_email`, `emit_log`).
*   **Complejidad Operacional:**
    *   **SEQUENTIAL:** Flujo lineal sin bifurcaciones.
    *   **BRANCHING:** Presencia de lógica condicional moderada.
    *   **COMPLEX_BRANCHING:** Algoritmos con múltiples ramificaciones o anidamiento profundo.
*   **Contexto de Dominio:** Identificación automática de la entidad de negocio afectada mediante el análisis de la firma del método y la clase contenedora (ej. `STORAGE`, `IDENTITY`, `UI_CONFIG`).

## 4. Minería de Software y Clustering de Comportamiento
La metodología emplea técnicas de **Minería de Repositorios de Software (MSR)** para tratar el código como un conjunto de datos estructurados.

*   **Vectorización de Comportamiento:** Uso de técnicas como *One-Hot Encoding* para transformar la clasificación cualitativa de la IR en vectores numéricos.
*   **Aprendizaje No Supervisado (Clustering):** Aplicación del algoritmo **K-Means** para agrupar métodos que comparten firmas semánticas similares. La hipótesis subyacente es que métodos con perfiles semánticos idénticos pertenecen a la misma capacidad funcional, independientemente de su ubicación física en el sistema.

## 6. Dualidad de Gherkin: Especificaciones Ejecutables y Pruebas de Caracterización

Una de las contribuciones fundamentales de esta metodología es el uso de Gherkin como puente entre dos conceptos tradicionalmente separados en la ingeniería de software:

### 6.1. Gherkin como Especificación Ejecutable
En el marco de BDD (*Behavior-Driven Development*), los escenarios Gherkin no son meros casos de prueba; son **especificaciones ejecutables**. Representan el comportamiento deseado del sistema en un lenguaje natural estructurado (Ubiquitous Language) que es comprensible tanto para los desarrolladores como para los expertos de negocio. En la metodología SIR-FE, el proceso de extracción recupera la especificación funcional que ha quedado "atrapada" en el código legacy.

### 6.2. Pruebas de Caracterización (Characterization Tests)
Dado que en los sistemas legados el código fuente suele ser la única "fuente de verdad" actualizada, los artefactos generados por SIR-FE actúan como **Pruebas de Caracterización**, según la definición de **Michael Feathers (2004)**. 

*   **Objetivo:** El propósito de estas pruebas no es validar la corrección lógica (si el código es "correcto" según un documento de diseño), sino **caracterizar y documentar lo que el sistema hace actualmente**.
*   **Valor en la Reingeniería:** Al automatizar esta caracterización en formato Gherkin, se crea una red de seguridad que permite realizar procesos de refactorización o migración tecnológica asegurando la preservación del comportamiento funcional histórico.

De este modo, los resultados de SIR-FE cumplen una doble función: sirven como **documentación funcional recuperada** (Especificación) y como **suite de regresión automatizada** (Caso de Prueba).

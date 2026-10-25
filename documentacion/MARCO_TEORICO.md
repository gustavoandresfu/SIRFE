# Extracción de especificaciones funcionales en formato Gherkin a partir de código fuente de aplicaciones legacy
## Marco Teórico: Metodología SIR-FE

## 1. Ingeniería Inversa y Mantenimiento de Sistemas Legados
El mantenimiento de sistemas legados representa uno de los mayores desafíos en la ingeniería de software actual. Según **Parnas (1994)**, el envejecimiento del software ocurre con frecuencia debido a la degradación de la documentación de requerimientos y la pérdida del conocimiento sobre la arquitectura original.

*   **Ingeniería Inversa:** Proceso de análisis de un sistema para identificar sus componentes y sus interrelaciones, creando representaciones en un nivel de abstracción más alto (Chikofsky & Cross).
*   **Recuperación de Conceptos (Concept Location):** Técnica orientada a identificar qué fragmentos del código fuente implementan un concepto específico del dominio de negocio.

## 2. Análisis Estático y Abstracción Sintáctica
La base técnica de SIR-FE reside en el análisis estático de código, que permite examinar propiedades del software sin necesidad de ejecutarlo en un entorno operativo completo.

*   **Abstract Syntax Tree (AST):** Una representación jerárquica de la estructura sintáctica del código fuente. El AST permite navegar la estructura lógica del programa, facilitando la identificación de estructuras de control (`If`, `For`), llamadas a funciones, excepciones y retornos de datos.
*   **Inspección Intraprocedural de Efectos:** Examen localizado de las operaciones de un método para inferir su perfil de ejecución (por ejemplo, si altera atributos del objeto o si realiza operaciones de solo lectura).

## 3. Representación Intermedia Semántica (SIR)
La metodología propone una **Capa Intermedia (IR)** preliminar para reducir la brecha semántica entre las instrucciones de bajo nivel y la descripción funcional.

### 3.1. Taxonomía de Roles Funcionales Heurísticos
SIR-FE clasifica cada método analizado según patrones sintácticos detectados en el AST:

| Rol | Definición Técnica | Heurística en el AST | Intención Funcional Asociada |
| :--- | :--- | :--- | :--- |
| **VALIDATOR / GUARD** | Lógica de control de precondiciones. | Presencia de nodos `Raise`, `Assert` o retornos condicionales tempranos de corte. | Validación de reglas de consistencia y seguridad. |
| **PERSISTER** | Operación orientada a efectos de almacenamiento. | Invocación de métodos reconocidos como mutables (`write`, `create`, `update`, `save`). | Persistencia de datos o alteración de estado persistente. |
| **TRANSFORMER** | Operación de procesamiento algorítmico. | Presencia de valor de retorno combinado con estructuras de iteración (`For`, `While`) o múltiples asignaciones. | Aplicación de cálculos o transformación de estructuras. |
| **EXTRACTOR** | Operación de consulta y recuperación. | Presencia de sentencias de retorno de valores sin bucles ni lógica compleja. | Lectura de atributos o consulta de datos. |

### 3.2. Dimensiones Semánticas Complementarias
Para enriquecer el vector de características del método, se extraen dimensiones auxiliares:

*   **Efectos de Estado Detectados:**
    *   **PERSISTENT:** Invocación de operaciones de escritura/almacenamiento.
    *   **MEMORY:** Asignación a atributos de instancia (`self.*`).
    *   **EXTERNAL:** Invocación de métodos de emisión de señales o mensajería (`send`, `trigger`, `emit`, `rpc`).
*   **Inferencia Contextual:** Asociación preliminar a un dominio funcional mediante coincidencia de palabras clave configurables en los nombres de clases y funciones (`IDENTITY`, `STORAGE`, `UI_CONFIG`).

## 4. Minería de Software y Clustering de Comportamiento
*   **Vectorización de Comportamiento:** Transformación de las variables cualitativas y categóricas de la SIR en matrices numéricas ponderadas por pesos de confianza heurísticos.
*   **Aprendizaje No Supervisado:** Aplicación de algoritmos de agrupamiento como **K-Means**, **Agglomerative Clustering** o **DBSCAN** para particionar los métodos según su proximidad en el espacio de características.
*   **Hipótesis de Trabajo:** Los métodos que comparten perfiles sintácticos similares pueden agruparse como componentes colaborativos de una misma capacidad funcional preliminar.

## 5. El Rol de Gherkin: Candidatos para Pruebas de Caracterización

La metodología investiga el formato Gherkin como mecanismo de articulación en la ingeniería inversa:

### 5.1. Formato Gherkin como Lenguaje Declarativo Puente
En BDD (*Behavior-Driven Development*), los escenarios Gherkin estructuran el comportamiento mediante cláusulas `Dado`, `Cuando`, `Entonces`. SIR-FE utiliza esta estructura como plantilla declarativa para sintetizar las precondiciones, acciones y postcondiciones identificadas en cada cluster de métodos.

### 5.2. Escenarios Candidatos para Pruebas de Caracterización (Characterization Tests)
Según **Michael Feathers (2004)**, las pruebas de caracterización tienen como objetivo registrar y documentar el comportamiento actual de un sistema para protegerlo durante procesos de modernización.

*   **Naturaleza de los Escenarios Generados:** Los artefactos sintetizados por SIR-FE son **escenarios candidatos de caracterización**, concebidos como borradores estructurados que describen el flujo detectado.
*   **Distinción con Pruebas Ejecutables:** A diferencia de una suite de pruebas de regresión terminada, estos escenarios **no incluyen step definitions ejecutables ni aserciones de tiempo de ejecución**. Su función es servir como especificación funcional preliminar recuperada y como punto de partida para que los ingenieros de calidad implementen posteriormente pruebas ejecutables con herramientas como *Behave* o *pytest-bdd*.

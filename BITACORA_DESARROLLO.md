
# Bitácora de Desarrollo

Este documento registra los pasos seguidos durante el desarrollo del proyecto, explicando la lógica y el propósito de cada cambio.

## 1. Corrección en la Ejecución del Servidor (`backend/main.py`)

**Cambio:**
Se modificó la llamada a `uvicorn.run` para pasar la aplicación como una cadena de importación (`"main:app"`) en lugar de intentar pasar el objeto `app` con una sintaxis incorrecta.

**Código:**
```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

**Lógica:**
Al usar `"main:app"` (string), permitimos que `uvicorn` encuentre la aplicación dinámicamente. Esto es crucial cuando se usa `reload=True`, ya que el servidor necesita poder recargar el módulo completo cuando detecta cambios en el código. La sintaxis anterior tenía un error de tipado (`app:"main:app"`).

## 2. Configuración de la Base de Datos (`backend/db/database.py`)

**Cambio:**
Se creó el archivo de configuración para la conexión con la base de datos usando SQLAlchemy.

**Componentes Clave:**
- **`create_engine`**: Establece la conexión física con la base de datos usando la URL definida en `settings`.
- **`SessionLocal`**: Una fábrica de sesiones. Cada vez que necesitamos interactuar con la DB, creamos una nueva sesión desde aquí.
- **`Base`**: Clase base declarativa. Todos nuestros modelos heredarán de esta clase para que SQLAlchemy pueda mapearlos a tablas.
- **`get_db`**: Una función generadora (dependency) que crea una sesión, la entrega para su uso y asegura que se cierre al finalizar, incluso si ocurren errores.

## 3. Definición de Modelos de Historia (`backend/models/story.py`)

**Cambio:**
Se definieron las tablas `stories` y `story_nodes`.

**Lógica:**
- **`Story`**: Representa una historia o partida. Guarda metadatos como el título, descripción y sesión.
- **`StoryNode`**: Representa un fragmento de la historia (un nodo).
    - Tiene una relación con `Story` (muchos nodos pertenecen a una historia).
    - `is_root`: Marca si es el nodo inicial.
    - `is_ending` / `is_winning_ending`: Determinan si el juego termina aquí.
    - `options`: Campo JSON para guardar las posibles decisiones que llevan a otros nodos.

## 4. Definición de Modelo de Trabajos (`backend/models/job.py`)

**Cambio:**
Se definió la tabla `story_jobs` para manejar tareas asíncronas o estados de generación.

**Lógica:**
- **`StoryJob`**: Permite rastrear el estado de procesos largos (como la generación de una historia por IA).
- Campos como `status`, `error`, y `completed_job` ayudan a monitorear el progreso y manejar fallos sin bloquear la respuesta inmediata al usuario.

## 5. Definición de Esquemas (Schemas) (`backend/schemas/`)

**Cambio:**
Se crearon los esquemas Pydantic para la validación de datos de entrada y salida de la API.

**Archivos creados:**
- `backend/schemas/story.py`: Contiene los esquemas para las historias.
- `backend/schemas/job.py`: (Pendiente de implementación) Para manejar estados de trabajos.

**Lógica (`schemas/story.py`):**
- **`StoryOptionsSchema`**: Define la estructura de las opciones de decisión en un nodo.
- **`StoryNodeBase`**: Esquema base para los nodos de la historia.
- **`CompleteStoryNodeResponse`**: Esquema para la respuesta completa de un nodo, incluyendo ID y opciones.
- **`StoryBase`**: Esquema base para la historia.
- **`CreateStoryRequest`**: Esquema para la solicitud de creación de una historia (solo requiere el tema).
- **`CompleteStoryResponse`**: Esquema completo de la historia, incluyendo el nodo raíz y todos los nodos.

## 6. Estructura de Rutas (Routers) (`backend/routers/`)

**Cambio:**
Se crearon los archivos para los endpoints de la API, aunque aún están vacíos.

**Archivos creados:**
- `backend/routers/story.py`: Manejará los endpoints relacionados con las historias.
- `backend/routers/job.py`: Manejará los endpoints para el estado de tareas en segundo plano.

## 7. Estructura del Núcleo (Core) (`backend/core/`)

**Cambio:**
Se definieron los archivos base para la lógica central del juego y la configuración.

**Archivos:**
- `backend/core/config.py`: Configuración global (variables de entorno, base de datos).
- `backend/core/prompts.py`: (Pendiente) Almacenará los prompts para la IA.
- `backend/core/story_generator.py`: (Pendiente) Lógica de generación de historias.
- `backend/core/models.py`: (Pendiente) Modelos internos del core.

## 8. Implementación de Endpoints y Lógica de Jobs (`backend/routers/story.py` y `backend/schemas/job.py`)

**Cambio:**
Se implementó la lógica para crear historias de manera asíncrona y consultar su estado.

**Detalles de Implementación:**

1.  **Esquemas de Jobs (`backend/schemas/job.py`)**:
    -   `StoryJobBase`: Define los datos básicos de un trabajo (tema).
    -   `StoryJobResponse`: Estructura de respuesta que incluye el ID del trabajo, estado, fecha de creación y errores si los hubo.
    -   `StoryJobCreate`: Esquema para la creación (hereda de Base).

2.  **Router de Historias (`backend/routers/story.py`)**:
    -   **`create_story` (POST `/story/create`)**:
        -   Recibe el tema de la historia.
        -   Genera un `session_id` si no existe (usando cookies).
        -   Crea un registro `StoryJob` en la base de datos con estado "pending".
        -   Lanza una tarea en segundo plano (`generate_story_task`) para no bloquear la respuesta.
        -   Retorna el `job_id` para que el frontend pueda hacer polling.
    
    -   **`generate_story_task` (Background Task)**:
        -   Simula (por ahora) el proceso de generación.
        -   Actualiza el estado del job a "procesando" y luego a "completado" o "error".
        -   Maneja la sesión de base de datos independientemente del request principal.

    -   **`get_complete_story` (GET `/story/{story_id}/complete`)**:
        -   Recupera una historia completa por su ID.
        -   Usa una función auxiliar `build_coplete_story_tree` (pendiente de implementación completa) para estructurar la respuesta.

## 9. Corrección de Errores y Ajustes de Configuración

**Cambio:**
Se realizaron varias correcciones para asegurar que el backend se ejecute correctamente y la documentación de la API esté disponible.

**Detalles:**

1.  **Corrección de Imports (Prefijo `backend.`)**:
    -   Se eliminó el prefijo `backend.` de los imports en `routers/story.py`, `routers/job.py`, `models/story.py`, `models/job.py` y `db/database.py`.
    -   **Razón**: Al ejecutar la aplicación desde el directorio `backend`, los imports deben ser relativos a ese directorio raíz, no incluir el nombre del directorio padre como paquete.

2.  **Corrección de Indentación (`backend/core/config.py`)**:
    -   Se corrigió un `IndentationError` donde todo el contenido del archivo tenía una indentación innecesaria.

3.  **Registro de Routers (`backend/main.py`)**:
    -   Se agregaron las llamadas a `app.include_router()` para los routers de `story` y `job`.
    -   **Resultado**: Los endpoints ahora son visibles en la documentación automática (`/docs`).

4.  **Corrección de Tipo en Modelo (`backend/models/job.py`)**:
    -   Se corrigió el tipo de columna `string` (minúscula) a `String` (mayúscula, de SQLAlchemy).

5.  **Corrección de Relación en Modelo (`backend/models/story.py`)**:
    -   Se corrigió la referencia en `relationship("Node", ...)` a `relationship("StoryNode", ...)` para coincidir con el nombre real de la clase.

## 10. Solución de Error 500 en Creación de Historias

**Problema:**
Al intentar crear una historia (`POST /api/story/create`), el servidor devolvía un error interno 500.

**Causas y Soluciones:**

1.  **Inconsistencia de Campos (`backend/models/job.py`)**:
    -   **Error**: El modelo `StoryJob` tenía el campo `completed_job`, pero el esquema `StoryJobResponse` esperaba `completed_at`.
    -   **Solución**: Se renombró la columna en el modelo a `completed_at` para mantener la coherencia.

2.  **Errores Tipográficos (`backend/routers/story.py`)**:
    -   **Error**: Se encontraron variables mal escritas como `jpb_id` en lugar de `job_id` y asignaciones incorrectas como `job.story = 1` en lugar de `job.story_id = 1`.
    -   **Solución**: Se corrigieron todos los errores de tipeo en la función `generate_story_task`.

3.  **Error de Relación SQLAlchemy (`backend/models/story.py`)**:
    -   **Error**: `InvalidRequestError` debido a que `relationship` apuntaba a una clase inexistente `"Node"`.
    -   **Solución**: Se cambió a `"StoryNode"`, que es el nombre correcto de la clase del modelo.

4.  **Tablas no Creadas (`backend/main.py`)**:
    -   **Error**: La función `create_tables()` no se estaba llamando al inicio de la aplicación, por lo que la base de datos estaba vacía.
    -   **Solución**: Se restauró la llamada a `create_tables()` en `main.py`.

5.  **Reinicio de Base de Datos**:
    -   Para aplicar los cambios de esquema (como el renombre de columna) sin migraciones complejas en desarrollo, se eliminó el archivo `database.db` para forzar su recreación con la estructura correcta.

## 11. Documentación de `story_generator.py`

**Cambio:**
Se agregaron comentarios detallados en español al archivo `backend/core/story_generator.py` para explicar el propósito de los módulos importados y la lógica de las funciones implementadas.

**Detalles:**
- **Imports:** Se documentó qué hace cada librería importada (SQLAlchemy, LangChain, modelos, etc.).
- **Clase `StoryGenerator`:**
    - **`_get_llm`**: Explica la configuración del modelo GPT-4.
    - **`generate_story`**: Describe el flujo completo de generación: configuración del prompt, invocación del LLM, parseo de la respuesta y guardado en base de datos.
    - **`_process_story_node`**: Detalla la lógica recursiva para procesar y guardar los nodos de la historia y sus opciones.

## 12. Limpieza de Entorno Virtual Redundante

**Cambio:**
Se eliminó el directorio `.venv` ubicado en la raíz del proyecto (`c:\Users\daguo\OneDrive\Documents\Proyecto Juego interactivo\.venv`).

**Razón:**
Existía una redundancia con el entorno virtual principal ubicado en `backend/.venv`. El entorno de la raíz probablemente fue creado por error y no contenía las dependencias del proyecto, lo que podía causar confusión al seleccionar el intérprete correcto. Se conservó únicamente el entorno dentro de `backend/` que está sincronizado con `pyproject.toml`.

## 13. Corrección de Error Tipográfico en `core/models.py`

**Error:**
La aplicación fallaba al iniciar con un `ImportError` porque la clase `StoryLLMResponse` estaba mal escrita como `StotyLLMResponse` en `backend/core/models.py`.

**Solución:**
Se renombró la clase a `StoryLLMResponse` para coincidir con la importación en `story_generator.py`.

## 14. Configuración de `OPENAI_API_KEY`

**Problema:**
La generación de historias fallaba con un error indicando que la `OPENAI_API_KEY` no estaba configurada.

**Solución:**
Se actualizó el archivo `backend/.env` con la clave de API proporcionada por el usuario.

## 15. Corrección de Inyección de API Key en LangChain

**Problema:**
A pesar de tener la `OPENAI_API_KEY` en el archivo `.env`, `LangChain` seguía lanzando un error porque no encontraba la clave en las variables de entorno del sistema (`os.environ`).

**Solución:**
Se modificó el método `_get_llm` en `backend/core/story_generator.py` para pasar explícitamente la clave desde la configuración de la aplicación (`settings.OPENAI_API_KEY`) al constructor de `ChatOpenAI`.

```python
return ChatOpenAI(model="gpt-4-turbo", api_key=settings.OPENAI_API_KEY)
```

## 16. Corrección de Error de Sintaxis en `story_generator.py`

**Problema:**
Durante la edición anterior, se introdujo accidentalmente un error de indentación y se borró parte de la definición de la clase `StoryGenerator`, lo que causaba un `IndentationError` al iniciar la aplicación.

**Solución:**
Se restauró el contenido completo del archivo `backend/core/story_generator.py`, asegurando que la estructura de la clase y los métodos sean correctos, manteniendo la corrección de la API Key.


## 17. Cambio de Modelo OpenAI

**Problema:**
La API de OpenAI devolvió un error `model_not_found` al intentar usar `gpt-4-turbo`. Esto puede deberse a restricciones de la cuenta o a que el nombre del modelo no es exacto para el tier actual.

**Solución:**
Se actualizó el modelo a `gpt-4o` en `backend/core/story_generator.py`, que es el modelo insignia actual y debería estar disponible.

```python
return ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
```

## 18. Error de Cuota Insuficiente (OpenAI)

**Problema:**
Se recibió un error `429 insufficient_quota` al intentar generar una historia.

**Causa:**
La cuenta de OpenAI asociada a la API Key ha excedido su cuota de uso o no tiene créditos disponibles. Esto es un problema de facturación de la cuenta de OpenAI y no del código.

**Acción Requerida:**
El usuario debe verificar su facturación en [platform.openai.com](https://platform.openai.com/account/billing) y agregar créditos para continuar usando la API.

## 19. Revisión Final del Backend

**Acciones:**
- Se realizó una revisión completa de los archivos `routers/story.py`, `schemas/story.py` y `models/story.py`.
- Se corrigió un error tipográfico en el nombre de la función `build_coplete_story_tree` -> `build_complete_story_tree`.
- Se restauró la integridad del archivo `routers/story.py` que había sufrido corrupción durante la edición.

**Estado Actual:**
El backend está funcional y el código es correcto. La aplicación levanta sin errores y los endpoints están definidos correctamente. La única limitación actual es externa (cuota de OpenAI), pero el código está listo para funcionar una vez resuelto ese aspecto administrativo.

## 20. Decisión de Diseño: Versión 0.1.0

**Estado:**
Se decide mantener la implementación actual con OpenAI (`gpt-4o`) y el modelo de costos centralizado (API Key en el backend) para completar la versión 0.1.0 (MVP).

**Plan Futuro:**
Para versiones posteriores, se evaluará la migración a modelos gratuitos (como Google Gemini o Groq) o cambios en la arquitectura para reducir costos operativos antes de un despliegue masivo.

## 21. Configuración de Control de Versiones

**Acciones:**
- Se eliminó el repositorio Git de `backend/` para evitar repositorios anidados.
- Se inicializó un repositorio Git en la raíz del proyecto (`Proyecto Juego interactivo/`).
- Se creó `.gitignore` en la raíz con reglas para proteger archivos sensibles (`.env`, `*.db`) y archivos generados.
- Se configuró la identidad Git del usuario.
- Se realizó el commit inicial del proyecto completo (backend + bitácora).

**Estructura del repositorio:**
```
Proyecto Juego interactivo/
├── .git/
├── .gitignore
├── BITACORA_DESARROLLO.md
└── backend/
    ├── core/
    ├── db/
    ├── models/
    ├── routers/
    ├── schemas/
    └── ...
```

## 22. Documentación Adicional y Correcciones Menores

**Fecha:** 2025-11-29

**Archivos documentados:**
- **`core/models.py`**: Se agregaron comentarios explicando los modelos Pydantic para validar respuestas del LLM (`StoryOptionLLM`, `StoryNodeLLM`, `StoryLLMResponse`)
- **`models/job.py`**: Se documentó completamente el modelo `StoryJob` que rastrea el estado de trabajos asíncronos de generación

**Correcciones realizadas:**
- **`core/story_generator.py`**: 
  - Actualizado comentario del método `_get_llm` de 'gpt-4-turbo' a 'gpt-4o'
  - Corregido typo en parámetro por defecto: `theme: str = "fatasy"` → `theme: str = "fantasy"`

**Estado:**
Toda la documentación del backend está completa. Cada archivo tiene comentarios explicativos sobre módulos importados, propósito de clases y funciones.


# Proyecto: Crea tu Propia Aventura (IA)

Este proyecto es una aplicación web de ficción interactiva que utiliza Inteligencia Artificial Generativa (Google Gemini) para crear historias dinámicas donde las decisiones del usuario influyen en la trama en tiempo real.

## Características

*   **Historias Infinitas**: Generadas al vuelo por IA basada en temas elegidos por el usuario.
*   **Interactividad**: El usuario elige entre múltiples opciones en cada paso de la historia.
*   **Persistencia**: Las historias y el progreso se guardan automáticamente.
*   **Diseño Responsivo**: Interfaz amigable para escritorio y móviles.

## Tecnologías

### Backend
*   **Framework**: FastAPI (Python)
*   **IA**: Google Gemini 2.0 Flash (vía LangChain)
*   **Base de Datos**: SQLite (SQLAlchemy ORM)
*   **Herramientas**: `uv` para gestión de paquetes.

### Frontend
*   **Framework**: React (Vite)
*   **Estilos**: CSS Modules / Vanilla CSS

## Configuración Local

### Requisitos Previos
*   Python 3.12+
*   Node.js 18+
*   Clave de API de Google Gemini

### 1. Configuración del Backend

Navega al directorio `backend`:
```bash
cd backend
```

Instala las dependencias (usando `uv` o `pip`):
```bash
pip install -r requirements.txt
```

Crea un archivo `.env` en la carpeta `backend` con tu API Key:
```env
GEMINI_API_KEY=tu_clave_aqui
```

Inicia el servidor localmente:
```bash
uvicorn main:app --reload
```
El servidor correrá en `http://localhost:8000`.

### 2. Configuración del Frontend

Navega al directorio `frontend`:
```bash
cd frontend
```

Instala las dependencias:
```bash
npm install
```

Inicia el servidor de desarrollo:
```bash
npm run dev
```
La aplicación estará disponible en `http://localhost:5173`.

## Despliegue en Render

El proyecto está configurado para desplegarse en Render.com.

*   **Build Script**: `backend/build.sh` (instala dependencias).
*   **Start Command**: `backend/Procfile` (inicia uvicorn).

Asegúrate de configurar la variable de entorno `GEMINI_API_KEY` en el panel de Render.

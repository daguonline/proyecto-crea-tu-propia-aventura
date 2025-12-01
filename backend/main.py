"""
Archivo principal de la aplicación FastAPI.
Configura el servidor, middlewares, y registra los routers de la API.
"""

# Imports de FastAPI para crear la aplicación y manejar CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuración de la aplicación y routers
from core.config import settings  # Configuración centralizada desde variables de entorno
from routers import story, job  # Routers que manejan los endpoints de historias y trabajos
from db.database import create_tables  # Función para crear las tablas en la base de datos

# Crear las tablas en la base de datos al iniciar la aplicación
create_tables()


# Configuración de la aplicación FastAPI
app = FastAPI(
    title="Juega Tu Propia Aventura API", 
    description="API para generar aventuras divertidas",
    version="0.1.0",
    docs_url="/docs",   # URL donde estará la documentación interactiva (Swagger UI)
    redoc_url="/redoc", # URL para la documentación alternativa (ReDoc)
)


# Configuración de CORS (Cross-Origin Resource Sharing)
# Permite que el frontend (que estará en otro dominio/puerto) pueda hacer peticiones a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Orígenes permitidos (configurados en .env)
    allow_credentials=True,   # Permite el envío de cookies
    allow_methods=["*"],      # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],      # Permite todos los headers
)

# Registro de routers con el prefijo /api
app.include_router(story.router, prefix=settings.API_PREFIX)  # Endpoints de historias
app.include_router(job.router, prefix=settings.API_PREFIX)    # Endpoints de trabajos

# Punto de entrada cuando se ejecuta directamente con Python
if __name__ == "__main__":
    import uvicorn
    # Ejecuta el servidor con recarga automática en desarrollo
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

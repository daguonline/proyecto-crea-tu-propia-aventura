"""
Configuración centralizada de la aplicación.
Lee variables de entorno desde el archivo .env y las valida usando Pydantic.
"""

from typing import List
from pydantic_settings import BaseSettings  # Para leer configuración desde variables de entorno
from pydantic import field_validator  # Para validar y transformar campos

class Settings(BaseSettings):
    """
    Clase que define todas las configuraciones de la aplicación.
    Los valores se leen automáticamente desde el archivo .env
    """
    
    # Prefijo para todas las rutas de la API (ej: /api/story/create)
    API_PREFIX: str = '/api'
    
    # Modo debug (activa logs adicionales en desarrollo)
    DEBUG: bool = False

    # URL de conexión a la base de datos (requerido en .env)
    DATABASE_URL: str

    # Orígenes permitidos para CORS (separados por comas en .env)
    ALLOWED_ORIGINS: str = ''

    # Clave de API de OpenAI para generar historias (requerido en .env)
    OPENAI_API_KEY: str 

    @field_validator('ALLOWED_ORIGINS')
    def parse_allowed_origins(cls, v: str) -> List[str]:
        """
        Convierte la cadena de orígenes separados por comas en una lista.
        Ejemplo: "http://localhost:3000,http://localhost:5137" -> ["http://localhost:3000", "http://localhost:5137"]
        """
        return v.split(',') if v else []

    class Config:
        """Configuración de cómo Pydantic lee las variables de entorno"""
        env_file = '.env'  # Archivo desde donde leer las variables
        env_file_encoding = 'utf-8'  # Codificación del archivo
        case_sensitive = True  # Los nombres de variables distinguen mayúsculas/minúsculas
       
# Instancia global de configuración que se importa en otros módulos
settings = Settings()

"""
Configuración de la base de datos usando SQLAlchemy.
Define el motor de conexión, la sesión y funciones auxiliares para gestionar la DB.
"""

# Imports de SQLAlchemy para manejar la base de datos
from sqlalchemy import create_engine  # Crea la conexión con la base de datos
from sqlalchemy.orm import sessionmaker  # Fábrica para crear sesiones de DB
from sqlalchemy.ext.declarative import declarative_base  # Base para los modelos ORM

from core.config import settings  # Configuración que contiene la URL de la DB


# Motor de base de datos: establece la conexión física con SQLite
engine = create_engine(
    settings.DATABASE_URL  # URL leída desde .env (ej: sqlite:///./database.db)
)

# Fábrica de sesiones: cada vez que necesitamos interactuar con la DB, creamos una sesión
SessionLocal = sessionmaker(
    autocommit=False,  # No hacer commit automático (control manual de transacciones)
    autoflush=False,   # No hacer flush automático
    bind=engine        # Vincula esta sesión al motor de base de datos
)

# Clase base para todos los modelos ORM
# Todos los modelos (Story, StoryNode, etc.) heredan de esta clase
Base = declarative_base()

def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    Se usa como dependencia en FastAPI para inyectar la DB en los endpoints.
    Asegura que la sesión se cierre correctamente después de cada request.
    """
    db = SessionLocal()
    try:
        yield db  # Entrega la sesión al endpoint
    finally:
        db.close()  # Cierra la sesión al terminar (incluso si hay error)

def create_tables():
    """
    Crea todas las tablas definidas en los modelos si no existen.
    Se ejecuta al iniciar la aplicación (llamado desde main.py).
    """
    Base.metadata.create_all(bind=engine)
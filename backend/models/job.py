"""
Modelo de base de datos para trabajos (jobs) de generación de historias.
Permite rastrear el estado de las generaciones asíncronas de historias.
"""

# Imports de SQLAlchemy para definir columnas y tipos de datos
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func  # Funciones SQL como now() para timestamps

# Clase base para todos los modelos ORM
from db.database import Base

class StoryJob(Base):
    """
    Representa un trabajo de generación de historia en la base de datos.
    
    Cuando un usuario solicita crear una historia, se crea un registro StoryJob
    con estado 'pending'. La generación se hace en segundo plano y este registro
    se actualiza con el progreso:
    - 'pending' -> 'procesando' -> 'completado' (o 'error')
    
    El frontend hace polling a este registro para saber cuándo la historia está lista.
    """
    __tablename__ = "story_jobs"
    
    # ID autoincremental interno de la base de datos
    id = Column(Integer, primary_key=True, index=True)
    
    # UUID único del trabajo (se expone al frontend para hacer polling)
    job_id = Column(String, index=True, unique=True)
    
    # ID de sesión del usuario que solicitó la historia
    session_id = Column(String, index=True)
    
    # Tema solicitado para la historia (ej: "fantasy", "sci-fi")
    theme = Column(String)
    
    # Estado actual: "pending", "procesando", "completado", "error"
    status = Column(String)
    
    # ID de la historia generada (null hasta que se complete)
    story_id = Column(Integer, nullable=True)
    
    # Mensaje de error si la generación falló (null si no hay error)
    error = Column(String, nullable=True)
    
    # Timestamp de cuándo se creó el trabajo (automático)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamp de cuándo se completó o falló (null mientras está en proceso)
    completed_at = Column(DateTime(timezone=True), nullable=True)
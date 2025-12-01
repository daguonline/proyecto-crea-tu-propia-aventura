"""
Router para consultar el estado de trabajos (jobs) de generación de historias.
Permite al frontend hacer polling para saber cuándo una historia está lista.
"""

# Imports de FastAPI para crear endpoints y manejar dependencias
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session  # Tipo para la sesión de base de datos

# Imports locales
from db.database import get_db  # Dependencia que proporciona la sesión de DB
from models.job import StoryJob  # Modelo ORM del trabajo
from schemas.job import StoryJobResponse  # Schema de respuesta

# Configuración del router con prefijo /job
router = APIRouter(
    prefix="/job",
    tags=["job"]  # Agrupa estos endpoints en la documentación
)

@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Consulta el estado de un trabajo de generación de historia.
    
    El frontend llama a este endpoint repetidamente (polling) para saber
    si la historia ya fue generada o si hubo algún error.
    
    Args:
        job_id: UUID del trabajo a consultar
        db: Sesión de base de datos (inyectada automáticamente)
        
    Returns:
        StoryJobResponse con el estado actual del trabajo
        
    Raises:
        HTTPException 404 si el job_id no existe
    """
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

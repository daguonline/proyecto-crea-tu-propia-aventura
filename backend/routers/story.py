"""
Router para la creación y consulta de historias interactivas.
Maneja la generación asíncrona de historias usando OpenAI y el almacenamiento en DB.
"""

import uuid  # Para generar IDs únicos de trabajos
from typing import Optional
from datetime import datetime
# Imports de FastAPI
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session  # Tipo para sesiones de base de datos

# Imports locales
from db.database import get_db, SessionLocal  # Dependencias de base de datos
from models.story import Story, StoryNode  # Modelos ORM
from models.job import StoryJob  # Modelo de trabajo asíncrono
from schemas.story import (  # Schemas de validación
    CompleteStoryNodeResponse, CompleteStoryResponse, CreateStoryRequest
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator  # Lógica de generación con LLM

# Configuración del router
router = APIRouter(
    prefix="/story",
    tags=["story"]  # Agrupa endpoints en la documentación
)

def get_session_id(session_id: Optional[str] = Cookie(None)):
    """
    Obtiene o genera un ID de sesión para el usuario.
    Si el usuario ya tiene una cookie de sesión, la reutiliza.
    Si no, genera un nuevo UUID.
    
    Args:
        session_id: ID de sesión desde la cookie (opcional)
        
    Returns:
        str: ID de sesión (existente o nuevo)
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """
    Endpoint para crear una nueva historia interactiva.
    
    La generación se hace de forma asíncrona para no bloquear la respuesta.
    El frontend debe hacer polling al endpoint /job/{job_id} para saber cuándo está lista.
    
    Args:
        request: Contiene el tema de la historia
        background_tasks: Gestor de tareas en segundo plano de FastAPI
        response: Objeto de respuesta para setear cookies
        session_id: ID de sesión del usuario (inyectado)
        db: Sesión de base de datos (inyectada)
        
    Returns:
        StoryJobResponse con el job_id para hacer polling
    """
    # Guardar el session_id en una cookie para futuras peticiones
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    # Generar un ID único para este trabajo
    job_id = str(uuid.uuid4())

    # Crear registro del trabajo en la base de datos con estado "pending"
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,    
        status="pending"
    )
    db.add(job)
    db.commit()

    # Lanzar la generación de la historia en segundo plano
    # Esto permite que el endpoint responda inmediatamente
    background_tasks.add_task(
        generate_story_task, 
        job_id, 
        request.theme, 
        session_id
    )

    return job

def generate_story_task(job_id: str, theme: str, session_id: str):
    """
    Tarea en segundo plano que genera la historia usando el LLM.
    
    Esta función se ejecuta de forma asíncrona después de que el endpoint
    /create responde al cliente. Actualiza el estado del job en la DB.
    
    Args:
        job_id: UUID del trabajo
        theme: Tema de la historia solicitado por el usuario
        session_id: ID de sesión del usuario
    """
    # Crear una nueva sesión de DB independiente (estamos en otro thread)
    db = SessionLocal()

    try:
        # Buscar el registro del trabajo
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return
        
        try:
            # Actualizar estado a "procesando"
            job.status = "procesando"
            db.commit()

            # Generar la historia usando OpenAI (puede tardar varios segundos)
            story = StoryGenerator.generate_story(db, session_id, theme)
            
            # Actualizar el job con el ID de la historia generada
            job.story_id = story.id
            job.status = "completado"
            job.completed_at = datetime.now()
            db.commit()
            
        except Exception as e:
            # Si algo falla, guardar el error en el job
            job.status = "error"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()

    finally:
        # Siempre cerrar la sesión de DB
        db.close()


@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una historia completa con todos sus nodos y opciones.
    
    Args:
        story_id: ID de la historia a consultar
        db: Sesión de base de datos (inyectada)
        
    Returns:
        CompleteStoryResponse con la estructura completa de la historia
        
    Raises:
        HTTPException 404 si la historia no existe
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Construir el árbol completo de la historia
    complete_story = build_complete_story_tree(db, story)
    return complete_story

def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    """
    Construye la estructura completa de una historia con todos sus nodos.
    
    Convierte los nodos de la base de datos en una estructura jerárquica
    que incluye el nodo raíz y un diccionario con todos los nodos.
    
    Args:
        db: Sesión de base de datos
        story: Objeto Story de SQLAlchemy
        
    Returns:
        CompleteStoryResponse con la historia completa estructurada
        
    Raises:
        HTTPException 500 si no se encuentra el nodo raíz
    """
    # Obtener todos los nodos de esta historia
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()
    
    # Convertir cada nodo a su schema de respuesta
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options  # Las opciones ya están en formato JSON
        )
        node_dict[node.id] = node_response

    # Encontrar el nodo raíz (el punto de inicio de la historia)
    root_node = next((node for node in nodes if node.is_root), None)    
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")

    # Construir la respuesta completa
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],  # Nodo de inicio
        all_nodes=node_dict  # Diccionario con todos los nodos por ID
    )
"""
Modelos Pydantic para validar las respuestas del LLM (OpenAI).
Estos modelos definen la estructura JSON que esperamos recibir del modelo de lenguaje
cuando genera una historia interactiva.
"""

# Imports de typing para definir tipos complejos
from typing import List, Dict, Any, Optional

# Imports de Pydantic para validación de datos
from pydantic import BaseModel  # Clase base para crear modelos de datos
from pydantic import Field  # Para agregar metadatos y validaciones a los campos


class StoryOptionLLM(BaseModel):
    """
    Representa una opción de decisión en un nodo de la historia.
    
    Cada opción tiene un texto que se muestra al usuario y apunta
    al siguiente nodo de la historia (que puede ser otro nodo con opciones
    o un nodo final).
    """
    text: str = Field(description="the text of the option shown to the user")
    next_node: Dict[str, Any] = Field(description="the next node and its options")


class StoryNodeLLM(BaseModel):
    """
    Representa un nodo (fragmento) de la historia.
    
    Cada nodo contiene:
    - El contenido narrativo que se muestra al usuario
    - Flags que indican si es un final (y si es victoria o derrota)
    - Una lista de opciones que llevan a otros nodos (si no es un final)
    
    Esta estructura permite crear historias ramificadas tipo "elige tu propia aventura".
    """
    content: str = Field(description="The main content of the story node")
    isEnding: bool = Field(description="Whether this node is an ending node")
    isWinningEnding: bool = Field(description="Whether this node is a winning ending node")
    options: Optional[List[StoryOptionLLM]] = Field(default=None, description="The options for this node")   


class StoryLLMResponse(BaseModel):
    """
    Estructura completa de la respuesta del LLM al generar una historia.
    
    Contiene:
    - El título de la historia
    - El nodo raíz (punto de inicio) que contiene toda la estructura anidada
    
    El LLM debe devolver un JSON que cumpla con este esquema. Pydantic
    se encarga de validar que la respuesta sea correcta y convertirla a objetos Python.
    """
    title: str = Field(description="The title of the story")
    rootNode: StoryNodeLLM = Field(description="The root node of the story")
from sqlalchemy.orm import Session  # Importa Session para manejar la conexión y transacciones con la base de datos
from core.config import settings  # Importa la configuración de la aplicación

from langchain_openai import ChatOpenAI  # Importa la clase para interactuar con modelos de chat de OpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate  # Importa utilidades para crear plantillas de prompts
from langchain_core.output_parsers import PydanticOutputParser  # Importa el parser para convertir la salida del LLM a objetos Pydantic

from core.prompts import STORY_PROMPT  # Importa el prompt base para la generación de historias
from models.story import Story, StoryNode  # Importa los modelos de base de datos para Historia y Nodo de Historia
from core.models import StoryLLMResponse, StoryNodeLLM  # Importa los esquemas Pydantic para la estructura de respuesta del LLM


class StoryGenerator:
    """
    Clase encargada de la generación de historias interactivas utilizando LLMs.
    """
    
    @classmethod
    def _get_llm(cls):
        """
        Configura y devuelve una instancia del modelo de lenguaje (LLM).
        Usa 'gpt-4o' para la generación.
        """
        return ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
    
    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        """
        Genera una nueva historia basada en un tema dado.
        
        Args:
            db (Session): Sesión de base de datos.
            session_id (str): Identificador de la sesión del usuario.
            theme (str): Tema de la historia (por defecto 'fantasy').
            
        Returns:
            Story: El objeto de historia creado y guardado en la base de datos.
        """
        llm = cls._get_llm()
        # Configura el parser para validar que la salida del LLM cumpla con el esquema StoryLLMResponse
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        # Crea el template del prompt combinando el prompt del sistema y la entrada del usuario
        prompt = ChatPromptTemplate.from_messages([

            (
                "system",
                STORY_PROMPT
            ),
            (
                "human",
                f"Creando la historia con el tema: {theme}"        
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        # Invoca al LLM con el prompt generado
        raw_response = llm.invoke(prompt.invoke({}))


        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        # Parsea la respuesta de texto a una estructura de objetos Python (Pydantic)
        story_structure = story_parser.parse(response_text)

        # Crea el registro de la historia en la base de datos
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()  # Obtiene el ID de la historia sin confirmar la transacción aún
        
        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        # Procesa y guarda recursivamente los nodos de la historia comenzando por la raíz
        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()  # Confirma todos los cambios en la base de datos
        return story_db    
            


    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        """
        Procesa un nodo de historia y sus opciones recursivamente.
        
        Args:
            db (Session): Sesión de base de datos.
            story_id (int): ID de la historia a la que pertenece el nodo.
            node_data (StoryNodeLLM): Datos del nodo provenientes del LLM.
            is_root (bool): Indica si es el nodo raíz de la historia.
            
        Returns:
            StoryNode: El objeto de nodo creado.
        """
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"],
            options=[]
        )

        db.add(node)
        db.flush()

        # Si no es un final y tiene opciones, procesa las opciones recursivamente
        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.next_node

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                # Llamada recursiva para crear el nodo hijo
                child_node = cls._process_story_node(db, story_id, next_node, False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()
        return node
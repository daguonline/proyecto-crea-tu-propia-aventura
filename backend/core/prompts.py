"""
Prompts para el modelo de lenguaje (LLM).
Define las instrucciones que se envían a OpenAI para generar historias interactivas.
"""

# Prompt principal que se envía al LLM para generar una historia completa
STORY_PROMPT = """
                You are a creative story writer that creates engaging choose-your-own-adventure stories.
                Generate a complete branching story with multiple paths and endings in the JSON format I'll specify.

                The story should have:
                1. A compelling title
                2. A starting situation (root node) with 2-3 options
                3. Each option should lead to another node with its own options
                4. Some paths should lead to endings (both winning and losing)
                5. At least one path should lead to a winning ending

                Story structure requirements:
                - Each node should have 2-3 options except for ending nodes
                - The story should be 3-4 levels deep (including root node)
                - Add variety in the path lengths (some end earlier, some later)
                - Make sure there's at least one winning path
                - You must adapt all content to the user's login language.

                Output your story in this exact JSON structure:
                {format_instructions}

                Don't simplify or omit any part of the story structure. 
                Don't add any text outside of the JSON structure.
                """

# Ejemplo de la estructura JSON esperada (solo para referencia, no se usa directamente)
# El parser de Pydantic genera las instrucciones de formato automáticamente
json_structure = """
        {
            "title": "Story Title",
            "rootNode": {
                "content": "The starting situation of the story",
                "isEnding": false,
                "isWinningEnding": false,
                "options": [
                    {
                        "text": "Option 1 text",
                        "nextNode": {
                            "content": "What happens for option 1",
                            "isEnding": false,
                            "isWinningEnding": false,
                            "options": [
                                // More nested options
                            ]
                        }
                    },
                    // More options for root node
                ]
            }
        }
        """
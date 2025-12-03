/**
 * Componente StoryGame
 * 
 * Este es el componente principal del juego interactivo.
 * Renderiza el nodo actual de la historia, muestra el contenido y las opciones disponibles.
 * También maneja la lógica de navegación entre nodos y la pantalla de finalización.
 */
import { useState, useEffect } from 'react';

function StoryGame({ story, onNewStory }) {
    const [currentNodeId, setCurrentNodeId] = useState(null);
    const [currentNode, setCurrentNode] = useState(null);
    const [options, setOptions] = useState([]);
    const [isEnding, setIsEnding] = useState(false);
    const [isWinningEnding, setIsWinningEnding] = useState(false);

    useEffect(() => {
        if (story && story.root_node) {
            const rootNodeId = story.root_node.id;
            setCurrentNodeId(rootNodeId);
        }
    }, [story]);

    useEffect(() => {
        if (currentNodeId && story && story.all_nodes) {
            const node = story.all_nodes[currentNodeId];

            setCurrentNode(node);
            setIsEnding(node.is_ending);
            setIsWinningEnding(node.is_winning_ending);

            if (!node.is_ending && node.options && node.options.length > 0) {
                setOptions(node.options);
            } else {
                setOptions([]);
            }
        }
    }, [currentNodeId, story]);

    const chooseOption = (optionId) => {
        setCurrentNodeId(optionId);
    };

    const restartStory = () => {
        if (story && story.root_node) {
            setCurrentNodeId(story.root_node.id);
        }
    };

    if (!currentNode) {
        return <div className="story-game">Cargando historia...</div>;
    }

    return (
        <div className="story-game">
            <header className="story-header">
                <h2>{story.title}</h2>
            </header>

            <div className="story-content">
                <p>{currentNode.content}</p>

                {isEnding ? (
                    <div className="story-ending">
                        <h3>{isWinningEnding ? "¡Felicidades!" : "Fin"}</h3>
                        <p>{isWinningEnding ? "Has ganado" : "Has perdido"}</p>

                        <div className="ending-actions">
                            <button onClick={restartStory} className="restart-btn">
                                Jugar de nuevo
                            </button>
                            <button onClick={onNewStory} className="new-story-btn">
                                Crear nueva historia
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="story-options">
                        <h3>¿Qué quieres hacer?</h3>
                        <div className="option-list">
                            {options.map((option, index) => (
                                <button
                                    key={index}
                                    onClick={() => chooseOption(option.node_id)}
                                    className="option-btn"
                                >
                                    {option.text}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default StoryGame;
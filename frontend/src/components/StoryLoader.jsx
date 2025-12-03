/**
 * Componente StoryLoader
 * 
 * Este componente se encarga de cargar una historia existente desde el backend usando su ID.
 * Muestra un estado de carga, maneja errores si la historia no existe, y renderiza
 * el juego (StoryGame) una vez que los datos están listos.
 */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from 'axios';
import LoadingStatus from "./LoadingStatus.jsx";
import StoryGame from "./StoryGame.jsx";
import { API_BASE_URL } from "../util";


function StoryLoader() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [story, setStory] = useState(null);
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null);

    useEffect(() => {
        loadStory(id)
    }, [id])

    const loadStory = async (storyId) => {
        setLoading(true)
        setError(null)

        try {
            const response = await axios.get(`${API_BASE_URL}/story/${storyId}/complete`)
            setStory(response.data)
            setLoading(false)
        } catch (err) {
            if (err.response?.status === 404) {
                setError("Historia no encontrada")
            } else {
                setError("Error al cargar la historia")
            }
        } finally {
            setLoading(false)
        }
    }

    const createNewStory = () => {
        navigate("/")
    }

    if (loading) {
        return <LoadingStatus theme={"story"} />
    }

    if (error) {
        return <div className="story-loader">
            <div className="error-message">
                <h2>Historia no encontrada</h2>
                <p>{error}</p>
                <button onClick={createNewStory}>Crear nueva historia</button>
            </div>
        </div>
    }

    if (story) {
        return <div className="story-loader">
            <StoryGame story={story} onNewStory={createNewStory} />
        </div>
    }

    return null;
}

export default StoryLoader;
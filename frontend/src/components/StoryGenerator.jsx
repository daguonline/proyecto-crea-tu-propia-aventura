/**
 * Componente StoryGenerator
 * 
 * Este componente maneja la creación de nuevas historias.
 * Permite al usuario ingresar un tema, envía la solicitud al backend,
 * y hace polling del estado del trabajo hasta que la historia esté lista.
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import LoadingStatus from "./LoadingStatus.jsx";
import ThemeInput from "./ThemeImput.jsx";
import { API_BASE_URL } from "../util";

function StoryGenerator() {
    const navigate = useNavigate();
    const [theme, setTheme] = useState("");
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        let pollInterval;

        // Hacer polling mientras el job esté pendiente o procesando
        if (jobId && (jobStatus === "pending" || jobStatus === "procesando")) {
            pollInterval = setInterval(() => {
                pollJobStatus(jobId);
            }, 3000); // Cada 3 segundos
        }

        return () => {
            if (pollInterval) {
                clearInterval(pollInterval);
            }
        };
    }, [jobId, jobStatus]);

    const generateStory = async (theme) => {
        setLoading(true);
        setError(null);
        setTheme(theme);

        try {
            const response = await axios.post(`${API_BASE_URL}/story/create`, { theme });
            const { job_id, status } = response.data;
            setJobId(job_id);
            setJobStatus(status);

            // Iniciar polling inmediatamente
            pollJobStatus(job_id);
        } catch (e) {
            setError(`Error al generar la historia: ${e.message}`);
            setLoading(false);
        }
    };

    const pollJobStatus = async (id) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/job/${id}`);
            const { status, story_id, error: jobError } = response.data;

            console.log(`Job ${id}: status=${status}, story_id=${story_id}, error=${jobError}`);

            setJobStatus(status);

            if (status === "completado" && story_id) {
                console.log(`Historia completada, navegando a /story/${story_id}`);
                fetchStory(story_id);
            } else if (status === "error" || jobError) {
                console.error(`Error en job: ${jobError}`);
                setError(jobError || "Error al generar la historia");
                setLoading(false);
            }
        } catch (e) {
            console.error(`Error al consultar job: ${e.message}`, e.response);
            if (e.response?.status !== 404) {
                setError(`Error al verificar el estado: ${e.message}`);
                setLoading(false);
            }
        }
    };

    const fetchStory = async (id) => {
        try {
            setLoading(false);
            setJobStatus("completado");
            navigate(`/story/${id}`);
        } catch (e) {
            setError(`Error al cargar la historia: ${e.message}`);
            setLoading(false);
        }
    };

    const reset = () => {
        setTheme("");
        setJobId(null);
        setJobStatus(null);
        setError(null);
        setLoading(false);
    };

    return (
        <div className="story-generator">
            {error && (
                <div className="error-message">
                    <p>{error}</p>
                    <button onClick={reset}>Intentar de nuevo</button>
                </div>
            )}

            {!jobId && !error && !loading && <ThemeInput onSubmit={generateStory} />}

            {loading && <LoadingStatus theme={theme} />}
        </div>
    );
}

export default StoryGenerator;

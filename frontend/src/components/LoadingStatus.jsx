/**
 * Componente LoadingStatus
 * 
 * Muestra una animación de carga y un mensaje personalizado mientras
 * se generan o recuperan los datos de la historia.
 */
function LoadingStatus({ theme }) {
    return <div className="loading-container">
        <h2>{theme === "story" ? "Cargando historia" : `Generando tu ${theme}`}</h2>

        <div className="loading-animation">
            <div className="spinner"></div>
        </div>


        <p className="loading-info">
            {theme === "story" ? "Cargando historia..." : `Por favor espera, estamos generando tu ${theme}...`}
        </p>


    </div>

}

export default LoadingStatus;

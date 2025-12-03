/**
 * Componente ThemeImput
 * 
 * Este componente permite al usuario ingresar un tema para generar una nueva historia.
 * Maneja la validación del input y envía el tema al componente padre.
 */
import { useState } from "react"

function ThemeImput({ onSubmit }) {
    const [theme, setTheme] = useState("");
    const [error, setError] = useState("")

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!theme.trim()) {
            setError("Por favor ingresa el nombre de un tema");
            return
        }
        onSubmit(theme)
    }

    return <div className="theme-imput-container">
        <h2>Genera tu aventura</h2>
        <p>Indica el tema sobre el que quieres que se desarrolle la historia</p>

        <form onSubmit={handleSubmit}>
            <div className="input-group">
                <input
                    type="text"
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    placeholder="Ingresa el tema (ej. piratas, fantasía, anime, etc.)"
                    className={error ? "error" : ""}
                />
                {error && <p className="error-text">{error}</p>}

            </div>
            <button type="submit" className='generate-btn'>
                Generar Historia
            </button>

        </form>

    </div>

}

export default ThemeImput;

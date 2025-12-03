// En desarrollo: usa el proxy de Vite (/api -> http://localhost:8000)
// En producción: usa la variable de entorno VITE_API_URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";
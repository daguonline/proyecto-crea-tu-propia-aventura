import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_story_generation():
    print("1. Iniciando generación de historia con Gemini...")
    try:
        response = requests.post(f"{BASE_URL}/story/create", json={"theme": "espacio exterior"})
        response.raise_for_status()
        data = response.json()
        job_id = data["job_id"]
        print(f"   Job creado: {job_id}")
    except Exception as e:
        print(f"   Error al crear job: {e}")
        return

    print("2. Esperando a que se complete el trabajo (Polling)...")
    for i in range(20):  # Intentar por 60 segundos (20 * 3s)
        time.sleep(3)
        try:
            job_response = requests.get(f"{BASE_URL}/job/{job_id}")
            job_response.raise_for_status()
            job_data = job_response.json()
            status = job_data["status"]
            print(f"   Intento {i+1}: Estado = {status}")

            if status == "completado":
                print(f"   ¡Éxito! Historia generada. ID: {job_data['story_id']}")
                return
            elif status == "error":
                print(f"   Error en el trabajo: {job_data.get('error')}")
                return
        except Exception as e:
            print(f"   Error al consultar job: {e}")
    
    print("   Tiempo de espera agotado.")

if __name__ == "__main__":
    test_story_generation()

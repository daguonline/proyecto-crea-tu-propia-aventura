import requests
import os

API_KEY = "AIzaSyAmZhllRRlkc40sw7CX9eis_l2dsOkgG_0"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print("Available models:")
    for model in data.get('models', []):
        if 'gemini' in model['name']:
            print(f"- {model['name']}")
except Exception as e:
    print(f"Error: {e}")

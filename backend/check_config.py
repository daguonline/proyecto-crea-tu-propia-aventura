import sys
import os

# Add the current directory to sys.path to make sure we can import core
sys.path.append(os.getcwd())

try:
    from core.config import settings
    print(f"GEMINI_API_KEY loaded: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
    if settings.GEMINI_API_KEY:
        print(f"Key starts with: {settings.GEMINI_API_KEY[:5]}...")
        print(f"Key length: {len(settings.GEMINI_API_KEY)}")
    else:
        print("GEMINI_API_KEY is empty string or None")
        
    print(f"OPENAI_API_KEY loaded: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
except Exception as e:
    print(f"Error loading settings: {e}")

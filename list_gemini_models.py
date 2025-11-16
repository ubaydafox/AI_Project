import os
import google.generativeai as genai

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    models = genai.list_models()
    print("Available Gemini models for your API key:")
    for m in models:
        print(m.name)
except Exception as e:
    print(f"Error: {e}")

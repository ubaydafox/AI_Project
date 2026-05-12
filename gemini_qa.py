import os
import json
import google.generativeai as genai
from datetime import datetime
from constants import DATA_DIR

def ask_gemini(question, history=None, user_batch="Unknown"):
    # Get current date and time
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Load your data using absolute paths from constants
    try:
        with open(DATA_DIR / 'routine_data.json', encoding='utf-8') as f:
            routine = json.load(f)
        with open(DATA_DIR / 'faculty_info.json', encoding='utf-8') as f:
            faculty = json.load(f)
        with open(DATA_DIR / 'course_info.json', encoding='utf-8') as f:
            courses = json.load(f)
        with open(DATA_DIR / 'bus_info.json', encoding='utf-8') as f:
            bus = json.load(f)
    except Exception as e:
        return f"Error loading data for Gemini: {e}"

    # Prepare the prompt with current date/time and short-term history
    history_text = ""
    if history:
        for role, msg in history:
            history_text += f"[{role}] {msg}\n"
            
    prompt = f"""
    [SYSTEM: Current date and time is {now}]
    Your name is MetroMate. You are a helpful Telegram bot for university routine, faculty, course, and bus info.
    If anyone asks about your name, always reply: 'Hi, I'm MetroMate.'
    If anyone asks about your developer, reply: 'I was developed by Abu Ubayda and Nahidul Islam Roni.'
    
    User Batch: {user_batch}
    
    Here is the campus data:
    Routine: {json.dumps(routine, ensure_ascii=False)}
    Faculty: {json.dumps(faculty, ensure_ascii=False)}
    Courses: {json.dumps(courses, ensure_ascii=False)}
    Bus Schedule: {json.dumps(bus, ensure_ascii=False)}
    
    {(f'Recent conversation history:\n{history_text}' if history_text else '')}
    
    User question: {question}
    
    Instructions:
    1. Answer in Bangla if the question is in Bangla, otherwise in English.
    2. Be concise but helpful.
    3. Use the provided data to answer routine or bus related questions.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key not configured."
        
    genai.configure(api_key=api_key)
    try:
        # Use gemini-1.5-flash as it is fast and reliable for this task
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API error: {e}"

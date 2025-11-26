import os
import json
import google.generativeai as genai
from datetime import datetime

def ask_gemini(question, history=None):
    # Get current date and time
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Load your data
    with open('data/routine_data.json', encoding='utf-8') as f:
        routine = json.load(f)
    with open('data/faculty_info.json', encoding='utf-8') as f:
        faculty = json.load(f)
    with open('data/course_info.json', encoding='utf-8') as f:
        courses = json.load(f)
    with open('data/bus_info.json', encoding='utf-8') as f:
        bus = json.load(f)

    # Prepare the prompt with current date/time and short-term history
    history_text = ""
    if history:
        for role, msg in history:
            history_text += f"[{role}] {msg}\n"
    prompt = f"""
    [SYSTEM: Current date and time is {now}]
    Your name is MetroMate. You are a helpful Telegram bot for university routine, faculty, course, and bus info. If anyone asks about your name, always reply: 'Hi, I'm MetroMate.'
    If anyone asks about your developer, reply: 'I was developed by Abu Ubayda and Nahidul Islam Roni.'
    Here is the data:
    Routine: {routine}
    Faculty: {faculty}
    Courses: {courses}
    Bus Schedule: {bus}
    {(f'Recent conversation:\n{history_text}' if history_text else '')}
    User question: {question}
    Answer in Bangla if the question is in Bangla, otherwise in English.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API error: {e}"

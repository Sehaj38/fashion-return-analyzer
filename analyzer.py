from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

def setup_groq():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass

    if not api_key:
        raise ValueError("GROQ_API_KEY not found!")

    client = Groq(api_key=api_key)
    return client

def analyze_reviews(reviews_text):
    prompt = f"""
    You are a fashion retail analyst. Your response must be a single valid JSON object.
    
    STRICT RULES:
    - Return ONLY the JSON object
    - NO markdown, NO code fences, NO backticks
    - NO comments inside JSON
    - NO trailing commas
    - All strings must use double quotes
    - score must be an integer between 0 and 100
    - level must be exactly one of: Low, Medium, High
    
    Required JSON structure:
    {{
        "top_complaints": [
            {{"complaint": "title here", "description": "explanation here"}},
            {{"complaint": "title here", "description": "explanation here"}},
            {{"complaint": "title here", "description": "explanation here"}}
        ],
        "return_risk": {{
            "level": "High",
            "score": 75,
            "reason": "one sentence explanation here"
        }},
        "recommendations": [
            {{"title": "title here", "action": "action here"}},
            {{"title": "title here", "action": "action here"}},
            {{"title": "title here", "action": "action here"}}
        ],
        "summary": "exactly two sentences summarizing the reviews here"
    }}
    
    Customer reviews to analyze:
    {reviews_text}
    """

    client = setup_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\n\nRaw response:\n{raw}")
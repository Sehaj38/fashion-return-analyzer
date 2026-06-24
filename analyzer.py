from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

def setup_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file")
    client = Groq(api_key=api_key)
    return client

def analyze_reviews(reviews_text):
    prompt = f"""
    You are a fashion retail analyst helping reduce product returns.
    
    Analyze the following customer reviews and respond ONLY with a JSON object.
    No explanation, no markdown, no extra text. Just raw JSON.
    
    The JSON must follow this exact structure:
    {{
        "top_complaints": [
            {{"complaint": "complaint title", "description": "brief explanation"}},
            {{"complaint": "complaint title", "description": "brief explanation"}},
            {{"complaint": "complaint title", "description": "brief explanation"}}
        ],
        "return_risk": {{
            "level": "High",
            "score": 78,
            "reason": "one sentence explanation"
        }},
        "recommendations": [
            {{"title": "recommendation title", "action": "specific action to take"}},
            {{"title": "recommendation title", "action": "specific action to take"}},
            {{"title": "recommendation title", "action": "specific action to take"}}
        ],
        "summary": "2 sentence overall summary of the reviews"
    }}
    
    Rules:
    - return_risk level must be exactly: Low, Medium, or High
    - return_risk score must be a number between 0 and 100
    - Return ONLY the JSON, nothing else
    
    Here are the customer reviews:
    {reviews_text}
    """

    client = setup_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content

    # Clean response in case AI adds markdown code fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    # Parse JSON string into Python dictionary
    result = json.loads(raw)
    return result
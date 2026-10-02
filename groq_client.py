import json
from config import GROQ_API_KEY

MODEL = 'llama-3.3-70b-versatile'

def available():
    return bool(GROQ_API_KEY)

def _client():
    if not GROQ_API_KEY:
        return None
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)

def ask_json(system, prompt, default):
    if not GROQ_API_KEY:
        return default
    try:
        client = _client()
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{'role':'system','content':system},{'role':'user','content':prompt}],
            temperature=0.1,
            response_format={'type':'json_object'},
        )
        data = json.loads(r.choices[0].message.content)
        return data if isinstance(data, dict) else default
    except Exception:
        return default

def ask_text(system, prompt, default=''):
    if not GROQ_API_KEY:
        return default
    try:
        client = _client()
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{'role':'system','content':system},{'role':'user','content':prompt}],
            temperature=0.2,
        )
        return (r.choices[0].message.content or default).strip()
    except Exception:
        return default

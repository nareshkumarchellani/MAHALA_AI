from groq_client import ask_json

def run(text, language='English'):
    default = {
        'clean_text': (text or '').strip(),
        'language': language if language in ['English', 'Urdu'] else 'English'
    }
    r = ask_json(
        'You are a civic complaint intake agent. Output JSON only. Support English and Urdu only. Do not invent facts.',
        f'Clean and detect this complaint. Return clean_text and language only. Complaint: {text}',
        default,
    )
    clean = str(r.get('clean_text') or default['clean_text']).strip()
    lang = r.get('language') if r.get('language') in ['English', 'Urdu'] else default['language']
    return {'clean_text': clean, 'language': lang}

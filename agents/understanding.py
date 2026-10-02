from groq_client import ask_json
from config import CATEGORIES

def run(text, language='English'):
    default = {
        'title': (text or '').strip()[:70] or 'Civic complaint',
        'summary': (text or '').strip(),
        'category': 'Other',
        'subcategory': 'General',
        'entities': [],
        'location_clues': [],
        'severity_clues': [],
    }
    r = ask_json(
        'You classify Pakistan civic complaints. JSON only. Do not invent facts. '
        'Use exactly one category from the supplied list. Support English and Urdu.',
        f'Complaint language: {language}\nComplaint: {text}\nCategories: {", ".join(CATEGORIES)}',
        default,
    )
    category = r.get('category') if r.get('category') in CATEGORIES else 'Other'
    title = str(r.get('title') or default['title']).strip()[:120]
    summary = str(r.get('summary') or default['summary']).strip()
    return {
        'title': title or default['title'],
        'summary': summary or default['summary'],
        'category': category,
        'subcategory': str(r.get('subcategory') or 'General').strip()[:80],
        'entities': r.get('entities') if isinstance(r.get('entities'), list) else [],
        'location_clues': r.get('location_clues') if isinstance(r.get('location_clues'), list) else [],
        'severity_clues': r.get('severity_clues') if isinstance(r.get('severity_clues'), list) else [],
    }

from groq_client import ask_json

PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

def run(text, category, summary):
    default = {
        'priority': 'Medium',
        'impact_score': 55,
        'reasoning': 'Demo-mode assessment based only on the supplied complaint.'
    }
    r = ask_json(
        'Assess civic complaint priority using only supplied facts. JSON only. '
        'Priority must be Low, Medium, High, or Critical; impact_score 0-100. Do not invent facts.',
        f'Category: {category}\nComplaint: {text}\nSummary: {summary}',
        default,
    )
    priority = r.get('priority') if r.get('priority') in PRIORITIES else 'Medium'
    try:
        score = max(0, min(100, int(r.get('impact_score', 55))))
    except (TypeError, ValueError):
        score = 55
    reasoning = str(r.get('reasoning') or default['reasoning']).strip()[:500]
    return {'priority': priority, 'impact_score': score, 'reasoning': reasoning}

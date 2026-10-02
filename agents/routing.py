from groq_client import ask_json

MAP = {
    'Garbage / Waste': 'Waste Management',
    'Water': 'Water & Sewerage',
    'Sewerage': 'Water & Sewerage',
    'Roads': 'Roads & Infrastructure',
    'Electricity': 'Electricity',
    'Street Lights': 'Municipal Services',
    'Parks': 'Parks & Public Spaces',
    'Public Spaces': 'Municipal Services',
    'Public Safety': 'Public Safety',
    'Other': 'Municipal Services',
}

def run(category, text, departments):
    names = [d.get('name') for d in departments if d.get('name')]
    fallback = MAP.get(category, names[0] if names else 'Other')
    if names and fallback not in names:
        fallback = names[0]
    default = {'department': fallback, 'reasoning': 'Category-based routing in demo mode.'}
    if not names:
        return default
    r = ask_json(
        'Route civic complaints to the most relevant department. JSON only. '
        'Choose only from supplied departments. Do not invent departments.',
        f'Category: {category}\nComplaint: {text}\nDepartments: {names}',
        default,
    )
    dept = r.get('department') if r.get('department') in names else fallback
    return {'department': dept, 'reasoning': str(r.get('reasoning') or default['reasoning'])[:500]}

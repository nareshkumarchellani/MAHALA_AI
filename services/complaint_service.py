from pathlib import Path
import uuid
from config import UPLOAD_DIR
from database import execute, one, query, now
from agents.intake import run as intake
from agents.understanding import run as understanding
from agents.duplicate import run as duplicate
from agents.clustering import run as clustering
from agents.evidence import run as evidence
from agents.priority import run as priority
from agents.routing import run as routing
from services.notification_service import notify

ALLOWED_UPLOADS = {
    'jpg','jpeg','png','webp','mp4','mov','avi','wav','mp3','m4a','ogg'
}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

def analyze_and_create(citizen_id, text, language, category_hint=None, latitude=None,
                       longitude=None, address='', evidence_type=None, evidence_path=None):
    raw = intake(text, language)
    clean = raw.get('clean_text') or text
    understood = understanding(clean, language)
    if category_hint and category_hint != 'Other':
        understood['category'] = category_hint

    existing = query('SELECT * FROM complaints ORDER BY id DESC LIMIT 100')
    dup = duplicate(clean, understood['category'], latitude, longitude, existing)
    cases = query('SELECT * FROM community_cases ORDER BY id DESC')
    cl = clustering(understood['category'], latitude, longitude, cases)
    ev = evidence(evidence_type, evidence_path, latitude, longitude, address)
    pri = priority(clean, understood['category'], understood['summary'])
    departments = query('SELECT * FROM departments WHERE active=1')
    rt = routing(understood['category'], clean, departments)
    dept = next((d for d in departments if d['name'] == rt['department']), None)

    if not ev['evidence_valid']:
        raise ValueError('The evidence file could not be validated.')

    case_id = cl['case']['id'] if cl.get('case') else None
    cid = execute(
        '''INSERT INTO complaints(
            citizen_id,title,description,language,category,subcategory,latitude,longitude,address,
            evidence_type,evidence_path,ai_summary,ai_priority,impact_score,duplicate_of,
            community_case_id,routed_department_id,status,citizen_confirmed,government_submitted,
            created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (
            citizen_id, understood['title'], clean, language, understood['category'],
            understood.get('subcategory'), latitude, longitude, address,
            ev['evidence_type'], evidence_path, understood['summary'], pri['priority'],
            pri['impact_score'], dup['related']['id'] if dup['is_duplicate'] and dup.get('related') else None,
            case_id, dept['id'] if dept else None, 'Submitted', 0, 0, now(), now()
        )
    )

    if case_id:
        execute(
            'UPDATE community_cases SET complaint_count=complaint_count+1,updated_at=? WHERE id=?',
            (now(), case_id)
        )
    elif latitude is not None and longitude is not None:
        case_title = f"{understood['category']} Issue - {address or 'Community Area'}"
        case_id = execute(
            '''INSERT INTO community_cases(
                title,category,description,complaint_count,latitude,longitude,area_name,
                priority,status,routed_department_id,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
            (
                case_title, understood['category'], understood['summary'], 1,
                latitude, longitude, address or 'Community Area', pri['priority'],
                'Submitted', dept['id'] if dept else None, now(), now()
            )
        )
        execute('UPDATE complaints SET community_case_id=? WHERE id=?', (case_id, cid))

    execute(
        'INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',
        (cid, dept['id'] if dept else None, 'Submitted',
         'AI analysis complete. Awaiting citizen confirmation.', now())
    )
    notify(
        citizen_id, 'AI analysis complete',
        f'Complaint #{cid} was analyzed and is ready for your confirmation.'
    )
    return {
        'complaint_id': cid,
        'understanding': understood,
        'priority': pri,
        'routing': rt,
        'duplicate': dup,
        'community_case_id': case_id,
    }

def get_for_citizen(citizen_id):
    return query(
        '''SELECT c.*,d.name department FROM complaints c
           LEFT JOIN departments d ON d.id=c.routed_department_id
           WHERE c.citizen_id=? ORDER BY c.id DESC''', (citizen_id,)
    )

def get_one(cid, citizen_id=None):
    if citizen_id is None:
        return one(
            '''SELECT c.*,d.name department FROM complaints c
               LEFT JOIN departments d ON d.id=c.routed_department_id WHERE c.id=?''', (cid,)
        )
    return one(
        '''SELECT c.*,d.name department FROM complaints c
           LEFT JOIN departments d ON d.id=c.routed_department_id
           WHERE c.id=? AND c.citizen_id=?''', (cid, citizen_id)
    )

def history(cid):
    return query(
        '''SELECT cu.*,d.name department FROM case_updates cu
           LEFT JOIN departments d ON d.id=cu.department_id
           WHERE cu.complaint_id=? ORDER BY cu.id ASC''', (cid,)
    )

def confirm_submit(cid, citizen_id):
    c = get_one(cid, citizen_id)
    if not c:
        return False, 'Complaint not found.'
    if c['citizen_confirmed'] and c['government_submitted']:
        return True, 'This complaint has already been submitted.'
    execute(
        '''UPDATE complaints SET citizen_confirmed=1,government_submitted=1,
           status='Under Review',updated_at=? WHERE id=? AND citizen_id=?''',
        (now(), cid, citizen_id)
    )
    execute(
        'INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',
        (cid, c['routed_department_id'], 'Under Review',
         'Citizen confirmed the complaint for department submission.', now())
    )
    notify(
        citizen_id, 'Complaint submitted',
        f'Complaint #{cid} was submitted to the routed department.'
    )
    return True, 'Submitted successfully.'

def save_upload(uploaded):
    if not uploaded:
        return None
    name = getattr(uploaded, 'name', '') or ''
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    size = getattr(uploaded, 'size', None)
    if ext not in ALLOWED_UPLOADS or (size is not None and size > MAX_UPLOAD_BYTES):
        return None
    data = uploaded.getvalue()
    if len(data) > MAX_UPLOAD_BYTES:
        return None
    path = UPLOAD_DIR / f'{uuid.uuid4().hex}.{ext}'
    path.write_bytes(data)
    return str(path)

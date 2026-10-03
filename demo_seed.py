"""Extra demo data for MAHALA AI (idempotent: safe to run many times)."""
from datetime import datetime, timedelta, timezone

from database import get_conn, hash_password

PASSWORD = 'demo123'
NUM_CITIZENS = 10

NEW_DEPARTMENTS = [
    ('Electricity', 'ELEC', 'electricity'),
    ('Parks & Public Spaces', 'PARKS', 'parks'),
    ('Public Safety', 'SAFETY', 'safety'),
]

CITIZEN_NAMES = [
    'Ali Raza', 'Sana Khan', 'Bilal Ahmed', 'Hina Siddiqui', 'Usman Malik',
    'Ayesha Noor', 'Hamza Sheikh', 'Fatima Zehra', 'Imran Qureshi', 'Zainab Ali',
]

AREAS = {
    'gulshan': ('Gulshan-e-Iqbal', 24.9215, 67.0920),
    'saddar': ('Saddar', 24.8607, 67.0011),
    'pechs': ('PECHS', 24.8700, 67.0700),
    'korangi': ('Korangi', 24.8300, 67.1300),
    'nazimabad': ('North Nazimabad', 24.9400, 67.0400),
    'lyari': ('Lyari', 24.8600, 66.9900),
    'clifton': ('Clifton', 24.8138, 67.0300),
    'malir': ('Malir', 24.8900, 67.2000),
    'orangi': ('Orangi Town', 24.9500, 66.9900),
    'dha': ('DHA Phase 5', 24.8000, 67.0600),
}

CATEGORY_DEPT = {
    'Garbage / Waste': 'Waste Management',
    'Roads': 'Roads & Infrastructure',
    'Water': 'Water & Sewerage',
    'Sewerage': 'Water & Sewerage',
    'Street Lights': 'Municipal Services',
    'Electricity': 'Electricity',
    'Parks': 'Parks & Public Spaces',
    'Public Spaces': 'Municipal Services',
    'Public Safety': 'Public Safety',
    'Other': 'Municipal Services',
}

STATUS_FLOW = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Closed']
STATUS_NOTES = {
    'Submitted': 'Complaint received and analyzed by MAHALA AI.',
    'Under Review': 'Citizen confirmed the complaint for department submission.',
    'Assigned': 'Case assigned to a field team.',
    'In Progress': 'Field team is working on the issue.',
    'Resolved': 'Department marked the issue as resolved.',
    'Closed': 'Citizen confirmed the resolution.',
    'Reopened': 'Citizen reopened the issue.',
}

IMPACT_RANGE = {'Low': (15, 30), 'Medium': (40, 60), 'High': (65, 80), 'Critical': (85, 97)}

COMMUNITY_CASES = {
    'gulshan_garbage': ('Garbage Waste Issue - Gulshan-e-Iqbal', 'Garbage / Waste', 'gulshan', 'High', 'In Progress',
                        'Garbage has not been collected for days across several blocks.'),
    'saddar_road': ('Roads Issue - Saddar', 'Roads', 'saddar', 'High', 'Assigned',
                    'Broken roads and deep potholes causing traffic and accident risk.'),
    'korangi_sewer': ('Sewerage Issue - Korangi', 'Sewerage', 'korangi', 'Critical', 'Under Review',
                      'Overflowing sewage is flooding streets and entering homes.'),
    'lyari_water': ('Water Issue - Lyari', 'Water', 'lyari', 'High', 'Under Review',
                    'Several lanes report no water supply and leaking main pipes.'),
    'nazimabad_lights': ('Street Lights Issue - North Nazimabad', 'Street Lights', 'nazimabad', 'Medium', 'Submitted',
                         'Street lights are out on multiple roads after sunset.'),
    'orangi_power': ('Electricity Issue - Orangi Town', 'Electricity', 'orangi', 'Critical', 'In Progress',
                     'Exposed live wires and repeated transformer failures.'),
    'clifton_park': ('Parks Issue - Clifton', 'Parks', 'clifton', 'Low', 'Resolved',
                     'Park benches broken and play area needs maintenance.'),
    'malir_safety': ('Public Safety Issue - Malir', 'Public Safety', 'malir', 'High', 'Assigned',
                     'Open manholes and unsafe crossings near schools.'),
}

# (citizen no., title, description, category, area, priority, status, community case, days ago)
COMPLAINTS = [
    (1, 'Garbage not collected for 5 days', 'Garbage has not been picked up for five days and the smell is unbearable near our block.', 'Garbage / Waste', 'gulshan', 'High', 'In Progress', 'gulshan_garbage', 6),
    (2, 'Overflowing garbage bin', 'The public garbage bin on the main road is overflowing and attracting stray animals.', 'Garbage / Waste', 'gulshan', 'Medium', 'Assigned', 'gulshan_garbage', 5),
    (3, 'Garbage burning in open plot', 'People are burning garbage in the empty plot next to our building and smoke enters our homes.', 'Garbage / Waste', 'gulshan', 'High', 'Under Review', 'gulshan_garbage', 3),
    (4, 'Large pothole on main road', 'A very large pothole is causing accidents for motorcycles near the market.', 'Roads', 'saddar', 'High', 'Assigned', 'saddar_road', 8),
    (5, 'Road caved in after rain', 'Part of the road has sunk after rain and is dangerous for vehicles at night.', 'Roads', 'saddar', 'Critical', 'In Progress', 'saddar_road', 4),
    (6, 'Missing speed breaker marking', 'The speed breaker near the school has no paint or signs and is hard to see.', 'Roads', 'saddar', 'Low', 'Submitted', 'saddar_road', 2),
    (7, 'Sewage overflowing on street', 'Dirty sewage water is overflowing on the street and entering shops.', 'Sewerage', 'korangi', 'Critical', 'Under Review', 'korangi_sewer', 4),
    (8, 'Blocked sewer line in lane', 'The sewer line in our lane has been blocked for a week and the lane is flooded with dirty water.', 'Sewerage', 'korangi', 'High', 'Assigned', 'korangi_sewer', 7),
    (9, 'Foul smell from open drain', 'An open drain is releasing a strong smell and mosquitoes are increasing.', 'Sewerage', 'korangi', 'Medium', 'Under Review', 'korangi_sewer', 5),
    (10, 'No water supply for 3 days', 'There has been no water in our area for three days and families are buying tankers.', 'Water', 'lyari', 'High', 'Under Review', 'lyari_water', 3),
    (1, 'Main water pipe leaking', 'A main water pipe is leaking and wasting water all day beside the road.', 'Water', 'lyari', 'Medium', 'Assigned', 'lyari_water', 6),
    (2, 'Low water pressure', 'Water pressure is very low in the mornings and does not reach the upper floors.', 'Water', 'lyari', 'Low', 'Submitted', 'lyari_water', 1),
    (3, 'Street lights not working', 'Four street lights on our road are not working and the road is completely dark at night.', 'Street Lights', 'nazimabad', 'Medium', 'Submitted', 'nazimabad_lights', 2),
    (4, 'Flickering street light', 'A street light keeps flickering near the park entrance every evening.', 'Street Lights', 'nazimabad', 'Low', 'Under Review', 'nazimabad_lights', 4),
    (5, 'Dark road with snatching incidents', 'The road is dark because the lights are broken and there were two snatching incidents this week.', 'Street Lights', 'nazimabad', 'High', 'Assigned', 'nazimabad_lights', 3),
    (6, 'Exposed live wires near children', 'Live electrical wires are hanging low near a children play area and are very dangerous.', 'Electricity', 'orangi', 'Critical', 'In Progress', 'orangi_power', 2),
    (7, 'Transformer sparking', 'The transformer on our street is sparking every night and may cause a fire.', 'Electricity', 'orangi', 'Critical', 'Assigned', 'orangi_power', 3),
    (8, 'Long unannounced power cuts', 'We face power cuts for 6 to 8 hours every day without any notice.', 'Electricity', 'orangi', 'Medium', 'Under Review', 'orangi_power', 6),
    (9, 'Broken benches in park', 'Many benches in the park are broken and unsafe for the elderly.', 'Parks', 'clifton', 'Low', 'Resolved', 'clifton_park', 12),
    (10, 'Children play area damaged', 'The swings and slides in the play area are rusted and damaged.', 'Parks', 'clifton', 'Medium', 'Closed', 'clifton_park', 14),
    (1, 'Open manhole near school', 'An open manhole without a cover is right next to the school gate and children walk past it.', 'Public Safety', 'malir', 'Critical', 'Assigned', 'malir_safety', 2),
    (2, 'No zebra crossing near school', 'There is no safe crossing near the school and cars drive very fast on this road.', 'Public Safety', 'malir', 'High', 'Under Review', 'malir_safety', 5),
    (3, 'Garbage dumped near hospital', 'Garbage is being dumped behind the hospital wall and may spread infection.', 'Garbage / Waste', 'pechs', 'High', 'Under Review', None, 4),
    (4, 'Pothole outside my house', 'A small pothole outside my house is getting bigger after every rain.', 'Roads', 'dha', 'Low', 'Submitted', None, 1),
    (5, 'Water tanker mafia overcharging', 'Tanker operators are charging double the official rate in our neighbourhood.', 'Water', 'dha', 'Medium', 'Under Review', None, 5),
    (6, 'Street light on all day', 'The street light near our house stays on during the day and wastes electricity.', 'Street Lights', 'pechs', 'Low', 'Resolved', None, 9),
    (7, 'Illegal electricity connections', 'Dangerous illegal hooks are hanging from the pole and could electrocute someone.', 'Electricity', 'pechs', 'High', 'In Progress', None, 3),
    (8, 'Overgrown park with snakes', 'The park is overgrown with tall grass and snakes were seen last week.', 'Parks', 'gulshan', 'Medium', 'Assigned', None, 7),
    (9, 'Suspicious gathering near ATM', 'A group gathers near the ATM every night and people feel unsafe.', 'Public Safety', 'clifton', 'Medium', 'Submitted', None, 2),
    (10, 'Broken footpath', 'The footpath is broken and wheelchair users cannot use it.', 'Public Spaces', 'saddar', 'Low', 'Closed', None, 15),
    (2, 'Gas pipeline smell on street', 'There is a strong gas smell near the junction and it may be a leaking pipeline.', 'Other', 'korangi', 'Critical', 'Under Review', None, 1),
    (4, 'Stray dogs attacking people', 'Stray dogs have attacked several people in our street this month.', 'Public Safety', 'nazimabad', 'High', 'Submitted', None, 2),
    (6, 'Drain cover stolen', 'The drain cover on our road was stolen and the open drain is dangerous at night.', 'Sewerage', 'malir', 'High', 'Reopened', None, 8),
    (8, 'Park lights not working', 'The park lights are off and people cannot walk in the evening.', 'Parks', 'dha', 'Low', 'Under Review', None, 4),
    (1, 'Noise from construction at night', 'Construction work continues all night and nobody can sleep.', 'Public Spaces', 'clifton', 'Low', 'Submitted', None, 1),
    (3, 'Electric pole leaning dangerously', 'An electric pole is leaning to one side after the storm and may fall on the road.', 'Electricity', 'lyari', 'Critical', 'Assigned', None, 2),
    (5, 'Garbage truck skipping our street', 'The garbage truck never enters our street and we have to carry waste far away.', 'Garbage / Waste', 'orangi', 'Medium', 'In Progress', None, 6),
    (7, 'Road repair left unfinished', 'The road was dug for repairs two weeks ago and was never refilled.', 'Roads', 'malir', 'Medium', 'Under Review', None, 10),
]


def _ts(days_ago, extra_hours=0):
    t = datetime.now(timezone.utc) - timedelta(days=days_ago) + timedelta(hours=extra_hours)
    return t.isoformat(timespec='seconds')


def _timeline(final_status):
    if final_status == 'Reopened':
        return ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Reopened']
    return STATUS_FLOW[:STATUS_FLOW.index(final_status) + 1]


def seed_extra_demo_data():
    pw_hash = hash_password(PASSWORD)
    with get_conn() as c:
        # departments
        for name, code, username in NEW_DEPARTMENTS:
            exists = c.execute(
                'SELECT 1 FROM departments WHERE department_code=? OR username=?', (code, username)
            ).fetchone()
            if not exists:
                c.execute(
                    'INSERT INTO departments(name,username,password_hash,department_code,active,created_at) '
                    'VALUES(?,?,?,?,1,?)',
                    (name, username, pw_hash, code, _ts(30)),
                )
        depts = {r['name']: r['id'] for r in c.execute('SELECT id,name FROM departments')}

        # citizens
        citizen_ids = {}
        for i in range(1, NUM_CITIZENS + 1):
            username = f'demo{i}'
            row = c.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
            if not row:
                cur = c.execute(
                    'INSERT INTO users(username,password_hash,role,full_name,language,created_at) '
                    'VALUES(?,?,?,?,?,?)',
                    (username, pw_hash, 'citizen', CITIZEN_NAMES[(i - 1) % len(CITIZEN_NAMES)],
                     'English', _ts(30)),
                )
                citizen_ids[i] = cur.lastrowid
            else:
                citizen_ids[i] = row['id']

        # community cases
        case_ids = {}
        for key, (title, cat, area_key, prio, status, desc) in COMMUNITY_CASES.items():
            row = c.execute('SELECT id FROM community_cases WHERE title=?', (title,)).fetchone()
            if row:
                case_ids[key] = row['id']
                continue
            area, lat, lon = AREAS[area_key]
            cur = c.execute(
                '''INSERT INTO community_cases(title,category,description,complaint_count,latitude,longitude,
                   area_name,priority,status,routed_department_id,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (title, cat, desc, 0, lat, lon, area, prio, status,
                 depts.get(CATEGORY_DEPT.get(cat)), _ts(10), _ts(1)),
            )
            case_ids[key] = cur.lastrowid

        # complaints + timelines
        for n, (cnum, title, desc, cat, area_key, prio, status, case_key, days) in enumerate(COMPLAINTS):
            cid_citizen = citizen_ids[cnum]
            if c.execute('SELECT 1 FROM complaints WHERE citizen_id=? AND title=?',
                         (cid_citizen, title)).fetchone():
                continue
            area, lat, lon = AREAS[area_key]
            lat += ((n % 5) - 2) * 0.0012
            lon += (((n * 3) % 5) - 2) * 0.0012
            lo, hi = IMPACT_RANGE[prio]
            impact = lo + (n * 7) % (hi - lo + 1)
            dept_id = depts.get(CATEGORY_DEPT.get(cat))
            cur = c.execute(
                '''INSERT INTO complaints(
                    citizen_id,title,description,language,category,latitude,longitude,address,
                    ai_summary,ai_priority,impact_score,community_case_id,routed_department_id,
                    status,citizen_confirmed,government_submitted,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (cid_citizen, title, desc, 'English', cat, lat, lon, area, desc, prio, impact,
                 case_ids.get(case_key), dept_id, status, 1, 1, _ts(days), _ts(max(days - 2, 0))),
            )
            comp_id = cur.lastrowid
            for step, st_name in enumerate(_timeline(status)):
                c.execute(
                    'INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',
                    (comp_id, dept_id, st_name, STATUS_NOTES[st_name], _ts(days, extra_hours=step * 6)),
                )

        # keep community complaint_count in sync
        for key, cid in case_ids.items():
            c.execute(
                'UPDATE community_cases SET complaint_count='
                '(SELECT COUNT(*) FROM complaints WHERE community_case_id=?) WHERE id=?',
                (cid, cid),
            )
        c.commit()

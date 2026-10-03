import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import bcrypt
from config import DB_PATH

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def get_conn():
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA busy_timeout=15000')
    return c

def init_db():
    with get_conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            role TEXT NOT NULL, full_name TEXT, email TEXT, phone TEXT,
            language TEXT DEFAULT 'English', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS departments(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, department_code TEXT UNIQUE NOT NULL,
            active INTEGER DEFAULT 1, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS complaints(
            id INTEGER PRIMARY KEY, citizen_id INTEGER NOT NULL, title TEXT,
            description TEXT NOT NULL, language TEXT, category TEXT, subcategory TEXT,
            latitude REAL, longitude REAL, address TEXT, evidence_type TEXT, evidence_path TEXT,
            ai_summary TEXT, ai_priority TEXT, impact_score INTEGER, duplicate_of INTEGER,
            community_case_id INTEGER, routed_department_id INTEGER,
            status TEXT DEFAULT 'Submitted', citizen_confirmed INTEGER DEFAULT 0,
            government_submitted INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(citizen_id) REFERENCES users(id),
            FOREIGN KEY(routed_department_id) REFERENCES departments(id)
        );
        CREATE TABLE IF NOT EXISTS community_cases(
            id INTEGER PRIMARY KEY, title TEXT, category TEXT, description TEXT,
            complaint_count INTEGER DEFAULT 0, latitude REAL, longitude REAL, area_name TEXT,
            priority TEXT, status TEXT DEFAULT 'Submitted', routed_department_id INTEGER,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(routed_department_id) REFERENCES departments(id)
        );
        CREATE TABLE IF NOT EXISTS case_updates(
            id INTEGER PRIMARY KEY, complaint_id INTEGER NOT NULL, department_id INTEGER,
            status TEXT, note TEXT, created_at TEXT NOT NULL,
            FOREIGN KEY(complaint_id) REFERENCES complaints(id),
            FOREIGN KEY(department_id) REFERENCES departments(id)
        );
        CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT, message TEXT,
            read INTEGER DEFAULT 0, created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_complaints_citizen ON complaints(citizen_id);
        CREATE INDEX IF NOT EXISTS idx_complaints_department ON complaints(routed_department_id);
        CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
        CREATE INDEX IF NOT EXISTS idx_updates_complaint ON case_updates(complaint_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id,read);
        ''')
        c.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def seed_demo_data():
    with get_conn() as c:
        if not c.execute('SELECT 1 FROM users WHERE username=?', ('admin',)).fetchone():
            c.execute(
                'INSERT INTO users(username,password_hash,role,full_name,language,created_at) VALUES(?,?,?,?,?,?)',
                ('admin', hash_password('admin'), 'admin', 'MAHALA Administrator', 'English', now())
            )
        defaults = [
            ('Municipal Services','MUNI','municipal'),
            ('Water & Sewerage','WATER','water'),
            ('Waste Management','WASTE','waste'),
            ('Roads & Infrastructure','ROADS','roads'),
        ]
        for name, code, username in defaults:
            if not c.execute('SELECT 1 FROM departments WHERE department_code=?', (code,)).fetchone():
                c.execute(
                    'INSERT INTO departments(name,username,password_hash,department_code,active,created_at) VALUES(?,?,?,?,1,?)',
                    (name, username, hash_password('demo123'), code, now())
                )
        if not c.execute('SELECT 1 FROM users WHERE username=?', ('demo',)).fetchone():
            c.execute(
                'INSERT INTO users(username,password_hash,role,full_name,language,created_at) VALUES(?,?,?,?,?,?)',
                ('demo', hash_password('demo123'), 'citizen', 'Demo Citizen', 'English', now())
            )
        citizen = c.execute('SELECT id FROM users WHERE username=?', ('demo',)).fetchone()['id']
        if not c.execute('SELECT 1 FROM complaints').fetchone():
            depts = {r['name']: r['id'] for r in c.execute('SELECT id,name FROM departments')}
            samples = [
                ('Garbage collection problem','Garbage has not been collected for several days near the main street.','Garbage / Waste',24.9056,67.0822,'Gulshan area',depts.get('Waste Management')),
                ('Broken road','A large pothole is making the road difficult for vehicles and pedestrians.','Roads',24.8607,67.0011,'Saddar area',depts.get('Roads & Infrastructure')),
                ('Water leakage','A water pipe is leaking continuously beside the residential lane.','Water',24.9200,67.0800,'Gulshan area',depts.get('Water & Sewerage')),
                ('Street light problem','Two street lights are not working after sunset.','Street Lights',24.8900,67.0500,'PECHS area',depts.get('Municipal Services')),
            ]
            for title, desc, cat, lat, lon, area, did in samples:
                c.execute(
                    '''INSERT INTO complaints(
                        citizen_id,title,description,language,category,latitude,longitude,address,
                        ai_summary,ai_priority,impact_score,routed_department_id,status,
                        citizen_confirmed,government_submitted,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (citizen,title,desc,'English',cat,lat,lon,area,desc,'Medium',55,did,
                     'Submitted',1,1,now(),now())
                )
        # Ensure every seeded complaint has a timeline entry.
        for row in c.execute('SELECT id,routed_department_id,status FROM complaints WHERE citizen_id=?', (citizen,)).fetchall():
            if not c.execute('SELECT 1 FROM case_updates WHERE complaint_id=?', (row['id'],)).fetchone():
                c.execute(
                    'INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',
                    (row['id'], row['routed_department_id'], row['status'], 'Demo complaint seeded for the hackathon.', now())
                )
        c.commit()
    try:
        from demo_seed import seed_extra_demo_data
        seed_extra_demo_data()
    except Exception as exc:
        print('Extra demo data skipped:', exc)

def query(sql, args=()):
    with get_conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]

def one(sql, args=()):
    with get_conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None

def execute(sql, args=()):
    with get_conn() as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid

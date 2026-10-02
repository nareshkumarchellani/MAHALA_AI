import streamlit as st
from database import query, execute, one, hash_password, now
from services.analytics_service import overview
from pages.map import render as map_render

def render(user, page):
    if page == 'Overview': overview_page()
    elif page == 'Departments': departments()
    elif page == 'Complaints': complaints()
    elif page == 'Community Cases': community_cases()
    elif page == 'Users': users()
    elif page == 'Map': map_render()
    elif page == 'Analytics': analytics()
    else: settings()

def overview_page():
    st.title('Admin Overview')
    metrics = [
        ('Complaints', query('SELECT COUNT(*) n FROM complaints')[0]['n']),
        ('Users', query('SELECT COUNT(*) n FROM users')[0]['n']),
        ('Active Departments', query('SELECT COUNT(*) n FROM departments WHERE active=1')[0]['n']),
        ('Community Cases', query('SELECT COUNT(*) n FROM community_cases')[0]['n']),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)
    st.subheader('Recent activity')
    rows = query('''SELECT c.id,c.title,c.status,c.ai_priority,d.name department,c.updated_at
                    FROM complaints c LEFT JOIN departments d ON d.id=c.routed_department_id
                    ORDER BY c.updated_at DESC LIMIT 10''')
    st.dataframe(rows, use_container_width=True, hide_index=True)

def departments():
    st.title('Departments')
    with st.expander('Create Department', expanded=True):
        name = st.text_input('Department Name')
        code = st.text_input('Department Code')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Create Department', type='primary'):
            if not all([name.strip(), code.strip(), username.strip(), password]):
                st.error('All fields are required.')
            elif len(password) < 6:
                st.error('Password must be at least 6 characters.')
            else:
                try:
                    execute(
                        'INSERT INTO departments(name,username,password_hash,department_code,active,created_at) VALUES(?,?,?,?,1,?)',
                        (name.strip(), username.strip(), hash_password(password), code.strip().upper(), now())
                    )
                    st.success('Department created.')
                    st.rerun()
                except Exception:
                    st.error('Could not create department. Check unique name, code, and username.')
    st.dataframe(
        query('SELECT id,name,username,department_code,active,created_at FROM departments ORDER BY id'),
        use_container_width=True, hide_index=True
    )

def complaints():
    st.title('All Complaints')
    rows = query('''SELECT c.*,d.name department,u.full_name citizen
                    FROM complaints c
                    LEFT JOIN departments d ON d.id=c.routed_department_id
                    LEFT JOIN users u ON u.id=c.citizen_id
                    ORDER BY c.id DESC''')
    st.dataframe([
        {k: r[k] for k in ['id','title','category','ai_priority','status','citizen_confirmed',
                           'government_submitted','department','citizen','created_at']}
        for r in rows
    ], use_container_width=True, hide_index=True)

    st.subheader('Manage a complaint')
    ids = [r['id'] for r in rows]
    if not ids:
        st.info('No complaints.')
        return
    cid = st.selectbox('Complaint', ids)
    c = next(r for r in rows if r['id'] == cid)
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox('Status',
                              ['Submitted','Under Review','Assigned','In Progress','Resolved','Closed','Reopened'],
                              index=max(0, ['Submitted','Under Review','Assigned','In Progress','Resolved','Closed','Reopened'].index(c['status']) if c['status'] in ['Submitted','Under Review','Assigned','In Progress','Resolved','Closed','Reopened'] else 0))
    with col2:
        active = query('SELECT id,name FROM departments WHERE active=1 ORDER BY name')
        labels = {d['id']: d['name'] for d in active}
        options = [None] + list(labels)
        current = c['routed_department_id'] if c['routed_department_id'] in labels else None
        dept_id = st.selectbox('Department', options, index=options.index(current), format_func=lambda x: 'Unassigned' if x is None else labels[x])
    note = st.text_input('Admin note')
    if st.button('Save complaint update', type='primary'):
        execute('UPDATE complaints SET status=?,routed_department_id=?,updated_at=? WHERE id=?',
                (status, dept_id, now(), cid))
        execute('INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',
                (cid, dept_id, status, note or 'Admin updated the complaint.', now()))
        st.success('Complaint updated.')
        st.rerun()

def community_cases():
    st.title('Community Cases')
    rows = query('''SELECT cc.*,d.name department FROM community_cases cc
                    LEFT JOIN departments d ON d.id=cc.routed_department_id
                    ORDER BY cc.complaint_count DESC,cc.id DESC''')
    st.dataframe(rows, use_container_width=True, hide_index=True)

def users():
    st.title('Users')
    st.dataframe(query('SELECT id,username,role,full_name,language,created_at FROM users ORDER BY id DESC'),
                 use_container_width=True, hide_index=True)

def analytics():
    st.title('Analytics')
    a = overview()
    st.subheader('By category'); st.dataframe(a['categories'], hide_index=True, use_container_width=True)
    st.subheader('By status'); st.dataframe(a['statuses'], hide_index=True, use_container_width=True)
    st.subheader('By priority'); st.dataframe(a['priorities'], hide_index=True, use_container_width=True)

def settings():
    st.title('Settings')
    st.info('Demo mode is enabled. API credentials are read from Streamlit Secrets. Change demo credentials before production use.')
    st.code('Admin demo: admin / admin\nCitizen demo: demo / demo123\nDepartments: municipal, water, waste, roads / demo123')

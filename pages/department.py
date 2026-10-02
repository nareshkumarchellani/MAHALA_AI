import streamlit as st
from database import query,one,execute,now
from pages.map import render as map_render
from services.notification_service import notify

def render(user,page):
    did=user['department_id']
    if page=='Dashboard': dashboard(did)
    elif page=='Assigned Complaints': assigned(did)
    elif page=='Community Cases': community(did)
    elif page=='Map': map_render()
    else: profile(user)

def base(did): return query('''SELECT c.*,d.name department,u.full_name citizen FROM complaints c LEFT JOIN departments d ON d.id=c.routed_department_id LEFT JOIN users u ON u.id=c.citizen_id WHERE c.routed_department_id=? ORDER BY c.id DESC''',(did,))
def dashboard(did):
    st.title('Department Dashboard'); cs=base(did); vals=[len(cs),sum(x['status']=='In Progress' for x in cs),sum(x['status'] in ['Resolved','Closed'] for x in cs),sum(x['ai_priority'] in ['High','Critical'] for x in cs)]; cols=st.columns(4)
    for col,label,val in zip(cols,['New Cases','In Progress','Resolved','High Priority'],vals): col.metric(label,val)
    st.dataframe([{'ID':x['id'],'Title':x['title'],'Priority':x['ai_priority'],'Status':x['status'],'Citizen':x['citizen']} for x in cs],use_container_width=True,hide_index=True)
def assigned(did):
    st.title('Assigned Complaints')
    for c in base(did):
        with st.container(border=True):
            st.subheader(f"#{c['id']} · {c['title']}"); st.write(c['ai_summary'] or c['description']); st.write(f"Priority: {c['ai_priority']} · Impact: {c['impact_score']} · Status: {c['status']}"); st.write(f"Location: {c['address'] or 'Not supplied'}")
            status_options=['Under Review','Assigned','In Progress','Resolved','Closed','Reopened']
            new=st.selectbox('Update status',status_options,index=status_options.index(c['status']) if c['status'] in status_options else 0,key=f's{c["id"]}')
            note=st.text_input('Note',key=f'n{c["id"]}')
            if st.button('Apply Update',key=f'u{c["id"]}',type='primary'):
                execute('UPDATE complaints SET status=?,updated_at=? WHERE id=? AND routed_department_id=?',(new,now(),c['id'],did)); execute('INSERT INTO case_updates(complaint_id,department_id,status,note,created_at) VALUES(?,?,?,?,?)',(c['id'],did,new,note,now())); notify(c['citizen_id'],'Complaint status updated',f'Complaint #{c["id"]} is now {new}.'); st.success('Updated.'); st.rerun()
def community(did):
    st.title('Assigned Community Cases'); rows=query('SELECT * FROM community_cases WHERE routed_department_id=? ORDER BY complaint_count DESC',(did,))
    st.dataframe(rows,use_container_width=True,hide_index=True)
    if rows:
        case_id=st.selectbox('Community case', [r['id'] for r in rows])
        status=st.selectbox('Community case status',['Submitted','Under Review','In Progress','Resolved','Closed','Reopened'])
        if st.button('Update community case',type='primary'):
            execute('UPDATE community_cases SET status=?,updated_at=? WHERE id=? AND routed_department_id=?',(status,now(),case_id,did))
            st.success('Community case updated.')
            st.rerun()
def profile(user): st.title('Profile'); st.write(user.get('full_name','')); st.write('Department access is restricted to assigned cases.')

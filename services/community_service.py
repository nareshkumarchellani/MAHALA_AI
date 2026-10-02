from database import query,one

def cases(): return query('''SELECT cc.*,d.name department FROM community_cases cc LEFT JOIN departments d ON d.id=cc.routed_department_id ORDER BY cc.complaint_count DESC,cc.id DESC''')
def case_detail(cid): return one('SELECT * FROM community_cases WHERE id=?',(cid,))

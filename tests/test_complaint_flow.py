from services.complaint_service import analyze_and_create, get_one, confirm_submit, history

def test_end_to_end_complaint_flow():
    from database import one
    citizen = one('SELECT id FROM users WHERE username=?', ('demo',))
    result = analyze_and_create(
        citizen['id'],
        'A large amount of garbage is blocking the road near our market.',
        'English',
        'Garbage / Waste',
        24.905,
        67.081,
        'Test Market',
    )
    cid = result['complaint_id']
    c = get_one(cid, citizen['id'])
    assert c and c['citizen_confirmed'] == 0 and c['government_submitted'] == 0
    ok, msg = confirm_submit(cid, citizen['id'])
    assert ok
    c = get_one(cid, citizen['id'])
    assert c['citizen_confirmed'] == 1 and c['government_submitted'] == 1
    assert c['status'] == 'Under Review'
    assert any(h['status'] == 'Under Review' for h in history(cid))

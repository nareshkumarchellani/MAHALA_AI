from database import query, one

def test_schema_and_seed():
    tables = {r['name'] for r in query('SELECT name FROM sqlite_master WHERE type="table"')}
    assert {'users','departments','complaints','community_cases','case_updates','notifications'} <= tables
    assert one('SELECT * FROM users WHERE username=?', ('admin',))
    assert query('SELECT * FROM departments')
    assert query('SELECT * FROM complaints')
    assert query('SELECT * FROM case_updates')

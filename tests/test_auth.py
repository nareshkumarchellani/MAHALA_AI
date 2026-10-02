from database import hash_password, check_password
from auth import login, register

def test_password_hash():
    h = hash_password('secret')
    assert h != 'secret'
    assert check_password('secret', h)
    assert not check_password('wrong', h)

def test_admin_login():
    u = login('admin', 'admin')
    assert u and u['role'] == 'admin'

def test_department_login():
    u = login('water', 'demo123')
    assert u and u['role'] == 'department'
    assert u['department_id']

def test_register():
    ok, msg = register('testuser_xyz', 'secret1', 'secret1', 'Test User')
    assert ok, msg
    assert login('testuser_xyz', 'secret1')['role'] == 'citizen'

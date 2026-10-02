import streamlit as st
from database import one, execute, hash_password, check_password, now

def login(username,password):
    u=one('SELECT * FROM users WHERE username=?',(username,))
    if u and check_password(password,u['password_hash']): return u
    d=one('SELECT * FROM departments WHERE username=? AND active=1',(username,))
    if d and check_password(password,d['password_hash']): return {'id':d['id'],'username':d['username'],'role':'department','full_name':d['name'],'department_id':d['id'],'language':'English'}
    return None

def register(username,password,confirm,full_name,language='English'):
    if not username.strip() or not full_name.strip(): return False,'Username and full name are required.'
    if len(password)<6: return False,'Password must be at least 6 characters.'
    if password!=confirm: return False,'Passwords do not match.'
    if one('SELECT id FROM users WHERE username=?',(username.strip(),)): return False,'Username already exists.'
    execute('INSERT INTO users(username,password_hash,role,full_name,language,created_at) VALUES(?,?,?,?,?,?)',(username.strip(),hash_password(password),'citizen',full_name.strip(),language,now()))
    return True,'Account created. You can now sign in.'

def logout():
    for k in ['user','page','pending_analysis']: st.session_state.pop(k,None)
    st.rerun()

import streamlit as st
from config import APP_NAME
from database import init_db,seed_demo_data
from auth import login,register,logout
from services.notification_service import unread
from pages import citizen,admin,department

st.set_page_config(page_title=APP_NAME,page_icon='🏙️',layout='wide',initial_sidebar_state='expanded')

def css():
    st.markdown('''
    <style>

    /* ===== REMOVE STREAMLIT DEFAULT TOP BAR ===== */

   header[data-testid="stHeader"] {
    background: transparent !important;
    height: 2.75rem !important;
    min-height: 2.75rem !important;
}

/* Keep Streamlit sidebar toggle visible */
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

    div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    div[data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    footer {
        display: none !important;
        visibility: hidden !important;
    }

    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* ===== MAHALA AI DESIGN ===== */

    .stApp {
        background: radial-gradient(
            circle at 15% 0%,
            #123b5c 0%,
            #07121f 38%,
            #050b14 100%
        );
        color: #eef6ff;
    }

    [data-testid="stSidebar"] {
        background: rgba(5,16,29,.94);
        border-right: 1px solid rgba(120,220,255,.12);
    }

    .hero {
        padding: 44px 10px 25px;
    }

    .hero h1 {
        font-size: 4.4rem;
        line-height: 1;
        margin: 0;
        background: linear-gradient(90deg,#fff,#7de7ff);
        -webkit-background-clip: text;
        color: transparent;
    }

    .hero p {
        font-size: 1.15rem;
        color: #a9c1d2;
    }

    .pill {
        display: inline-block;
        padding: 7px 12px;
        border: 1px solid rgba(105,225,255,.25);
        border-radius: 999px;
        color: #8feaff;
        background: rgba(60,190,230,.08);
        font-size: .78rem;
    }

    .card {
        padding: 24px;
        border: 1px solid rgba(130,220,255,.14);
        border-radius: 22px;
        background: linear-gradient(
            145deg,
            rgba(18,42,64,.82),
            rgba(8,22,36,.72)
        );
        box-shadow: 0 16px 45px rgba(0,0,0,.22);
        height: 100%;
    }

    .card h3 {
        margin: .35rem 0;
    }

    .muted {
        color: #9eb5c6;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(120,220,255,.2);
        min-height: 42px;
    }

    .stTextInput > div > div,
    .stTextArea textarea,
    .stSelectbox > div > div {
        border-radius: 12px;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem;
    }

    .metric-card {
        padding: 15px;
        border-radius: 16px;
        background: rgba(20,50,72,.55);
    }

    </style>
    ''', unsafe_allow_html=True)

def translations(lang):
    return {'English':{'login':'LOGIN','register':'REGISTER','signin':'🚀 Sign In','create':'✨ Create Account','username':'Username','password':'Password','full':'Full Name'},'Urdu':{'login':'لاگ اِن','register':'رجسٹر','signin':'🚀 سائن اِن','create':'✨ اکاؤنٹ بنائیں','username':'صارف نام','password':'پاس ورڈ','full':'پورا نام'}}[lang]

def landing():
    if 'language' not in st.session_state: st.session_state.language='English'
    with st.sidebar:
        st.session_state.language=st.selectbox('Language',['English','Urdu'],index=['English','Urdu'].index(st.session_state.language))
    t=translations(st.session_state.language)
    st.markdown('<div class="hero"><span class="pill">🇵🇰 CIVIC INTELLIGENCE PLATFORM</span><h1>MAHALA AI</h1><p>AI-Powered Civic Complaint & Community Intelligence Platform</p><h2>Turn Civic Problems Into Real Action.</h2><p>Report problems. Let AI understand them. Get them to the right department.</p></div>',unsafe_allow_html=True)
    cols=st.columns(4)
    cards=[('🤖','01','AI Civic Intelligence','AI understands complaints, detects patterns, identifies duplicates and intelligently routes cases.','✦ 7 AI AGENTS'),('🎙️','02','Voice First','Citizens can speak naturally. AI converts voice into a structured civic complaint.','✦ VOICE + TEXT'),('📍','03','Smart Civic Map','Visualize complaint hotspots, community problems and high-impact civic areas.','✦ CIVIC INTELLIGENCE'),('🏢','04','Department Routing','Verified complaints are intelligently routed to the responsible government department.','✦ SMART ROUTING')]
    for col,(icon,num,title,desc,tag) in zip(cols,cards):
        with col: st.markdown(f'<div class="card"><div style="font-size:2rem">{icon}</div><span class="pill">{num}</span><h3>{title}</h3><p class="muted">{desc}</p><span class="pill">{tag}</span></div>',unsafe_allow_html=True)
    st.divider(); a,b=st.columns(2)
    with a:
        with st.container(border=True):
            st.subheader(t['login']); u=st.text_input(t['username'],key='lu'); p=st.text_input(t['password'],type='password',key='lp')
            if st.button(t['signin'],use_container_width=True,type='primary'):
                user=login(u,p)
                if user: st.session_state.user=user; st.rerun()
                else: st.error('Invalid username or password.')
    with b:
        with st.container(border=True):
            st.subheader(t['register']); u=st.text_input(t['username'],key='ru'); p=st.text_input(t['password'],type='password',key='rp'); cp=st.text_input('Confirm Password',type='password',key='rcp'); name=st.text_input(t['full'],key='rn')
            if st.button(t['create'],use_container_width=True):
                ok,msg=register(u,p,cp,name,st.session_state.language); st.success(msg) if ok else st.error(msg)
    st.caption('Hackathon demo: admin / admin. Production deployments must change the admin password.')

def sidebar_for(role):
    if role=='citizen':
        pages=['Dashboard','New Complaint','My Complaints','Community Issues','Map','AI Assistant','Profile',f'Notifications ({unread(st.session_state.user["id"])})']
    elif role=='admin': pages=['Overview','Departments','Complaints','Community Cases','Users','Map','Analytics','Settings']
    else: pages=['Dashboard','Assigned Complaints','Community Cases','Map','Profile']
    with st.sidebar:
        st.markdown('## 🏙️ MAHALA AI'); st.caption(f"{st.session_state.user.get('full_name','')} · {role.title()}")
        choice=st.radio('Navigate',pages)
        if st.button('Logout',use_container_width=True): logout()
    return choice

def main():
    init_db(); seed_demo_data(); css()
    if 'user' not in st.session_state: landing(); return
    user=st.session_state.user; page=sidebar_for(user['role']); clean=page.split(' (')[0]
    try:
        if user['role']=='citizen': citizen.render(user,clean)
        elif user['role']=='admin': admin.render(user,clean)
        else: department.render(user,clean)
    except Exception as exc:
        st.error('Something went wrong while loading this section. Please try again.')
        with st.expander('Technical details (demo mode)'):
            st.exception(exc)

if __name__=='__main__': main()

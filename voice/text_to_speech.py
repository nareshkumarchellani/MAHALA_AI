import streamlit as st

def speak(text,language='English'):
    lang='ur-PK' if language=='Urdu' else 'en-US'
    safe=text.replace('`','').replace('\\',' ')
    st.components.v1.html(f'''<script>window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance({safe!r});u.lang={lang!r};window.speechSynthesis.speak(u);</script>''',height=0)

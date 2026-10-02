
import streamlit as st
from groq_client import ask_text, available
from database import query
from voice.text_to_speech import speak
from voice.speech_to_text import transcribe


def _answer(user, q):
    st.session_state.assistant_messages.append({
        'role': 'user',
        'content': q
    })

    complaints = (
        query(
            'SELECT id,title,status,category,ai_summary '
            'FROM complaints '
            'WHERE citizen_id=? '
            'ORDER BY id DESC LIMIT 10',
            (user['id'],)
        )
        if user['role'] == 'citizen'
        else []
    )

    context = '\n'.join(str(x) for x in complaints)

    ans = ask_text(
        'You are MAHALA AI civic assistant. Support English and Urdu. '
        'Do not claim to be a government official. '
        'Answer only from user context and general writing guidance. '
        'Do not invent complaint status, department actions, laws, '
        'contacts, or guarantees.',
        f'User question: {q}\nUser complaint context: {context}',
        'I can help you write or understand a civic complaint. '
        'Please provide the complaint details or complaint ID.'
    )

    st.session_state.assistant_messages.append({
        'role': 'assistant',
        'content': ans
    })


def render(user):
    st.title('🤖 AI Civic Assistant')
    st.caption(
        'Ask MAHALA AI about complaints, civic services, '
        'status, routing, or how to write a report.'
    )

    if 'assistant_messages' not in st.session_state:
        st.session_state.assistant_messages = []

    # Conversation
    for msg in st.session_state.assistant_messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

    st.divider()

    # Voice assistant
    st.markdown('### 🎙️ Talk to MAHALA AI')

    audio = st.audio_input(
        '🎤 Speak your question',
        sample_rate=16000,
        key='assistant_voice_input'
    )

    if audio:
        import hashlib

        audio_hash = hashlib.sha256(audio.getvalue()).hexdigest()

        if st.session_state.get('assistant_audio_hash') != audio_hash:
            st.session_state.assistant_audio_hash = audio_hash

            with st.spinner('🎙️ Converting voice to text...'):
                q_voice, msg = transcribe(audio)

            if q_voice and q_voice.strip():
                st.session_state.assistant_voice_text = q_voice.strip()
                st.success('✅ Voice converted to text.')
            else:
                st.warning(
                    msg or 'Could not understand the recording.'
                )

    # Editable voice transcription
    voice_text = st.text_area(
        'Voice transcription',
        value=st.session_state.get('assistant_voice_text', ''),
        key='assistant_voice_text_box',
        height=90,
        placeholder='Your spoken question will appear here...'
    )

    voice_send = st.button(
        '🚀 Ask using voice',
        use_container_width=True,
        disabled=not voice_text.strip()
    )

    if voice_send:
        _answer(user, voice_text.strip())
        st.session_state.assistant_voice_text = ''
        st.rerun()

    st.divider()

    # Normal text chat remains available
    q = st.chat_input(
        'Or type: Ask about a complaint, status, routing...'
    )

    if q:
        _answer(user, q)
        st.rerun()

    if st.session_state.assistant_messages:
        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                '🔊 Read latest answer aloud',
                use_container_width=True
            ):
                latest = next(
                    (
                        m['content']
                        for m in reversed(
                            st.session_state.assistant_messages
                        )
                        if m['role'] == 'assistant'
                    ),
                    ''
                )

                if latest:
                    speak(
                        latest,
                        user.get('language', 'English')
                    )

        with c2:
            if st.button(
                '🗑️ Clear conversation',
                use_container_width=True
            ):
                st.session_state.assistant_messages = []
                st.session_state.assistant_voice_text = ''
                st.rerun()

    if not available():
        st.caption(
            'AI API is not configured; the assistant uses a safe fallback response.'
        )

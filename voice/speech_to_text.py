
import os
import tempfile

import streamlit as st


def _get_groq_key():
    """
    Always read the key from Streamlit Secrets first.
    Fall back to config.py and environment variables.
    """
    # 1. Streamlit Secrets
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass

    # 2. Project config
    try:
        from config import GROQ_API_KEY
        if GROQ_API_KEY:
            return str(GROQ_API_KEY).strip()
    except Exception:
        pass

    # 3. Environment fallback
    return os.getenv("GROQ_API_KEY", "").strip()



def convert_to_roman_urdu(text):
    """
    Convert Hindi/Devanagari transcription into Roman Urdu/English.
    Keeps the citizen's meaning instead of displaying Hindi script.
    """
    if not text or not text.strip():
        return text

    api_key = _get_groq_key()

    if not api_key:
        return text

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a civic complaint transcription normalizer. "
                        "Convert Hindi/Devanagari speech transcription into "
                        "natural Roman Urdu or simple Roman English. "
                        "Do NOT output Devanagari/Hindi script. "
                        "Preserve the exact meaning. "
                        "Do not add facts. "
                        "Do not summarize. "
                        "If the sentence is already English or Roman Urdu, "
                        "keep it essentially unchanged. "
                        "Output ONLY the converted complaint text."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        result = response.choices[0].message.content.strip()

        return result or text

    except Exception:
        # Never destroy a successful transcription if normalization fails.
        return text

def transcribe(audio_file):
    """
    Convert an uploaded Streamlit audio file to text using Groq Whisper.

    Returns:
        (text, message)
    """

    api_key = _get_groq_key()

    if not api_key:
        return (
            "",
            "Voice transcription is unavailable without GROQ_API_KEY."
        )

    if audio_file is None:
        return "", "No audio recording was provided."

    try:
        from groq import Groq
    except Exception as e:
        return "", f"Groq package is unavailable: {e}"

    try:
        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return "", "The recording is empty. Please record again."

        # Streamlit audio_input normally provides WAV audio.
        suffix = ".wav"

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        ) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            client = Groq(api_key=api_key)

            with open(tmp_path, "rb") as audio:
                result = client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-large-v3-turbo",
                    response_format="json"
                )

            text = getattr(result, "text", "") or ""

            text = str(text).strip()

            if not text:
                return (
                    "",
                    "Audio was received, but no speech could be detected."
                )

            return convert_to_roman_urdu(text), "Voice transcription successful."

        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    except Exception as e:
        return "", f"Voice transcription failed: {e}"

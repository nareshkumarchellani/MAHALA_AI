import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'mahala.db'
UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _secret(name: str, default: str = '') -> str:
    """Read configuration from Streamlit Secrets only, with a safe empty fallback."""
    try:
        import streamlit as st
        value = st.secrets.get(name, default)
        return str(value) if value is not None else default
    except Exception:
        return default


# API credentials are intentionally read from Streamlit Secrets only.
# No API key is read from .env or hardcoded in source code.
GROQ_API_KEY = _secret('GROQ_API_KEY')
GOOGLE_MAPS_API_KEY = _secret('GOOGLE_MAPS_API_KEY')
AZURE_SPEECH_KEY = _secret('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = _secret('AZURE_SPEECH_REGION')

APP_NAME = 'MAHALA AI'
STATUSES = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Closed', 'Reopened']
CATEGORIES = ['Garbage / Waste', 'Roads', 'Water', 'Sewerage', 'Street Lights', 'Electricity', 'Parks', 'Public Spaces', 'Public Safety', 'Other']
DEPARTMENTS = ['Municipal Services', 'Water & Sewerage', 'Waste Management', 'Roads & Infrastructure', 'Electricity', 'Parks & Public Spaces', 'Public Safety', 'Other']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

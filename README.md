# MAHALA AI

**AI-Powered Civic Complaint & Community Intelligence Platform**

> Turn Civic Problems Into Real Action.

MAHALA AI is a Pakistan-focused hackathon-ready civic complaint platform. Citizens can submit text or voice complaints in English or Urdu. The system structures the report, checks for related complaints, groups community issues, estimates priority and impact, routes cases to departments, and requires citizen confirmation before government submission.

## Features
- English and Urdu UI only
- Citizen, Admin, and Department roles
- bcrypt password hashing and role-based access
- Seven AI agents: Intake, Understanding, Duplicate Detection, Community Clustering, Evidence & Location, Priority & Impact, Department Routing
- Groq LLM + Whisper integration with safe demo fallbacks
- Photo/video/audio upload validation
- SQLite community cases and status timelines
- Civic issue hotspot map using Folium/OpenStreetMap fallback
- In-app notifications
- AI citizen assistant
- Admin department creation and analytics
- Department-only access to assigned complaints
- No real API keys in source

## Architecture
`app.py` initializes the database, session state, authentication and role routing. Business logic is separated into `services/`; AI logic is in `agents/`; voice adapters are in `voice/`; role views are in `pages/`. SQLite stores users, departments, complaints, community cases, updates and notifications.

## Google Colab setup
```bash
unzip MAHALA_AI.zip
cd MAHALA_AI
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
For Colab, expose port 8501 with your preferred tunnel, for example ngrok. Install/authenticate ngrok according to its current documentation, then run the tunnel against `localhost:8501`.

The first application startup automatically creates and seeds the SQLite database.

## API keys
### Streamlit Secrets

The application reads API credentials **only from Streamlit Secrets**. Do not put real keys in `.env`, source code, or the ZIP.

For local/Colab Streamlit runs, create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_key"
GOOGLE_MAPS_API_KEY = "your_google_maps_key"
AZURE_SPEECH_KEY = ""
AZURE_SPEECH_REGION = ""
```

- `GROQ_API_KEY`: enables LLM complaint analysis and Whisper transcription.
- `GOOGLE_MAPS_API_KEY`: enables the optional Google Maps frontend. Folium/OpenStreetMap remains available without it.
- `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`: optional TTS provider configuration.

For Streamlit Community Cloud, add the same values under the app's **Settings → Secrets**. The real `secrets.toml` file is ignored by Git and is not included in the ZIP.

## Demo login
- Admin: `admin` / `admin`
- Demo citizen: `demo` / `demo123`
- Demo departments use usernames `municipal`, `water`, `waste`, `roads` with password `demo123`.

The admin credentials are intentionally simple for a hackathon demo. **Change the admin password before production deployment.**

## Local setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## GitHub deployment
Push the project without `.env`, `mahala.db`, uploads, or secrets. Configure API keys through the deployment platform's secret/environment system.

## Streamlit Community Cloud
Create a new app pointing to `app.py`, then add `GROQ_API_KEY`, `GOOGLE_MAPS_API_KEY`, and optional Azure values as secrets. SQLite is suitable for a hackathon demo, not durable multi-instance production storage.

## Troubleshooting
- **Groq unavailable:** the app remains in demo mode and shows a friendly fallback.
- **Voice unavailable:** use text mode or configure `GROQ_API_KEY`.
- **Map API unavailable:** Folium/OpenStreetMap remains available.
- **Upload rejected:** only common image/video/audio extensions up to 50 MB are accepted.
- **Login fails:** use the demo credentials above or register a citizen account.

## Testing
```bash
python -m py_compile app.py database.py auth.py
pytest -q
```

The project is intentionally designed to avoid raw HTML source appearing as user-facing content. CSS is injected only for visual styling, while interactive application controls use Streamlit components.

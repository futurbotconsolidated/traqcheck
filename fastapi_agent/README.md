# TraqCheck BGV Agent Service

AI-powered background verification agent using LangChain and Google Gemini 2.5 Pro.

## Quick Setup

1. **Install Dependencies**
```bash
cd /Users/abheysharma/traqcheck/fastapi_agent
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

2. **Configure Environment**
Edit `.env` file and add your Google API key:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

3. **Run FastAPI Server**
```bash
uvicorn main:app --reload --port 8002
```

Or:
```bash
python main.py
```

## API Endpoints

- `GET /` - Health check
- `POST /agent/send-credentials` - Send credentials with personalized email
- `POST /agent/analyze-request` - Analyze BGV request
- `POST /agent/send-reminder` - Send document reminder

## Testing

Visit: http://localhost:8002/docs for interactive API documentation.

## Django Integration

The Django Celery task will automatically call `/agent/send-credentials` when a new candidate is created.

For automated reminders, install django-celery-beat in Django backend:
```bash
pip install django-celery-beat
```

Then start Celery Beat worker.

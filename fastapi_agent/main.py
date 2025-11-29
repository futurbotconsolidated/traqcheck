"""
TraqCheck BGV Agent Service - FastAPI Application
Main entry point for the LangChain-powered background verification agent.
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from models.schemas import (
    SendCredentialsRequest,
    AnalyzeRequestPayload,
    SendReminderRequest,
    AgentResponse
)
from agent.agent import get_agent, invoke_agent_with_rate_limit, reset_agent
from agent.prompts import (
    ONBOARDING_PROMPT_TEMPLATE,
    REMINDER_SENDING_PROMPT_TEMPLATE
)
from datetime import datetime

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TraqCheck BGV Agent Service",
    version="1.0.0",
    description="AI-powered background verification agent using LangChain and Google Gemini"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "TraqCheck BGV Agent Service",
        "version": "1.0.0",
        "model": settings.gemini_model
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "django_api": settings.django_api_url,
        "gemini_model": settings.gemini_model,
        "ses_region": settings.aws_ses_region_name
    }


@app.post("/agent/reset")
async def reset_agent_cache():
    """Reset the cached agent (useful after model changes)."""
    reset_agent()
    logger.info("Agent cache reset via API")
    return {
        "status": "success",
        "message": "Agent cache reset",
        "current_model": settings.gemini_model
    }


@app.post("/agent/send-credentials")
async def onboard_candidate(payload: SendCredentialsRequest):
    """
    Complete candidate onboarding: send credentials AND request documents in ONE email.

    This unified workflow:
    1. Analyzes candidate profile for appropriate tone/formality
    2. Sends personalized email with login credentials
    3. Requests required documents (PAN Card, Aadhaar Card) in the same email
    4. Updates BGV status to 'documents_requested'
    5. Logs the action for audit trail

    Called by Django Celery task after candidate creation.
    """
    logger.info(f"Received onboarding request for BGV #{payload.bgv_request_id}")

    try:
        agent = get_agent()

        prompt = ONBOARDING_PROMPT_TEMPLATE.format(
            bgv_request_id=payload.bgv_request_id,
            candidate_name=payload.candidate_name,
            candidate_email=payload.candidate_email,
            temp_password=payload.temp_password
        )

        logger.info(f"Executing unified onboarding workflow - BGV #{payload.bgv_request_id}")
        result = invoke_agent_with_rate_limit(agent, [("user", prompt)])

        messages = result.get('messages', [])
        agent_output = messages[-1].content if messages else "Onboarding completed"

        logger.info(f"Agent completed onboarding for BGV #{payload.bgv_request_id}")

        return {
            "status": "success",
            "message": "Candidate onboarded: credentials sent and documents requested",
            "bgv_request_id": payload.bgv_request_id,
            "agent_output": agent_output,
            "agent_reasoning": "Check logs for detailed agent steps"
        }

    except Exception as e:
        logger.error(f"Error in candidate onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/send-reminder")
async def send_reminder(payload: SendReminderRequest):
    """
    Send document submission reminder to candidate.
    Agent generates context-aware reminder based on days pending and previous reminders.
    Can be triggered manually or automatically via Celery Beat.
    """
    logger.info(f"Received reminder request for BGV #{payload.bgv_request_id}, trigger: {payload.trigger}")

    try:
        agent = get_agent()

        prompt = REMINDER_SENDING_PROMPT_TEMPLATE.format(
            bgv_request_id=payload.bgv_request_id,
            trigger=payload.trigger
        )

        logger.info(f"Executing agent for reminder sending - BGV #{payload.bgv_request_id}")
        result = invoke_agent_with_rate_limit(agent, [("user", prompt)])

        messages = result.get('messages', [])
        agent_output = messages[-1].content if messages else "Reminder sent"

        logger.info(f"Agent completed reminder sending for BGV #{payload.bgv_request_id}")

        return {
            "status": "success",
            "message": "Reminder sent successfully",
            "bgv_request_id": payload.bgv_request_id,
            "agent_output": agent_output,
            "trigger": payload.trigger
        }

    except Exception as e:
        logger.error(f"Error in reminder sending: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

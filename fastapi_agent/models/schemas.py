"""
Pydantic models for request and response schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class SendCredentialsRequest(BaseModel):
    """Request body for sending candidate credentials"""
    bgv_request_id: int
    candidate_email: EmailStr
    candidate_name: str
    temp_password: str


class AnalyzeRequestPayload(BaseModel):
    """Request body for analyzing BGV request"""
    bgv_request_id: int
    candidate_email: EmailStr
    candidate_name: str
    role: str
    total_experience: int


class SendReminderRequest(BaseModel):
    """Request body for sending document reminder"""
    bgv_request_id: int
    trigger: str = "manual"  # "manual" or "automated"


class AgentResponse(BaseModel):
    """Generic agent response"""
    status: str
    message: str
    bgv_request_id: int
    agent_reasoning: Optional[str] = None
    email_message_id: Optional[str] = None
    days_pending: Optional[int] = None

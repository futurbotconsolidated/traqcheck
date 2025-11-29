from langchain.tools import tool
from services.django_client import django_client
from services.email_service import email_service
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@tool
def fetch_bgv_request(bgv_request_id: int) -> dict:
    """Fetch complete BGV request data including candidate profile, work experience, education, skills, and current status. Use this tool to get detailed information about a candidate before taking any action."""
    try:
        data = django_client.fetch_bgv_request(bgv_request_id)
        return {
            'success': True,
            'data': data
        }
    except Exception as e:
        logger.error(f"Tool error - fetch_bgv_request: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@tool
def analyze_candidate_profile(bgv_request_id: int) -> dict:
    """Analyze candidate's role, total work experience, and background to determine their seniority level (junior/mid/senior) and appropriate communication tone. Returns analysis summary with seniority classification."""
    try:
        bgv_data = django_client.fetch_bgv_request(bgv_request_id)

        total_exp = bgv_data.get('total_work_experience', 0)
        role = bgv_data.get('role', '')
        work_experiences = bgv_data.get('work_experiences', [])
        skills = bgv_data.get('skills', [])

        if total_exp <= 3:
            seniority = "junior"
            tone = "friendly and encouraging"
        elif total_exp <= 7:
            seniority = "mid-level"
            tone = "professional and direct"
        else:
            seniority = "senior"
            tone = "formal and respectful"

        leadership_keywords = ['cto', 'vp', 'director', 'head', 'lead', 'principal', 'chief']
        is_leadership = any(keyword in role.lower() for keyword in leadership_keywords)

        analysis = {
            'success': True,
            'seniority': seniority,
            'tone': tone,
            'total_experience': total_exp,
            'role': role,
            'is_leadership': is_leadership,
            'num_work_experiences': len(work_experiences),
            'num_skills': len(skills),
            'required_documents': ['PAN Card', 'Aadhaar Card'],
            'recommendation': f"Use {tone} tone for communication. Candidate has {total_exp} years of experience."
        }

        logger.info(f"Profile analysis for BGV #{bgv_request_id}: {seniority} level")
        return analysis

    except Exception as e:
        logger.error(f"Tool error - analyze_candidate_profile: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@tool
def send_email_to_candidate(to_email: str, subject: str, body_html: str) -> dict:
    """Send a professional HTML email to candidate using AWS SES. Use this for sending credentials, document requests, or reminders. The email body should be well-formatted HTML."""
    try:
        result = email_service.send_html_email(
            to_email=to_email,
            subject=subject,
            body_html=body_html
        )

        logger.info(f"Email sent to {to_email}, MessageId: {result['message_id']}")
        return {
            'success': True,
            'message_id': result['message_id'],
            'to_email': to_email
        }

    except Exception as e:
        logger.error(f"Tool error - send_email_to_candidate: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@tool
def log_agent_action(bgv_request_id: int, action: str, message: str, metadata: dict = None) -> dict:
    """Log agent action in Django database for audit trail. Action must be one of: 'analysis', 'request_sent', 'reminder_sent'. This creates a permanent record of all agent activities."""
    try:
        valid_actions = ['analysis', 'request_sent', 'reminder_sent']
        if action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of: {valid_actions}")

        result = django_client.create_agent_log(
            bgv_request_id=bgv_request_id,
            action=action,
            message=message,
            metadata=metadata or {}
        )

        logger.info(f"Logged action '{action}' for BGV #{bgv_request_id}")
        return {
            'success': True,
            'log_id': result.get('id'),
            'action': action
        }

    except Exception as e:
        logger.error(f"Tool error - log_agent_action: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@tool
def update_bgv_status(bgv_request_id: int, status: str) -> dict:
    """Update BGVRequest status in Django. Valid statuses: 'pending_analysis', 'documents_requested', 'documents_submitted', 'completed'. Use this to track workflow progression."""
    try:
        valid_statuses = ['pending_analysis', 'documents_requested', 'documents_submitted', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        result = django_client.update_bgv_status(
            bgv_request_id=bgv_request_id,
            status=status
        )

        logger.info(f"Updated BGV #{bgv_request_id} status to: {status}")
        return {
            'success': True,
            'bgv_request_id': bgv_request_id,
            'new_status': status
        }

    except Exception as e:
        logger.error(f"Tool error - update_bgv_status: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


ALL_TOOLS = [
    fetch_bgv_request,
    analyze_candidate_profile,
    send_email_to_candidate,
    log_agent_action,
    update_bgv_status
]

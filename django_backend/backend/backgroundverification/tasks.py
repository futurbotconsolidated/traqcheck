from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import requests
from .models import AgentLog


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_candidate_credentials(self, bgv_request_id, candidate_email, candidate_name, temp_password, agent_log_id):
    """
    Complete candidate onboarding via AI agent.

    This calls a UNIFIED workflow that:
    - Sends login credentials to the candidate
    - Requests required documents (PAN Card, Aadhaar Card)
    - Updates BGV status to 'documents_requested'
    All in ONE personalized email.
    """
    try:
        response = requests.post(
            f"{settings.FASTAPI_AGENT_URL}/agent/send-credentials",
            json={
                'bgv_request_id': bgv_request_id,
                'candidate_email': candidate_email,
                'candidate_name': candidate_name,
                'temp_password': temp_password
            },
            timeout=200  
        )

        response.raise_for_status()

        log = AgentLog.objects.get(id=agent_log_id)
        log.metadata['credentials_sent'] = True
        log.metadata['sent_via'] = 'agent_service'
        log.save()

        return {
            'status': 'success',
            'bgv_request_id': bgv_request_id,
            'message': 'Credentials sent via agent service'
        }

    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            notify_admin_credential_failure.delay(
                bgv_request_id=bgv_request_id,
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                temp_password=temp_password,
                agent_log_id=agent_log_id,
                error=str(exc)
            )

            return {
                'status': 'failed',
                'bgv_request_id': bgv_request_id,
                'error': str(exc),
                'message': 'Admin notified'
            }


@shared_task
def notify_admin_credential_failure(bgv_request_id, candidate_email, candidate_name, temp_password, agent_log_id, error):
    try:
        log = AgentLog.objects.get(id=agent_log_id)
        log.metadata['credentials_sent'] = False
        log.metadata['failure_reason'] = error
        log.metadata['admin_notified'] = True
        log.save()
    except AgentLog.DoesNotExist:
        pass

    admin_email = settings.ADMIN_EMAIL

    subject = f'URGENT: Failed to Send Candidate Credentials - BGV #{bgv_request_id}'

    message = f"""
ALERT: Automatic credential delivery failed after all retry attempts.

BGV Request ID: {bgv_request_id}
Candidate: {candidate_name}
Email: {candidate_email}

Error: {error}

MANUAL ACTION REQUIRED:
Please manually send the following credentials to the candidate:

---
Subject: Your Login Credentials for Background Verification

Hi {candidate_name},

Please use the following credentials to login and upload your documents:

Login URL: {settings.FRONTEND_URL}/login
Email: {candidate_email}
Temporary Password: {temp_password}

(Please change your password after first login)

Documents Required:
- PAN Card
- Aadhaar Card

Thank you!
---

This is an automated alert from TraqCheck BGV System.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        fail_silently=False,
    )

    return {
        'status': 'admin_notified',
        'bgv_request_id': bgv_request_id,
        'admin_email': admin_email
    }


@shared_task
def check_pending_document_requests():
    """
    Periodic task to check for pending document requests.
    Sends automated reminders via FastAPI agent if documents not submitted after 3 days.
    Runs daily via Celery Beat.
    """
    from datetime import datetime, timedelta
    from .models import BGVRequest

    # Find pending requests older than 3 days
    cutoff_date = datetime.now() - timedelta(days=3)

    pending_requests = BGVRequest.objects.filter(
        status='documents_requested',
        created_at__lt=cutoff_date
    )

    reminder_count = 0

    for bgv_request in pending_requests:
        # Check if reminder already sent in last 48 hours
        recent_reminders = AgentLog.objects.filter(
            bgv_request=bgv_request,
            action='reminder_sent',
            created_at__gte=datetime.now() - timedelta(hours=48)
        ).exists()

        if not recent_reminders:
            # Call FastAPI to send reminder
            try:
                response = requests.post(
                    f"{settings.FASTAPI_AGENT_URL}/agent/send-reminder",
                    json={
                        'bgv_request_id': bgv_request.id,
                        'trigger': 'automated'
                    },
                    timeout=200  # 1 minute timeout for agent execution
                )
                response.raise_for_status()
                reminder_count += 1
            except Exception as e:
                # Log error but continue with other requests
                print(f"Failed to send reminder for BGV #{bgv_request.id}: {e}")

    return {
        'status': 'completed',
        'total_pending': pending_requests.count(),
        'reminders_sent': reminder_count
    }

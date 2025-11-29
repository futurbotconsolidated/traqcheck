"""
Email service using AWS SES for sending emails to candidates.
"""
import boto3
from botocore.exceptions import ClientError
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """AWS SES email service for candidate communications"""

    def __init__(self):
        """Initialize AWS SES client"""
        self.ses_client = boto3.client(
            'ses',
            region_name=settings.aws_ses_region_name,
            aws_access_key_id=settings.aws_ses_access_key_id,
            aws_secret_access_key=settings.aws_ses_secret_access_key
        )
        self.from_email = settings.default_from_email

    def send_html_email(
        self,
        to_email: str,
        subject: str,
        body_html: str
    ) -> dict:
        """
        Send HTML email via AWS SES.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body_html: HTML email body

        Returns:
            dict: Response with message_id and status

        Raises:
            Exception: If email sending fails
        """
        try:
            logger.info(f"Sending email to {to_email} with subject: {subject}")

            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )

            message_id = response['MessageId']
            logger.info(f"Email sent successfully. MessageId: {message_id}")

            return {
                'status': 'success',
                'message_id': message_id
            }

        except ClientError as e:
            error_msg = e.response['Error']['Message']
            logger.error(f"Failed to send email: {error_msg}")
            raise Exception(f"AWS SES error: {error_msg}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise Exception(f"Email sending failed: {str(e)}")


# Global email service instance
email_service = EmailService()

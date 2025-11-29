
import httpx
from core.config import settings
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DjangoClient:
    """HTTP client for Django API communication"""

    def __init__(self):
        """Initialize HTTP client with base URL and headers"""
        self.base_url = settings.django_api_url
        self.headers = {
            'X-Service-Secret': settings.django_service_secret,
            'Content-Type': 'application/json'
        }
        self.timeout = 30.0

    def fetch_bgv_request(self, bgv_request_id: int) -> Dict[str, Any]:
        """
        Fetch complete BGV request data from Django.

        Args:
            bgv_request_id: ID of the BGV request

        Returns:
            dict: Complete BGV request data with nested relations

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}/api/bgv/{bgv_request_id}/"
        logger.info(f"Fetching BGV request #{bgv_request_id} from Django")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Successfully fetched BGV request #{bgv_request_id}")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching BGV request: {e.response.status_code}")
            raise Exception(f"Failed to fetch BGV request: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching BGV request: {str(e)}")
            raise Exception(f"Django API error: {str(e)}")

    def create_agent_log(
        self,
        bgv_request_id: int,
        action: str,
        message: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create an AgentLog entry in Django.

        Args:
            bgv_request_id: ID of the BGV request
            action: Action type ('analysis', 'request_sent', 'reminder_sent')
            message: Log message
            metadata: Additional metadata (optional)

        Returns:
            dict: Created log entry

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}/api/bgv/{bgv_request_id}/agent-log/"
        logger.info(f"Creating agent log for BGV #{bgv_request_id}, action: {action}")

        payload = {
            'action': action,
            'message': message,
            'metadata': metadata or {}
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Successfully created agent log #{data.get('id')}")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating agent log: {e.response.status_code}")
            raise Exception(f"Failed to create agent log: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating agent log: {str(e)}")
            raise Exception(f"Django API error: {str(e)}")

    def update_bgv_status(
        self,
        bgv_request_id: int,
        status: str
    ) -> Dict[str, Any]:
        """
        Update BGVRequest status in Django.

        Args:
            bgv_request_id: ID of the BGV request
            status: New status ('pending_analysis', 'documents_requested', etc.)

        Returns:
            dict: Updated BGV request

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}/api/bgv/{bgv_request_id}/"
        logger.info(f"Updating BGV #{bgv_request_id} status to: {status}")

        payload = {'status': status}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.patch(url, json=payload, headers=self.headers)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Successfully updated BGV #{bgv_request_id} status")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating BGV status: {e.response.status_code}")
            raise Exception(f"Failed to update BGV status: {e.response.text}")
        except Exception as e:
            logger.error(f"Error updating BGV status: {str(e)}")
            raise Exception(f"Django API error: {str(e)}")


django_client = DjangoClient()

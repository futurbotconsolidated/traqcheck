"""
Custom authentication for service-to-service communication.
Allows FastAPI agent service to authenticate using X-Service-Secret header.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class ServiceSecretAuthentication(BaseAuthentication):
    """
    Service-to-service authentication using X-Service-Secret header.
    This allows the FastAPI agent service to make authenticated requests to Django APIs.
    """

    def authenticate(self, request):
        # Get the service secret from request header
        service_secret = request.headers.get('X-Service-Secret')

        # If no service secret header, return None (let other auth methods handle it)
        if not service_secret:
            return None

        # Get expected secret from settings
        expected_secret = getattr(settings, 'DJANGO_SERVICE_SECRET', None)

        if not expected_secret:
            raise AuthenticationFailed('Service authentication not configured')

        # Validate the secret
        if service_secret != expected_secret:
            raise AuthenticationFailed('Invalid service secret')

        # Return None for user (service authentication doesn't have a user object)
        # Return the service identifier as auth
        return (None, 'fastapi_agent_service')

    def authenticate_header(self, request):
        """
        Return the authentication header to use in 401 responses
        """
        return 'X-Service-Secret'

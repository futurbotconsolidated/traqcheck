from rest_framework.permissions import BasePermission
from authentication.models import CustomUser


class IsAuthenticatedOrServiceSecret(BasePermission):
    """
    Allow access to authenticated users OR service-to-service authentication.
    This is used for endpoints that can be called by both users and the FastAPI agent service.
    """
    def has_permission(self, request, view):
        # Allow if user is authenticated via JWT
        if request.user and request.user.is_authenticated:
            return True
        # Allow if authenticated via service secret
        if request.auth == 'fastapi_agent_service':
            return True
        return False


class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.RECRUITER


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.CANDIDATE


class IsBGVRequestRecruiter(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and obj.recruiter == request.user


class IsBGVRequestCandidate(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and obj.user == request.user

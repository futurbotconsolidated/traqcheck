from rest_framework import serializers
from .models import BGVRequest, WorkExperience, Education, Skill, Project, Document, AgentLog
from authentication.serializers import UserSerializer


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'role', 'company_name', 'start_date', 'end_date', 'description']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'degree', 'field_of_study', 'institute', 'start_date', 'end_date', 'gpa']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill_name', 'years_of_experience', 'competency']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'link', 'role_name', 'skill_names']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'file', 'uploaded_at']


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = ['id', 'action', 'message', 'metadata', 'created_at']

    def to_representation(self, instance):
        """
        Override to exclude temp_password from metadata when request is from frontend.
        FastAPI agent service requests (with request.auth == 'fastapi_agent_service') 
        will still receive the full metadata including temp_password.
        """
        representation = super().to_representation(instance)
        
        # Check if request is from FastAPI agent service
        request = self.context.get('request')
        is_service_request = request and getattr(request, 'auth', None) == 'fastapi_agent_service'
        
        # If not a service request, remove temp_password from metadata
        if not is_service_request and 'metadata' in representation:
            metadata = representation['metadata'].copy() if representation['metadata'] else {}
            if 'temp_password' in metadata:
                metadata = metadata.copy()
                metadata.pop('temp_password', None)
                representation['metadata'] = metadata
        
        return representation


class AgentLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = ['action', 'message', 'metadata']

    def validate_action(self, value):
        """Validate that action is one of the allowed choices"""
        if value not in dict(AgentLog.Action.choices):
            raise serializers.ValidationError(f"Invalid action. Must be one of: {', '.join(dict(AgentLog.Action.choices).keys())}")
        return value


class BGVRequestListSerializer(serializers.ModelSerializer):
    recruiter = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = BGVRequest
        fields = ['id', 'user', 'recruiter', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'status', 'created_at']


class BGVRequestDetailSerializer(serializers.ModelSerializer):
    recruiter = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    agent_logs = AgentLogSerializer(many=True, read_only=True)

    class Meta:
        model = BGVRequest
        fields = [
            'id', 'user', 'recruiter', 'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'about', 'marital_status', 'hobbies', 'country_of_citizenship',
            'country_of_residence', 'role', 'total_work_experience', 'total_work_experience_months',
            'resume_file', 'status', 'created_at', 'updated_at',
            'work_experiences', 'educations', 'skills', 'projects', 'documents', 'agent_logs'
        ]


class BGVRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BGVRequest
        fields = ['status']

    def validate_status(self, value):
        """Validate that status is one of the allowed choices"""
        if value not in dict(BGVRequest.Status.choices):
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join(dict(BGVRequest.Status.choices).keys())}")
        return value

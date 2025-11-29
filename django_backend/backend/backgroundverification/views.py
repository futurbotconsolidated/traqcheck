from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from datetime import datetime
from authentication.models import CustomUser
from .models import BGVRequest, WorkExperience, Education, Skill, Project, Document, AgentLog
from .serializers import (
    BGVRequestListSerializer,
    BGVRequestDetailSerializer,
    BGVRequestUpdateSerializer,
    AgentLogCreateSerializer,
    AgentLogSerializer
)
from .utils import parse_resume_file, generate_random_password
from .permissions import IsRecruiter, IsAuthenticatedOrServiceSecret


class UploadResumeView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        resume_file = request.FILES.get('file')
        if not resume_file:
            return Response({'detail': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed_data = parse_resume_file(resume_file)

            if parsed_data.get('status') != 'success':
                return Response({'detail': 'Failed to parse resume'}, status=status.HTTP_400_BAD_REQUEST)

            data = parsed_data.get('data', {})

            email = data.get('email')
            if not email:
                return Response({'detail': 'Email not found in resume'}, status=status.HTTP_400_BAD_REQUEST)

            candidate_user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'role': CustomUser.Role.CANDIDATE,
                    'full_name': f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
                    'phone_number': data.get('phoneNumber', '')
                }
            )

            temp_password = None
            if created:
                temp_password = generate_random_password()
                candidate_user.set_password(temp_password)
                candidate_user.save()
            else:
                # User already exists - generate new temp password for testing
                temp_password = generate_random_password()
                candidate_user.set_password(temp_password)
                candidate_user.save()

            bgv_request = BGVRequest.objects.create(
                user=candidate_user,
                recruiter=request.user,
                first_name=data.get('firstName', ''),
                last_name=data.get('lastName', ''),
                email=email,
                phone_number=data.get('phoneNumber', ''),
                date_of_birth=self.parse_date(data.get('dateOfBirth')),
                about=data.get('about', ''),
                marital_status=data.get('maritalStatus', ''),
                hobbies=data.get('hobbies', ''),
                country_of_citizenship=data.get('countryOfCitizenship', ''),
                country_of_residence=data.get('countryOfResidence', ''),
                role=data.get('role', ''),
                total_work_experience=data.get('totalWorkExperience', 0),
                total_work_experience_months=data.get('totalWorkExperienceInMonths', 0),
                resume_file=resume_file,
                status=BGVRequest.Status.PENDING_ANALYSIS
            )

            work_experiences = [
                WorkExperience(
                    bgv_request=bgv_request,
                    role=exp.get('role', ''),
                    company_name=exp.get('companyName', ''),
                    start_date=self.parse_date(exp.get('startDate')),
                    end_date=self.parse_date(exp.get('endDate')),
                    description=exp.get('description', '')
                )
                for exp in data.get('professionalBackground', [])
            ]
            WorkExperience.objects.bulk_create(work_experiences)

            educations = [
                Education(
                    bgv_request=bgv_request,
                    degree=edu.get('degree', ''),
                    field_of_study=edu.get('fieldOfStudy', ''),
                    institute=edu.get('institute', ''),
                    start_date=self.parse_date(edu.get('startDate')),
                    end_date=self.parse_date(edu.get('endDate')),
                    gpa=edu.get('gpa', '')
                )
                for edu in data.get('educationalBackground', [])
            ]
            Education.objects.bulk_create(educations)

            skills = [
                Skill(
                    bgv_request=bgv_request,
                    skill_name=skill.get('skillName', ''),
                    years_of_experience=skill.get('yearsOfExperience', 0),
                    competency=skill.get('competency', '')
                )
                for skill in data.get('skills', [])
            ]
            Skill.objects.bulk_create(skills)

            projects = [
                Project(
                    bgv_request=bgv_request,
                    name=project.get('name', ''),
                    description=project.get('description', ''),
                    link=project.get('link', ''),
                    role_name=project.get('role', {}).get('name', ''),
                    skill_names=project.get('skills', {}).get('skillNames', [])
                )
                for project in data.get('projects', [])
            ]
            Project.objects.bulk_create(projects)

            if temp_password:
                log = AgentLog.objects.create(
                    bgv_request=bgv_request,
                    action=AgentLog.Action.ANALYSIS,
                    message='Candidate account created, credentials queued for delivery',
                    metadata={
                        'temp_password': temp_password,
                        'user_created': True,
                        'candidate_email': email,
                        'credentials_sent': False
                    }
                )

                from .tasks import send_candidate_credentials
                send_candidate_credentials.delay(
                    bgv_request_id=bgv_request.id,
                    candidate_email=email,
                    candidate_name=f"{bgv_request.first_name} {bgv_request.last_name}",
                    temp_password=temp_password,
                    agent_log_id=log.id
                )

            return Response({
                'detail': 'Resume uploaded successfully. Candidate will receive login credentials via email shortly.',
                'bgv_request': BGVRequestDetailSerializer(bgv_request, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return None


class BGVRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BGVRequestListSerializer

    def get_queryset(self):
        if self.request.user.role == CustomUser.Role.RECRUITER:
            return BGVRequest.objects.filter(recruiter=self.request.user)
        else:
            return BGVRequest.objects.filter(user=self.request.user)


class BGVRequestDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrServiceSecret]

    def get_queryset(self):
        if self.request.auth == 'fastapi_agent_service':
            return BGVRequest.objects.all()
        if self.request.user.role == CustomUser.Role.RECRUITER:
            return BGVRequest.objects.filter(recruiter=self.request.user)
        else:
            return BGVRequest.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BGVRequestUpdateSerializer
        return BGVRequestDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(BGVRequestDetailSerializer(instance, context={'request': request}).data)


class CreateAgentLogView(APIView):
    permission_classes = [IsAuthenticatedOrServiceSecret]

    def post(self, request, pk):
        bgv_request = get_object_or_404(BGVRequest, pk=pk)

        serializer = AgentLogCreateSerializer(data=request.data)
        if serializer.is_valid():
            agent_log = serializer.save(bgv_request=bgv_request)
            return Response(
                AgentLogSerializer(agent_log, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        bgv_request = get_object_or_404(BGVRequest, pk=pk, user=request.user)

        pan_file = request.FILES.get('pan')
        aadhaar_file = request.FILES.get('aadhaar')

        if not pan_file and not aadhaar_file:
            return Response({'detail': 'At least one document is required'}, status=status.HTTP_400_BAD_REQUEST)

        documents = []
        if pan_file:
            documents.append(Document(
                bgv_request=bgv_request,
                document_type=Document.DocumentType.PAN,
                file=pan_file
            ))

        if aadhaar_file:
            documents.append(Document(
                bgv_request=bgv_request,
                document_type=Document.DocumentType.AADHAAR,
                file=aadhaar_file
            ))

        Document.objects.bulk_create(documents)

        bgv_request.status = BGVRequest.Status.DOCUMENTS_SUBMITTED
        bgv_request.save()

        return Response({
            'detail': 'Documents submitted successfully',
            'bgv_request': BGVRequestDetailSerializer(bgv_request, context={'request': request}).data
        }, status=status.HTTP_200_OK)

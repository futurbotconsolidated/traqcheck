from django.db import models
from authentication.models import CustomUser


class BGVRequest(models.Model):
    class Status(models.TextChoices):
        PENDING_ANALYSIS = 'pending_analysis', 'Pending Analysis'
        DOCUMENTS_REQUESTED = 'documents_requested', 'Documents Requested'
        DOCUMENTS_SUBMITTED = 'documents_submitted', 'Documents Submitted'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bgv_requests')
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recruiter_bgv_requests')

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    about = models.TextField(blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    hobbies = models.TextField(blank=True, null=True)
    country_of_citizenship = models.CharField(max_length=100, null=True, blank=True)
    country_of_residence = models.CharField(max_length=100, null=True, blank=True)

    role = models.CharField(max_length=200, null=True, blank=True)
    total_work_experience = models.IntegerField(default=0, null=True, blank=True)
    total_work_experience_months = models.IntegerField(default=0)

    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING_ANALYSIS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email} (by {self.recruiter.email})"

    class Meta:
        ordering = ['-created_at']


class WorkExperience(models.Model):
    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='work_experiences')
    role = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} at {self.company_name}"

    class Meta:
        ordering = ['-start_date']


class Education(models.Model):
    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    institute = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    gpa = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.degree} - {self.institute}"

    class Meta:
        ordering = ['-end_date']


class Skill(models.Model):
    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    years_of_experience = models.IntegerField(default=0)
    competency = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill_name} - {self.competency}"


class Project(models.Model):
    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True, null=True)
    role_name = models.CharField(max_length=200, blank=True, null=True)
    skill_names = models.JSONField(default=list, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    class DocumentType(models.TextChoices):
        PAN = 'pan', 'PAN Card'
        AADHAAR = 'aadhaar', 'Aadhaar Card'

    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(upload_to='documents/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bgv_request.email} - {self.document_type}"

    class Meta:
        ordering = ['-uploaded_at']


class AgentLog(models.Model):
    class Action(models.TextChoices):
        ANALYSIS = 'analysis', 'Profile Analysis'
        REQUEST_SENT = 'request_sent', 'Document Request Sent'
        REMINDER_SENT = 'reminder_sent', 'Reminder Sent'

    bgv_request = models.ForeignKey(BGVRequest, on_delete=models.CASCADE, related_name='agent_logs')
    action = models.CharField(max_length=50, choices=Action.choices)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bgv_request.email} - {self.action}"

    class Meta:
        ordering = ['-created_at']

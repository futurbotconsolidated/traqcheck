from django.contrib import admin
from .models import BGVRequest, WorkExperience, Education, Skill, Project, Document, AgentLog


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0


class AgentLogInline(admin.TabularInline):
    model = AgentLog
    extra = 0
    readonly_fields = ['action', 'message', 'metadata', 'created_at']


@admin.register(BGVRequest)
class BGVRequestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'role', 'status', 'recruiter', 'user', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WorkExperienceInline, EducationInline, SkillInline, ProjectInline, DocumentInline, AgentLogInline]


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'role', 'company_name', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['role', 'company_name']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'degree', 'field_of_study', 'institute', 'end_date']
    list_filter = ['degree']
    search_fields = ['degree', 'institute']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'skill_name', 'years_of_experience', 'competency']
    list_filter = ['competency']
    search_fields = ['skill_name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'name', 'role_name']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ['bgv_request', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    readonly_fields = ['bgv_request', 'action', 'message', 'metadata', 'created_at']

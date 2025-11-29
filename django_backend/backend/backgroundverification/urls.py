from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadResumeView.as_view(), name='upload-resume'),
    path('', views.BGVRequestListView.as_view(), name='bgv-request-list'),
    path('<int:pk>/', views.BGVRequestDetailView.as_view(), name='bgv-request-detail'),
    path('<int:pk>/agent-log/', views.CreateAgentLogView.as_view(), name='create-agent-log'),
    path('<int:pk>/submit-documents/', views.SubmitDocumentsView.as_view(), name='submit-documents'),
]

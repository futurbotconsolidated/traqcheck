'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { USER_ROLES, ROUTES } from '@/lib/constants';
import { bgvApi, BGVRequest, WorkExperience, Education, Skill, Project, AgentLog } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Phone, 
  Briefcase, 
  Calendar, 
  CheckCircle, 
  Clock, 
  XCircle,
  FileText,
  GraduationCap,
  Code,
  Globe,
  Download,
  Activity,
  Upload,
  FileCheck
} from 'lucide-react';
import DocumentUploadModal from '@/components/DocumentUploadModal';

export default function CandidateBGVDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [bgv, setBgv] = useState<BGVRequest | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const bgvId = params?.id ? parseInt(params.id as string) : null;

  useEffect(() => {
    if (!bgvId) {
      setError('Invalid BGV ID');
      setIsLoading(false);
      return;
    }

    const fetchBGVDetail = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await bgvApi.getDetail(bgvId);
        
        if (response.status === 'success' && response.data) {
          setBgv(response.data);
        } else {
          setError(response.message || 'Failed to fetch BGV details');
        }
      } catch (err: unknown) {
        const error = err as { response?: { data?: { message?: string } } };
        setError(
          error.response?.data?.message ||
          'An error occurred while fetching BGV details'
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchBGVDetail();
  }, [bgvId]);

  const handleUploadSuccess = () => {
    // Refresh BGV details after successful upload
    if (bgvId) {
      const fetchBGVDetail = async () => {
        try {
          const response = await bgvApi.getDetail(bgvId);
          if (response.status === 'success' && response.data) {
            setBgv(response.data);
          }
        } catch (err) {
          console.error('Failed to refresh BGV details:', err);
        }
      };
      fetchBGVDetail();
    }
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const formatDateTime = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const getStatusIcon = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'completed' || statusLower === 'success' || statusLower === 'verified') {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    if (statusLower === 'pending' || statusLower === 'in_progress' || statusLower === 'documents_requested') {
      return <Clock className="h-5 w-5 text-yellow-600" />;
    }
    if (statusLower === 'failed' || statusLower === 'rejected') {
      return <XCircle className="h-5 w-5 text-red-600" />;
    }
    return <Clock className="h-5 w-5 text-gray-600" />;
  };

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'completed' || statusLower === 'success' || statusLower === 'verified') {
      return 'text-green-600 bg-green-50 border-green-200';
    }
    if (statusLower === 'pending' || statusLower === 'in_progress' || statusLower === 'documents_requested') {
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
    if (statusLower === 'failed' || statusLower === 'rejected') {
      return 'text-red-600 bg-red-50 border-red-200';
    }
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  const getCompetencyColor = (competency: string) => {
    const comp = competency.toLowerCase();
    if (comp === 'high') return 'text-green-600 bg-green-50';
    if (comp === 'medium') return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <ProtectedRoute allowedRoles={[USER_ROLES.CANDIDATE]}>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push(ROUTES.CANDIDATE_DASHBOARD)}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
                <h1 className="text-xl font-semibold">TraqCheck</h1>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  {user?.full_name} ({user?.email})
                </span>
                <Button variant="outline" onClick={logout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {isLoading ? (
            <div className="text-center py-12">
              <p className="text-lg text-gray-500">Loading BGV details...</p>
            </div>
          ) : error ? (
            <Card>
              <CardContent className="pt-6">
                <div className="rounded-md bg-red-50 p-4 text-sm text-red-600">
                  {error}
                </div>
                <Button
                  className="mt-4"
                  onClick={() => router.push(ROUTES.CANDIDATE_DASHBOARD)}
                >
                  Back to Dashboard
                </Button>
              </CardContent>
            </Card>
          ) : bgv ? (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">
                    Background Verification Request #{bgv.id}
                  </h2>
                  <p className="mt-2 text-gray-600">
                    View your background verification details
                  </p>
                </div>
                <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${getStatusColor(bgv.status)}`}>
                  {getStatusIcon(bgv.status)}
                  <span className="font-medium capitalize">
                    {bgv.status.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>

              {/* Actions Card */}
              <Card>
                <CardContent className="pt-6">
                  <div className="flex flex-col sm:flex-row gap-4">
                    {bgv.resume_file && (
                      <a
                        href={bgv.resume_file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-primary hover:underline"
                      >
                        <Download className="h-5 w-5" />
                        <span className="font-medium">Download Resume</span>
                      </a>
                    )}
                    {bgv.status === 'documents_requested' && (
                      <Button
                        onClick={() => setIsUploadModalOpen(true)}
                        className="flex items-center gap-2"
                      >
                        <Upload className="h-4 w-4" />
                        Upload Documents
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="grid gap-6 md:grid-cols-2">
                {/* My Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5" />
                      My Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Full Name</p>
                      <p className="text-lg font-semibold">
                        {bgv.first_name} {bgv.last_name}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Email
                      </p>
                      <p className="text-lg">{bgv.email || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        Phone Number
                      </p>
                      <p className="text-lg">{bgv.phone_number || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <Briefcase className="h-4 w-4" />
                        Job Role
                      </p>
                      <p className="text-lg">{bgv.role || 'N/A'}</p>
                    </div>
                    {bgv.date_of_birth && (
                      <div>
                        <p className="text-sm font-medium text-gray-500">Date of Birth</p>
                        <p className="text-lg">{formatDate(bgv.date_of_birth)}</p>
                      </div>
                    )}
                    {bgv.country_of_residence && (
                      <div>
                        <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
                          <Globe className="h-4 w-4" />
                          Country of Residence
                        </p>
                        <p className="text-lg">{bgv.country_of_residence}</p>
                      </div>
                    )}
                    {bgv.country_of_citizenship && (
                      <div>
                        <p className="text-sm font-medium text-gray-500">Country of Citizenship</p>
                        <p className="text-lg">{bgv.country_of_citizenship}</p>
                      </div>
                    )}
                    {bgv.marital_status && (
                      <div>
                        <p className="text-sm font-medium text-gray-500">Marital Status</p>
                        <p className="text-lg">{bgv.marital_status}</p>
                      </div>
                    )}
                    {bgv.hobbies && (
                      <div>
                        <p className="text-sm font-medium text-gray-500">Hobbies</p>
                        <p className="text-lg">{bgv.hobbies}</p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-500">Total Work Experience</p>
                      <p className="text-lg">
                        {bgv.total_work_experience} years ({bgv.total_work_experience_months} months)
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Request Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      Request Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Request ID</p>
                      <p className="text-lg font-semibold">#{bgv.id}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Status</p>
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(bgv.status)}`}>
                        {getStatusIcon(bgv.status)}
                        <span className="capitalize">
                          {bgv.status.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Created At</p>
                      <p className="text-lg">{formatDateTime(bgv.created_at)}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Updated At</p>
                      <p className="text-lg">{formatDateTime(bgv.updated_at)}</p>
                    </div>
                    {bgv.recruiter && (
                      <div>
                        <p className="text-sm font-medium text-gray-500">Recruiter</p>
                        <p className="text-lg">{bgv.recruiter.full_name}</p>
                        <p className="text-sm text-gray-500">{bgv.recruiter.email}</p>
                        {bgv.recruiter.phone_number && (
                          <p className="text-sm text-gray-500">{bgv.recruiter.phone_number}</p>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* About */}
              {bgv.about && (
                <Card>
                  <CardHeader>
                    <CardTitle>About</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 whitespace-pre-line">{bgv.about}</p>
                  </CardContent>
                </Card>
              )}

              {/* Work Experience */}
              {bgv.work_experiences && bgv.work_experiences.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Briefcase className="h-5 w-5" />
                      Work Experience
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {bgv.work_experiences.map((exp: WorkExperience) => (
                      <div key={exp.id} className="border-l-4 border-primary pl-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-lg font-semibold">{exp.role}</h3>
                            <p className="text-gray-600">{exp.company_name}</p>
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatDate(exp.start_date)} - {exp.end_date ? formatDate(exp.end_date) : 'Present'}
                          </div>
                        </div>
                        {exp.description && (
                          <p className="text-gray-700 whitespace-pre-line mt-2">{exp.description}</p>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Education */}
              {bgv.educations && bgv.educations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <GraduationCap className="h-5 w-5" />
                      Education
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {bgv.educations.map((edu: Education) => (
                      <div key={edu.id} className="border-l-4 border-blue-500 pl-4">
                        <h3 className="text-lg font-semibold">{edu.degree}</h3>
                        <p className="text-gray-600">{edu.field_of_study}</p>
                        <p className="text-gray-500">{edu.institute}</p>
                        <div className="flex justify-between items-center mt-2">
                          <p className="text-sm text-gray-500">
                            {formatDate(edu.start_date)} - {formatDate(edu.end_date)}
                          </p>
                          {edu.gpa && (
                            <p className="text-sm font-medium">GPA: {edu.gpa}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Skills */}
              {bgv.skills && bgv.skills.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Code className="h-5 w-5" />
                      Skills
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {bgv.skills.map((skill: Skill) => (
                        <div
                          key={skill.id}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-white"
                        >
                          <span className="font-medium">{skill.skill_name}</span>
                          <span className="text-xs text-gray-500">
                            ({skill.years_of_experience} yrs)
                          </span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${getCompetencyColor(skill.competency)}`}
                          >
                            {skill.competency}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Projects */}
              {bgv.projects && bgv.projects.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Projects
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {bgv.projects.map((project: Project) => (
                      <div key={project.id} className="border-l-4 border-purple-500 pl-4">
                        <h3 className="text-lg font-semibold">{project.name}</h3>
                        {project.description && (
                          <p className="text-gray-700 mt-2">{project.description}</p>
                        )}
                        {project.link && (
                          <a
                            href={project.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline text-sm mt-2 inline-block"
                          >
                            View Project →
                          </a>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Documents */}
              {bgv.documents && bgv.documents.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileCheck className="h-5 w-5" />
                      Uploaded Documents
                    </CardTitle>
                    <CardDescription>
                      Documents submitted for background verification
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2">
                      {bgv.documents.map((doc) => (
                        <div
                          key={doc.id}
                          className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="font-semibold capitalize">
                                {doc.document_type === 'pan' ? 'PAN Card' : 'Aadhaar Card'}
                              </h3>
                              <p className="text-sm text-gray-500 mt-1">
                                Uploaded: {formatDateTime(doc.uploaded_at)}
                              </p>
                            </div>
                            <div className="rounded-full bg-blue-100 p-2">
                              <FileCheck className="h-4 w-4 text-blue-600" />
                            </div>
                          </div>
                          <a
                            href={doc.file}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-primary hover:underline text-sm mt-3"
                          >
                            <Download className="h-4 w-4" />
                            View Document
                          </a>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Agent Logs */}
              {bgv.agent_logs && bgv.agent_logs.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Agent Activity Log
                    </CardTitle>
                    <CardDescription>
                      Timeline of automated actions taken by the AI agent
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {bgv.agent_logs.map((log: AgentLog) => (
                        <div key={log.id} className="border-l-4 border-gray-300 pl-4 pb-4 last:pb-0">
                          <div className="flex justify-between items-start mb-1">
                            <div>
                              <span className="font-medium capitalize text-sm">
                                {log.action.replace(/_/g, ' ')}
                              </span>
                              <p className="text-gray-700 mt-1">{log.message}</p>
                            </div>
                            <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                              {formatDateTime(log.created_at)}
                            </span>
                          </div>
                          {log.metadata && Object.keys(log.metadata).length > 0 && (
                            <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                              <pre className="whitespace-pre-wrap">
                                {JSON.stringify(log.metadata, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : null}

          {/* Document Upload Modal */}
          {bgvId && (
            <DocumentUploadModal
              open={isUploadModalOpen}
              onOpenChange={setIsUploadModalOpen}
              bgvId={bgvId}
              onSuccess={handleUploadSuccess}
            />
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}


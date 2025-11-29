import axios from 'axios';
import { apiConfig, getAuthHeaders } from './api-config';
import { API_ENDPOINTS } from './constants';
import { STORAGE_KEYS } from './constants';

// Create axios instance
const apiClient = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  headers: apiConfig.headers,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Check if data is FormData (for file uploads)
    const isFormData = config.data instanceof FormData;
    const headers = getAuthHeaders(!isFormData);
    
    // For FormData, only add Authorization, let browser set Content-Type with boundary
    if (isFormData) {
      if (headers['Authorization']) {
        config.headers['Authorization'] = headers['Authorization'];
      }
      // Remove Content-Type to let browser set it with boundary
      delete config.headers['Content-Type'];
    } else {
      config.headers = { ...config.headers, ...headers };
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear tokens on unauthorized
      if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone_number: string;
  role: 'recruiter' | 'candidate';
  created_at: string;
}

export interface Tokens {
  refresh: string;
  access: string;
}

export interface LoginResponse {
  message: string;
  errors: null | Record<string, string[]>;
  data: {
    user: User;
    tokens: Tokens;
  };
  status: 'success' | 'error';
  status_code: number;
}

// BGV Types
export interface BGVUser {
  id: number;
  email: string;
  full_name: string;
  phone_number: string;
  role: 'recruiter' | 'candidate';
  created_at: string;
}

export interface WorkExperience {
  id: number;
  role: string;
  company_name: string;
  start_date: string;
  end_date: string | null;
  description: string;
}

export interface Education {
  id: number;
  degree: string;
  field_of_study: string;
  institute: string;
  start_date: string;
  end_date: string;
  gpa: string;
}

export interface Skill {
  id: number;
  skill_name: string;
  years_of_experience: number;
  competency: 'High' | 'Medium' | 'Low';
}

export interface Project {
  id: number;
  name: string;
  description: string;
  link: string | null;
  role_name: string;
  skill_names: string[];
}

export interface Document {
  id: number;
  document_type: 'pan' | 'aadhaar';
  file: string;
  uploaded_at: string;
}

export interface AgentLog {
  id: number;
  action: string;
  message: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface BGVRequest {
  id: number;
  user: BGVUser;
  recruiter: BGVUser;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  date_of_birth: string | null;
  about: string | null;
  marital_status: string | null;
  hobbies: string | null;
  country_of_citizenship: string | null;
  country_of_residence: string | null;
  role: string; // Job role (e.g., "Senior Software Engineer")
  total_work_experience: number;
  total_work_experience_months: number;
  resume_file: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  work_experiences: WorkExperience[];
  educations: Education[];
  skills: Skill[];
  projects: Project[];
  documents: Document[];
  agent_logs: AgentLog[];
}

export interface BGVListResponse {
  message?: string;
  errors?: null | Record<string, string[]>;
  data?: BGVRequest[];
  status?: 'success' | 'error';
  status_code?: number;
}

export interface BGVUploadResponse {
  message?: string;
  errors?: null | Record<string, string[]>;
  data?: BGVRequest;
  status?: 'success' | 'error';
  status_code?: number;
}

export interface BGVDetailResponse {
  message?: string;
  errors?: null | Record<string, string[]>;
  data?: BGVRequest;
  status?: 'success' | 'error';
  status_code?: number;
}

export interface BGVSubmitDocumentsResponse {
  message?: string;
  errors?: null | Record<string, string[]>;
  data?: BGVRequest;
  status?: 'success' | 'error';
  status_code?: number;
}

// API functions
export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      API_ENDPOINTS.LOGIN,
      credentials
    );
    return response.data;
  },
};

export const bgvApi = {
  upload: async (file: File): Promise<BGVUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Don't set Content-Type header - axios will handle it automatically for FormData
    const response = await apiClient.post<BGVUploadResponse>(
      API_ENDPOINTS.BGV_UPLOAD,
      formData
    );
    return response.data;
  },

  list: async (): Promise<BGVListResponse> => {
    const response = await apiClient.get<BGVListResponse>(
      API_ENDPOINTS.BGV_LIST
    );
    return response.data;
  },

  getDetail: async (id: number): Promise<BGVDetailResponse> => {
    const response = await apiClient.get<BGVDetailResponse>(
      API_ENDPOINTS.BGV_DETAIL(id)
    );
    return response.data;
  },

  submitDocuments: async (
    id: number,
    panFile: File,
    aadhaarFile: File
  ): Promise<BGVSubmitDocumentsResponse> => {
    const formData = new FormData();
    formData.append('pan', panFile);
    formData.append('aadhaar', aadhaarFile);
    
    const response = await apiClient.post<BGVSubmitDocumentsResponse>(
      API_ENDPOINTS.BGV_SUBMIT_DOCUMENTS(id),
      formData
    );
    return response.data;
  },
};

export default apiClient;


// API Base URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// User roles
export const USER_ROLES = {
  RECRUITER: 'recruiter',
  CANDIDATE: 'candidate',
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];

// API endpoints
export const API_ENDPOINTS = {
  LOGIN: '/api/auth/login/',
  BGV_UPLOAD: '/api/bgv/upload/',
  BGV_LIST: '/api/bgv/',
  BGV_DETAIL: (id: number) => `/api/bgv/${id}/`,
  BGV_SUBMIT_DOCUMENTS: (id: number) => `/api/bgv/${id}/submit-documents/`,
} as const;

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
} as const;

// Routes
export const ROUTES = {
  LOGIN: '/login',
  RECRUITER_DASHBOARD: '/dashboard/recruiter',
  CANDIDATE_DASHBOARD: '/dashboard/candidate',
  BGV_DETAIL: (id: number) => `/dashboard/recruiter/bgv/${id}`,
  CANDIDATE_BGV_DETAIL: (id: number) => `/dashboard/candidate/bgv/${id}`,
} as const;


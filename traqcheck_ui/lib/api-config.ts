import { API_BASE_URL, STORAGE_KEYS } from './constants';

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// Get auth headers with access token
export const getAuthHeaders = (includeContentType: boolean = true): Record<string, string> => {
  if (typeof window === 'undefined') {
    return includeContentType ? apiConfig.headers : {};
  }

  const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  const headers: Record<string, string> = {};
  
  if (includeContentType) {
    headers['Content-Type'] = apiConfig.headers['Content-Type'];
  }
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  return Object.keys(headers).length > 0 ? headers : apiConfig.headers;
};


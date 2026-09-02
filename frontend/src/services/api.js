import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch root application metadata from backend.
 * GET / -> { "name": "AI Finance Controller", "status": "running" }
 */
export const getRootInfo = async () => {
  const response = await apiClient.get('/');
  return response.data;
};

/**
 * Fetch backend health status.
 * GET /api/health -> { "status": "healthy" }
 */
export const getHealthStatus = async () => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

export default apiClient;

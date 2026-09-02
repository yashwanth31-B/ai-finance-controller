import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
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

/**
 * Fetch live system operational metrics and ground truth performance.
 * GET /api/metrics
 */
export const getMetrics = async () => {
  const response = await apiClient.get('/api/metrics');
  return response.data;
};

/**
 * Trigger batch multi-source 3-way reconciliation run.
 * POST /api/reconciliation/run
 */
export const runReconciliation = async () => {
  const response = await apiClient.post('/api/reconciliation/run');
  return response.data;
};

/**
 * Fetch all reconciliation results from the latest execution run.
 * GET /api/reconciliation/results
 */
export const getReconciliationResults = async () => {
  const response = await apiClient.get('/api/reconciliation/results');
  return response.data;
};

/**
 * Fetch single reconciliation result by invoice ID.
 * GET /api/reconciliation/results/:invoiceId
 */
export const getSingleResult = async (invoiceId) => {
  const response = await apiClient.get(`/api/reconciliation/results/${invoiceId}`);
  return response.data;
};

/**
 * Fetch active exceptions list with optional status/severity/type query filters.
 * GET /api/exceptions
 */
export const getExceptions = async (params = {}) => {
  const response = await apiClient.get('/api/exceptions', { params });
  return response.data;
};

/**
 * Fetch single exception record details by exception ID.
 * GET /api/exceptions/:exceptionId
 */
export const getSingleException = async (exceptionId) => {
  const response = await apiClient.get(`/api/exceptions/${exceptionId}`);
  return response.data;
};

export default apiClient;

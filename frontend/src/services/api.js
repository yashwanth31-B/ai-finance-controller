import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
 * Trigger batch multi-source 3-way reconciliation run on demo synthetic dataset.
 * POST /api/reconciliation/run
 */
export const runReconciliation = async () => {
  const response = await apiClient.post('/api/reconciliation/run');
  return response.data;
};

/**
 * Validate 3 uploaded CSV files (invoices, bank, gateway).
 * POST /api/upload/validate
 */
export const validateUploadFiles = async (formData) => {
  const response = await apiClient.post('/api/upload/validate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Trigger 3-way reconciliation run on validated uploaded CSV batch.
 * POST /api/reconciliation/run-uploaded
 */
export const runUploadedReconciliation = async (uploadBatchId) => {
  const response = await apiClient.post('/api/reconciliation/run-uploaded', {
    upload_batch_id: uploadBatchId,
  });
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

/**
 * Submit a human review decision (APPROVE_MATCH, REJECT_MATCH, MARK_RESOLVED, KEEP_UNDER_REVIEW).
 * POST /api/reviews
 */
export const submitReviewAction = async (payload) => {
  const response = await apiClient.post('/api/reviews', payload);
  return response.data;
};

/**
 * Fetch review history logs with optional query filters.
 * GET /api/reviews
 */
export const getReviews = async (params = {}) => {
  const response = await apiClient.get('/api/reviews', { params });
  return response.data;
};

/**
 * Fetch review history for a specific invoice ID.
 * GET /api/reviews/:invoiceId
 */
export const getInvoiceReviews = async (invoiceId) => {
  const response = await apiClient.get(`/api/reviews/${invoiceId}`);
  return response.data;
};

/**
 * Fetch immutable audit trail event logs with optional filters.
 * GET /api/audit-trail
 */
export const getAuditTrail = async (params = {}) => {
  const response = await apiClient.get('/api/audit-trail', { params });
  return response.data;
};

/**
 * Trigger AI-assisted root-cause analysis for an exception record.
 * POST /api/ai/analyze-exception
 */
export const analyzeExceptionWithAI = async (payload) => {
  const response = await apiClient.post('/api/ai/analyze-exception', payload);
  return response.data;
};

export default apiClient;

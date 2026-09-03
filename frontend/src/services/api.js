import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
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

/**
 * Helper to download binary or text files from reports endpoints.
 */
export const downloadReportFile = async (endpoint, defaultFilename) => {
  const response = await apiClient.get(endpoint, {
    responseType: 'blob',
  });
  const blob = new Blob([response.data], {
    type: response.headers['content-type'] || 'application/octet-stream',
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  
  const disposition = response.headers['content-disposition'];
  let filename = defaultFilename;
  if (disposition && disposition.includes('filename=')) {
    const matches = /filename="?([^";]+)"?/.exec(disposition);
    if (matches && matches[1]) {
      filename = matches[1];
    }
  }
  
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadReconciliationCSV = () => downloadReportFile('/api/reports/reconciliation.csv', 'reconciliation_report.csv');
export const downloadExceptionsCSV = () => downloadReportFile('/api/reports/exceptions.csv', 'exceptions_report.csv');
export const downloadAuditCSV = () => downloadReportFile('/api/reports/audit.csv', 'audit_trail_report.csv');
export const downloadSummaryPDF = () => downloadReportFile('/api/reports/summary.pdf', 'reconciliation_summary.pdf');

/**
 * Fetch current system settings and reconciliation tolerances.
 * GET /api/settings
 */
export const getSettings = async () => {
  const response = await apiClient.get('/api/settings');
  return response.data;
};

/**
 * Update system settings and reconciliation rules.
 * PUT /api/settings
 */
export const updateSettings = async (payload) => {
  const response = await apiClient.put('/api/settings', payload);
  return response.data;
};

/**
 * Reset system settings to safe defaults.
 * POST /api/settings/reset
 */
export const resetSettings = async () => {
  const response = await apiClient.post('/api/settings/reset');
  return response.data;
};

/** Auth Endpoints */
export const loginUser = async (email, password) => {
  const response = await apiClient.post('/api/auth/login', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/api/auth/me');
  return response.data;
};

export const logoutUser = async () => {
  const response = await apiClient.post('/api/auth/logout');
  return response.data;
};

/** Notification Endpoints */
export const getNotifications = async (params = {}) => {
  const response = await apiClient.get('/api/notifications', { params });
  return response.data;
};

export const markNotificationRead = async (id) => {
  const response = await apiClient.post(`/api/notifications/${id}/read`);
  return response.data;
};

export const markAllNotificationsRead = async () => {
  const response = await apiClient.post('/api/notifications/read-all');
  return response.data;
};

/** Assistant Q&A Endpoint */
export const queryAssistant = async (question) => {
  const response = await apiClient.post('/api/assistant/query', { question });
  return response.data;
};

export default apiClient;

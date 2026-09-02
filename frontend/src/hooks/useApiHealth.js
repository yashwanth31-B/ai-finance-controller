import { useState, useEffect, useCallback } from 'react';
import { getHealthStatus, getRootInfo } from '../services/api';

export const useApiHealth = (pollIntervalMs = 15000) => {
  const [status, setStatus] = useState('checking'); // 'checking' | 'healthy' | 'unhealthy' | 'offline'
  const [appInfo, setAppInfo] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);

  const checkHealth = useCallback(async () => {
    try {
      const [rootData, healthData] = await Promise.all([
        getRootInfo(),
        getHealthStatus()
      ]);

      if (healthData.status === 'healthy' && rootData.status === 'running') {
        setStatus('healthy');
        setAppInfo(rootData);
        setError(null);
      } else {
        setStatus('unhealthy');
        setError('Backend reported degraded health status');
      }
    } catch (err) {
      setStatus('offline');
      setError(err.message || 'Unable to connect to backend server');
    } finally {
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    checkHealth();
    if (pollIntervalMs > 0) {
      const interval = setInterval(checkHealth, pollIntervalMs);
      return () => clearInterval(interval);
    }
  }, [checkHealth, pollIntervalMs]);

  return {
    status,
    appInfo,
    lastChecked,
    error,
    refresh: checkHealth
  };
};

export default useApiHealth;

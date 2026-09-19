/**
 * Application Configuration Module
 * Loads Base URLs, Timeouts, and Metadata from configuration (.env / environment variables)
 * Zero hardcoded endpoints.
 */

const getBackendUrl = () => {
  const envUrl = import.meta.env.VITE_BACKEND_URL;
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  return 'http://127.0.0.1:8000';
};

const getApiBaseUrl = () => {
  const envApiUrl = import.meta.env.VITE_API_BASE_URL;
  if (envApiUrl && envApiUrl.trim()) {
    return envApiUrl.trim().replace(/\/+$/, '');
  }
  return '/api/v1';
};

const config = {
  appName: import.meta.env.VITE_APP_NAME || 'DocVerify AI',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  backendUrl: getBackendUrl(),
  apiBaseUrl: getApiBaseUrl(),
  timeoutMs: Number(import.meta.env.VITE_API_TIMEOUT_MS) || 60000,
  
  // Helper to extract port from backend URL
  get backendPort() {
    try {
      const url = new URL(this.backendUrl);
      return url.port || (url.protocol === 'https:' ? '443' : '80');
    } catch {
      return '8000';
    }
  },
  
  // Fully qualified health check endpoint
  get healthUrl() {
    // If apiBaseUrl is relative, use backendUrl as base
    if (this.apiBaseUrl.startsWith('http://') || this.apiBaseUrl.startsWith('https://')) {
      return `${this.apiBaseUrl}/health`;
    }
    return `${this.backendUrl}/api/v1/health`;
  }
};

export default config;

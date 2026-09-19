import axios from 'axios';
import config from '../config';

// Create API client using dynamic base URL from configuration file
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.timeoutMs,
});

export const configApi = {
  getDefaults: (docType) => apiClient.get(`/config/defaults?doc_type=${docType}`),
  getFactoryDefaults: (docType) => apiClient.get(`/config/factory-defaults?doc_type=${docType}`),
  saveConfig: (docType, cfg) => apiClient.post('/config/save', { doc_type: docType, config: cfg }),
  resetConfig: (docType) => apiClient.post(`/config/reset?doc_type=${docType}`),
};

export const verifyApi = {
  verifySingle: (formData) => apiClient.post('/verify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  verifyBulk: (formData) => apiClient.post('/verify/bulk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export const ocrApi = {
  extractOcr: (formData) => apiClient.post('/ocr/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getEngines: () => apiClient.get('/ocr/engines'),
};

export const systemApi = {
  checkHealth: () =>
    axios
      .get(config.healthUrl, { timeout: 10000 })
      .then((r) => r.data)
      .catch(() => null),
};

export default apiClient;

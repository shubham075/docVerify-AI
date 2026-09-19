/**
 * DocVerify AI - JavaScript / Node.js Integration Client
 * Utility client to integrate document quality verification and OCR extraction into other Node.js / Web projects.
 *
 * Usage:
 *   const { DocVerifyClient } = require('./docVerifyClient');
 *   // or: import { DocVerifyClient } from './docVerifyClient.js';
 *
 *   const client = new DocVerifyClient({ baseURL: 'http://localhost:8000' });
 *   const result = await client.verifyDocument(fs.createReadStream('passport.jpg'), 'id_passport');
 *   console.log(result.status, result.stages.ocr.extracted_fields);
 */

const axios = require('axios');
const FormData = require('form-data');

class DocVerifyClient {
  constructor(options = {}) {
    const envBaseUrl = typeof process !== 'undefined' && process.env ? process.env.DOCVERIFY_BASE_URL : null;
    this.baseURL = (options.baseURL || envBaseUrl || 'http://127.0.0.1:8000').replace(/\/$/, '');
    this.apiV1 = `${this.baseURL}/api/v1`;
    this.timeout = options.timeout || 60000;
  }

  async healthCheck() {
    const response = await axios.get(`${this.apiV1}/health`, { timeout: this.timeout });
    return response.data;
  }

  /**
   * Get supported OCR engines and host availability.
   */
  async getOcrEngines() {
    const response = await axios.get(`${this.apiV1}/ocr/engines`, { timeout: this.timeout });
    return response.data;
  }

  /**
   * Verify document quality (Sanity, Glare, Boundary, Sharpness, OCR).
   * @param {Blob|Buffer|ReadableStream} file - File buffer, stream, or blob.
   * @param {string} docType - 'general' or 'id_passport'
   * @param {object} [configOverrides] - Optional threshold overrides
   * @param {string} [filename='document.png'] - Optional filename
   * @param {string} [ocrEngine] - Optional OCR engine ('auto', 'tesseract', 'doctr', 'paddleocr')
   */
  async verifyDocument(file, docType = 'id_passport', configOverrides = null, filename = 'document.png', ocrEngine = null) {
    const form = new FormData();
    form.append('file', file, filename);
    form.append('doc_type', docType);

    const overrides = configOverrides ? { ...configOverrides } : {};
    if (ocrEngine) {
      overrides.ocr_engine = ocrEngine;
    }

    if (Object.keys(overrides).length > 0) {
      form.append('config', JSON.stringify(overrides));
    }

    const headers = typeof form.getHeaders === 'function' ? form.getHeaders() : {};
    const response = await axios.post(`${this.apiV1}/verify`, form, {
      headers,
      timeout: this.timeout,
    });
    return response.data;
  }

  /**
   * Standalone OCR data and structured entity extraction (bypasses blur gating).
   * @param {Blob|Buffer|ReadableStream} file
   * @param {string} docType - 'general' or 'id_passport'
   * @param {number} [confidenceThreshold=75]
   * @param {string} [filename='document.png']
   * @param {string} [ocrEngine='auto']
   */
  async extractOcr(file, docType = 'id_passport', confidenceThreshold = 75, filename = 'document.png', ocrEngine = 'auto') {
    const form = new FormData();
    form.append('file', file, filename);
    form.append('doc_type', docType);
    form.append('confidence_threshold', String(confidenceThreshold));
    form.append('ocr_engine', ocrEngine);

    const headers = typeof form.getHeaders === 'function' ? form.getHeaders() : {};
    const response = await axios.post(`${this.apiV1}/ocr/extract`, form, {
      headers,
      timeout: this.timeout,
    });
    return response.data;
  }
}

module.exports = { DocVerifyClient };

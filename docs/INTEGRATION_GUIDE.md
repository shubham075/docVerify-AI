# DocVerify AI — External Projects Integration Guide

This guide explains how external projects (in Python, Node.js, Go, Java, C#, or bash) can integrate with this service as a standalone microservice utility.

---

## 1. Architecture Overview

DocVerify AI operates as an internal microservice providing document image quality validation, blur detection, glare masking, and OCR entity extraction.

```
┌───────────────────────────────────────────────────────────┐
│                  External Client Projects                 │
│    (Python App, Node.js Backend, Go Service, Mobile API)  │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP / REST (Multipart Form)
                              ▼
┌───────────────────────────────────────────────────────────┐
│              DocVerify AI Microservice (Port 8000)        │
│                                                           │
│  • GET  /api/v1/health          (Liveness probe)          │
│  • POST /api/v1/verify          (Full CV Quality + OCR)   │
│  • POST /api/v1/verify/bulk     (Parallel batch verify)   │
│  • POST /api/v1/ocr/extract     (Standalone OCR parsing)  │
│  • GET  /api/v1/config/defaults (Active configurations)   │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Quick Deployment (Docker)

To run DocVerify AI as an independent background service across your infrastructure:

```bash
# Clone or navigate to the repository
git clone <repo-url> docverify && cd docverify

# Launch backend and UI with Docker Compose
docker compose up -d

# Verify service health
curl http://localhost:8000/api/v1/health
```

The service is accessible at `http://localhost:8000` (API) and `http://localhost:5173` (Admin UI).

---

## 3. Endpoints Reference

### 1. `POST /api/v1/verify` (Full Quality Pipeline + OCR)
Performs complete quality screening (Sanity, Glare, Boundary Rectification, Tiled Sharpness, OCR).

* **Method**: `POST`
* **Content-Type**: `multipart/form-data`
* **Parameters**:
  * `file` (File, required): The document image or PDF (JPG, PNG, PDF, TIFF, WEBP).
  * `doc_type` (string, required): `"general"` or `"id_passport"`.
  * `config` (string, optional): JSON string of threshold overrides (e.g. `{"enable_ocr": true, "ocr_engine": "paddleocr", "blurry_reject_threshold": 60}`).

* **Response Example**:
```json
{
  "status": "PASS",
  "final_reason": "Document passed all verification stages.",
  "stages": {
    "sanity": { "status": "pass", "resolution_px": 1600, "brightness": 199.7 },
    "boundary_detection": { "status": "pass", "confidence": 0.0, "fallback_used": true },
    "glare": { "status": "pass", "glare_area_pct": 0.51 },
    "sharpness": { "status": "pass", "score": 103.26, "anisotropy_ratio": 0.999 },
    "ocr": {
      "status": "pass",
      "engine": "tesseract",
      "engine_label": "Tesseract OCR",
      "requested_engine": "paddleocr",
      "warning": "Requested OCR engine 'PaddleOCR' is not currently available on the host. Gracefully fell back to 'Tesseract OCR'.",
      "avg_word_confidence": 83.43,
      "total_words": 51,
      "raw_text": "OFFICIAL IDENTITY CARD...",
      "extracted_fields": {
        "full_name": "EMMA WATSON",
        "document_number": "P00000189A",
        "nationality": "UTOPIA",
        "dates_found": ["14 APR 1988", "28 OCT 2032"]
      },
      "fields_validated": ["document_number", "dates", "full_name"]
    }
  },
  "filename": "passport.jpg"
}
```

---

### 2. `POST /api/v1/ocr/extract` (Standalone OCR & Entities)
Bypasses blur/glare gating to extract raw text and structured fields immediately with your choice of OCR engine.

* **Method**: `POST`
* **Content-Type**: `multipart/form-data`
* **Parameters**:
  * `file` (File, required)
  * `doc_type` (string, default `"id_passport"`): `"general"` or `"id_passport"`.
  * `confidence_threshold` (int, default `75`): Word confidence pass threshold.
  * `ocr_engine` (string, default `"auto"`): `"auto"`, `"tesseract"`, `"doctr"`, or `"paddleocr"`.

* **Response Example**:
```json
{
  "status": "pass",
  "engine": "tesseract",
  "engine_label": "Tesseract OCR",
  "requested_engine": "doctr",
  "warning": "Requested OCR engine 'docTR (Mindee)' is not currently available on the host. Gracefully fell back to 'Tesseract OCR'.",
  "avg_word_confidence": 83.43,
  "total_words": 51,
  "raw_text": "SURNAME: WATSON\nGIVEN NAMES: EMMA...",
  "extracted_fields": {
    "full_name": "EMMA WATSON",
    "document_number": "P00000189A",
    "nationality": "UTOPIA",
    "dates_found": ["14 APR 1988", "28 OCT 2032"],
    "mrz": {
      "format": "TD3 (Passport)",
      "document_number": "P00000189",
      "date_of_birth": "880414",
      "expiry_date": "321028"
    }
  }
}
```

---

### 3. `GET /api/v1/ocr/engines` (OCR Engine Discovery)
Lists all supported OCR engines, descriptions, and host environment availability.

* **Method**: `GET`
* **Response Example**:
```json
[
  {
    "id": "auto",
    "label": "Auto-Detect (Best Available)",
    "description": "Automatically routes to doctr or PaddleOCR if available, gracefully falling back to Tesseract.",
    "available": true,
    "is_default": true
  },
  {
    "id": "tesseract",
    "label": "Tesseract OCR",
    "description": "Fast, deterministic C++ binary engine with Leptonica preprocessing.",
    "available": true,
    "is_default": false
  },
  {
    "id": "doctr",
    "label": "docTR (Mindee)",
    "description": "Deep-learning end-to-end OCR (DBNet + CRNN) with high layout and multi-font accuracy.",
    "available": false,
    "is_default": false
  },
  {
    "id": "paddleocr",
    "label": "PaddleOCR",
    "description": "Ultra-lightweight and high-precision PP-OCRv4 with angle classification and multilingual support.",
    "available": false,
    "is_default": false
  }
]
```

---

### 4. `POST /api/v1/verify/bulk` (Parallel Batch Analysis)
Upload up to 50 documents simultaneously for asynchronous process-pool execution.

---

## 4. Drop-in Client Code Snippets

### Python
Copy [clients/python/doc_verify_client.py](file:///d:/CODES/DOC_BLURINESS/clients/python/doc_verify_client.py) into your project:

```python
from doc_verify_client import DocVerifyClient

client = DocVerifyClient(base_url="http://localhost:8000")

# 0. Check Available OCR Engines
engines = client.get_ocr_engines()
print("Available OCR engines:", [e["id"] for e in engines if e["available"]])

# 1. Quality & Blur Verification (with specific OCR engine selection)
res = client.verify_document("passport.jpg", doc_type="id_passport", ocr_engine="auto")
if res["status"] == "PASS":
    ocr_stage = res["stages"]["ocr"]
    print(f"Verified via {ocr_stage.get('engine')}: {ocr_stage['extracted_fields'].get('full_name')}")
    if ocr_stage.get("warning"):
        print(f"Engine notice: {ocr_stage['warning']}")
else:
    print(f"Rejected: {res['final_reason']}")

# 2. Standalone OCR Extraction (Choose docTR, PaddleOCR, or Tesseract)
ocr_data = client.extract_ocr("invoice.pdf", doc_type="general", ocr_engine="doctr")
print("Engine:", ocr_data.get("engine"), "Total words:", ocr_data["total_words"])
print(ocr_data["raw_text"])
```

### Node.js / JavaScript
Copy [clients/javascript/docVerifyClient.js](file:///d:/CODES/DOC_BLURINESS/clients/javascript/docVerifyClient.js) into your project:

```javascript
const fs = require('fs');
const { DocVerifyClient } = require('./docVerifyClient');

const client = new DocVerifyClient({ baseURL: 'http://localhost:8000' });

async function verify() {
  // Query supported OCR engines
  const engines = await client.getOcrEngines();
  console.log('Supported engines:', engines);

  // Verify document with specific OCR engine
  const fileStream = fs.createReadStream('id_card.png');
  const result = await client.verifyDocument(fileStream, 'id_passport', null, 'id_card.png', 'paddleocr');
  
  if (result.status === 'PASS') {
    console.log('Document valid. Engine:', result.stages.ocr.engine);
    console.log('Extracted data:', result.stages.ocr.extracted_fields);
    if (result.stages.ocr.warning) console.warn(result.stages.ocr.warning);
  } else {
    console.log('Document rejected:', result.final_reason);
  }
}
verify();
```

### cURL
```bash
# Query available OCR engines
curl -X GET "http://localhost:8000/api/v1/ocr/engines"

# Verify an ID card with auto engine selection
curl -X POST "http://localhost:8000/api/v1/verify" \
  -F "file=@id_card.png" \
  -F "doc_type=id_passport" \
  -F 'config={"ocr_engine":"auto"}'

# Extract OCR only using paddleocr or doctr
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -F "file=@invoice.png" \
  -F "doc_type=general" \
  -F "ocr_engine=paddleocr"
```

---

## 5. Configuration Files & Environment Variables

DocVerify AI is fully config-driven. **No endpoints or URLs are hardcoded in code files.**

### Backend Configuration (`backend/.env`)

Located at [backend/.env](file:///d:/CODES/DOC_BLURINESS/backend/.env) (with template at [backend/.env.example](file:///d:/CODES/DOC_BLURINESS/backend/.env.example)):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `BASE_URL` | `http://127.0.0.1:8000` | Public base URL of the microservice (used in docs, responses, self-reference) |
| `HOST` | `127.0.0.1` | Network interface to bind the uvicorn server |
| `PORT` | `8000` | Network port to listen on |
| `API_V1_STR` | `/api/v1` | Base route prefix for API endpoints |
| `CORS_ORIGINS` | `["http://localhost:5173", "*"]` | Permitted CORS origins (comma-separated or JSON list) |
| `PROJECT_NAME` | `DocVerify AI` | Service name in OpenAPI documentation and health payloads |
| `MAX_SINGLE_FILE_SIZE_MB` | `15` | Max individual file upload size limit |
| `MAX_FILES_PER_BULK_UPLOAD` | `25` | Maximum number of files in a bulk batch request |
| `TEMP_UPLOAD_DIR` | `temp_uploads` | Scratch directory for multipart file processing |

### Frontend Configuration (`frontend/.env`)

Located at [frontend/.env](file:///d:/CODES/DOC_BLURINESS/frontend/.env) (with template at [frontend/.env.example](file:///d:/CODES/DOC_BLURINESS/frontend/.env.example)):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VITE_BACKEND_URL` | `http://127.0.0.1:8000` | Target backend host URL for Vite proxy and direct health checks |
| `VITE_API_BASE_URL` | `/api/v1` | Relative API path (for reverse proxy) or absolute `http://.../api/v1` |
| `VITE_PORT` | `5173` | Vite local development server port |
| `VITE_API_TIMEOUT_MS` | `60000` | Global Axios request timeout in milliseconds |
| `VITE_APP_NAME` | `DocVerify AI` | UI application title |
| `VITE_APP_VERSION` | `1.0.0` | Application release version |

### External Client SDK Base URL Override

External Python and Node.js integrations can override the base URL either via constructor argument or globally via the `DOCVERIFY_BASE_URL` environment variable:

```bash
# Set in external application's environment
export DOCVERIFY_BASE_URL="http://docverify.internal:8000"
```
```python
# Python client will automatically use DOCVERIFY_BASE_URL if no base_url argument is given:
client = DocVerifyClient()
```


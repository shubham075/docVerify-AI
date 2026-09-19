#!/usr/bin/env bash
# DocVerify AI - cURL Integration Examples
# Ready-to-use API calls for bash scripts, microservices, and CI/CD pipelines

API_BASE="http://localhost:8000/api/v1"

echo "=== 1. Health Check ==="
curl -s "$API_BASE/health" | jq .

echo -e "\n=== 2. Full Quality Verification (ID / Passport) ==="
curl -s -X POST "$API_BASE/verify" \
  -F "file=@backend/tests/fixtures/test_dataset_100/id_passport/id_passport_001.png" \
  -F "doc_type=id_passport" | jq .

echo -e "\n=== 3. Quality Verification with Custom Overrides ==="
curl -s -X POST "$API_BASE/verify" \
  -F "file=@backend/sharp_test.png" \
  -F "doc_type=id_passport" \
  -F 'config={"enable_brightness_check": false, "enable_ocr": true}' | jq .

echo -e "\n=== 4. Standalone OCR & Entity Extraction (No Blur Gating) ==="
curl -s -X POST "$API_BASE/ocr/extract" \
  -F "file=@backend/tests/fixtures/test_dataset_100/id_passport/id_passport_001.png" \
  -F "doc_type=id_passport" | jq .

echo -e "\n=== 5. Bulk Verification ==="
curl -s -X POST "$API_BASE/verify/bulk" \
  -F "files=@backend/tests/fixtures/test_dataset_100/id_passport/id_passport_001.png" \
  -F "files=@backend/tests/fixtures/test_dataset_100/id_passport/id_passport_002.png" \
  -F "doc_type=id_passport" | jq .

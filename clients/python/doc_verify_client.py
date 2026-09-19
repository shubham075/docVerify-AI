"""
DocVerify AI - Python Integration Client
Utility client to integrate document quality verification and OCR extraction into other Python projects.

Usage:
    from doc_verify_client import DocVerifyClient

    client = DocVerifyClient(base_url="http://localhost:8000")
    
    # 1. Full document verification (blur, glare, resolution, sharpness + OCR)
    result = client.verify_document("passport.jpg", doc_type="id_passport")
    if result["status"] == "PASS":
        print("Verified!", result["stages"]["ocr"]["extracted_fields"])
    else:
        print("Rejected:", result["final_reason"])

    # 2. Standalone OCR & Entity Extraction (bypass blur checks)
    ocr_data = client.extract_ocr("invoice.pdf", doc_type="general")
    print("Extracted text:", ocr_data["raw_text"])
"""

import os
import requests
import json
from typing import Dict, Any, Optional, Union, List, BinaryIO
from pathlib import Path


class DocVerifyClient:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 60):
        # Read from parameter or DOCVERIFY_BASE_URL env variable, default to 127.0.0.1:8000
        resolved_url = base_url or os.environ.get("DOCVERIFY_BASE_URL", "http://127.0.0.1:8000")
        self.base_url = resolved_url.rstrip("/")
        self.api_v1 = f"{self.base_url}/api/v1"
        self.timeout = timeout

    def health_check(self) -> Dict[str, Any]:
        """Checks if the DocVerify AI microservice is healthy."""
        res = requests.get(f"{self.api_v1}/health", timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    def get_ocr_engines(self) -> Dict[str, Any]:
        """Returns list of supported OCR engines (Tesseract, docTR, PaddleOCR) and host availability."""
        res = requests.get(f"{self.api_v1}/ocr/engines", timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    def verify_document(
        self,
        file_path_or_bytes: Union[str, Path, BinaryIO],
        doc_type: str = "id_passport",
        config_overrides: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        ocr_engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs quality verification (Sanity, Glare, Boundary, Tiled Sharpness, OCR).
        
        Args:
            file_path_or_bytes: Path to file or binary file-like object.
            doc_type: 'general' or 'id_passport'.
            config_overrides: Optional dictionary to override pipeline parameters.
            filename: Optional filename if passing bytes.
            ocr_engine: Optional OCR engine ('auto', 'tesseract', 'doctr', 'paddleocr').
        """
        files = self._prepare_files(file_path_or_bytes, filename)
        data: Dict[str, Any] = {"doc_type": doc_type}

        overrides = dict(config_overrides) if config_overrides else {}
        if ocr_engine:
            overrides["ocr_engine"] = ocr_engine

        if overrides:
            data["config"] = json.dumps(overrides)

        res = requests.post(f"{self.api_v1}/verify", files=files, data=data, timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    def verify_bulk(
        self,
        file_paths: List[Union[str, Path]],
        doc_type: str = "id_passport",
        config_overrides: Optional[Dict[str, Any]] = None,
        ocr_engine: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Runs parallel quality verification across multiple files."""
        files = []
        for path in file_paths:
            p = Path(path)
            files.append(("files", (p.name, open(p, "rb"))))

        data: Dict[str, Any] = {"doc_type": doc_type}
        overrides = dict(config_overrides) if config_overrides else {}
        if ocr_engine:
            overrides["ocr_engine"] = ocr_engine

        if overrides:
            data["config"] = json.dumps(overrides)

        try:
            res = requests.post(f"{self.api_v1}/verify/bulk", files=files, data=data, timeout=self.timeout)
            res.raise_for_status()
            return res.json()
        finally:
            for _, (_, f) in files:
                f.close()

    def extract_ocr(
        self,
        file_path_or_bytes: Union[str, Path, BinaryIO],
        doc_type: str = "id_passport",
        confidence_threshold: int = 75,
        filename: Optional[str] = None,
        ocr_engine: str = "auto"
    ) -> Dict[str, Any]:
        """
        Direct OCR extraction endpoint (bypasses blur gating).
        Returns raw text, word count, confidence, and structured entities (names, dates, MRZ).
        
        Args:
            ocr_engine: 'auto', 'tesseract', 'doctr', or 'paddleocr'.
        """
        files = self._prepare_files(file_path_or_bytes, filename)
        data = {
            "doc_type": doc_type,
            "confidence_threshold": str(confidence_threshold),
            "ocr_engine": ocr_engine
        }
        res = requests.post(f"{self.api_v1}/ocr/extract", files=files, data=data, timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    def _prepare_files(self, file_path_or_bytes, filename):
        if isinstance(file_path_or_bytes, (str, Path)):
            p = Path(file_path_or_bytes)
            name = filename or p.name
            return {"file": (name, open(p, "rb"))}
        else:
            name = filename or "document.png"
            return {"file": (name, file_path_or_bytes)}


if __name__ == "__main__":
    # Self-test example
    client = DocVerifyClient()
    try:
        health = client.health_check()
        print("Connected to DocVerify Microservice:", health)
    except Exception as e:
        print("Could not connect:", e)

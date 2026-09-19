import cv2
import numpy as np
from typing import Dict, Any
from app.services.pipeline.general_doc.pipeline import run_general_doc_pipeline
from app.services.pipeline.id_passport.pipeline import run_id_passport_pipeline
from app.services.pipeline.ocr.engine import run_ocr_confidence

def run_pipeline_orchestrator(image: np.ndarray, doc_type: str, config) -> Dict[str, Any]:
    """
    Routes the image to the correct pipeline and runs all active stages.
    OCR is an independent inspection stage with an explicit on/off toggle (not a fallback).
    """
    # 1. Route to primary document pipeline (Sanity, Boundary, Glare, Sharpness)
    if doc_type == "id_passport":
        result = run_id_passport_pipeline(image, config)
    else:
        result = run_general_doc_pipeline(image, config)

    # If the document has already been rejected by an earlier active stage, return early
    if result.get("status") == "REJECT":
        return result

    # 2. OCR Verification Stage (Standard independent check, not a fallback)
    if getattr(config, "enable_ocr", False):
        ocr_engine_choice = getattr(config, "ocr_engine", "auto")
        ocr_res = run_ocr_confidence(image, doc_type, config, ocr_engine=ocr_engine_choice)
        result["stages"]["ocr"] = ocr_res

        if ocr_res.get("status") == "fail":
            result["status"] = "REJECT"
            result["final_reason"] = f"OCR confidence below threshold: {ocr_res.get('avg_word_confidence', 0.0):.1f}% < {config.ocr_confidence_threshold}%"
        elif ocr_res.get("status") == "pass":
            if result.get("status") == "BORDERLINE":
                result["status"] = "PASS"
                result["final_reason"] = "Sharpness borderline, but OCR confidence passed."
            else:
                result["final_reason"] = "Document passed all verification stages."
        elif ocr_res.get("status") == "unavailable":
            if result.get("status") == "BORDERLINE":
                result["final_reason"] = "Sharpness borderline (OCR engine unavailable on host)."
    else:
        result["stages"]["ocr"] = {
            "status": "skipped",
            "reason": "OCR check disabled"
        }

    return result

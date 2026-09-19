import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from app.services.pipeline.ocr.base import BaseOCREngine, OCREngineResult
from app.services.pipeline.ocr.tesseract_engine import TesseractEngine
from app.services.pipeline.ocr.doctr_engine import DocTrEngine
from app.services.pipeline.ocr.paddle_engine import PaddleOCREngine
from app.services.pipeline.ocr.extractor import OCREntityExtractor

# Engine Singletons
_tesseract_engine = TesseractEngine()
_doctr_engine = DocTrEngine()
_paddle_engine = PaddleOCREngine()

_REGISTRY: Dict[str, BaseOCREngine] = {
    "tesseract": _tesseract_engine,
    "doctr": _doctr_engine,
    "paddleocr": _paddle_engine,
}

def list_ocr_engines() -> List[Dict[str, Any]]:
    """
    Returns the metadata and runtime availability of all registered OCR engines.
    """
    engines_meta = [
        {
            "id": "auto",
            "label": "Auto-Detect (Best Available)",
            "description": "Automatically routes to doctr or PaddleOCR if available, gracefully falling back to Tesseract.",
            "available": True,
            "is_default": True,
        }
    ]

    for engine_id, engine in _REGISTRY.items():
        engines_meta.append({
            "id": engine.name,
            "label": engine.label,
            "description": engine.description,
            "available": engine.is_available(),
            "is_default": False,
        })

    return engines_meta

def get_ocr_engine_availability() -> Dict[str, bool]:
    """Returns a dictionary mapping engine ID to boolean availability."""
    return {k: v.is_available() for k, v in _REGISTRY.items()}

def resolve_ocr_engine(requested_engine: Optional[str] = "auto") -> Tuple[BaseOCREngine, Optional[str]]:
    """
    Resolves the requested OCR engine with graceful fallback support.
    Returns (selected_engine, warning_message_if_any).
    """
    req = (requested_engine or "auto").strip().lower()

    if req == "auto":
        # Auto priority: doctr -> paddleocr -> tesseract
        if _doctr_engine.is_available():
            return _doctr_engine, None
        if _paddle_engine.is_available():
            return _paddle_engine, None
        return _tesseract_engine, None

    if req in _REGISTRY:
        target = _REGISTRY[req]
        if target.is_available():
            return target, None
        
        # Target requested but not available -> Graceful fallback
        # Fallback priority: any available engine, default to Tesseract
        fallback = _tesseract_engine
        if not fallback.is_available():
            for alt in [_doctr_engine, _paddle_engine]:
                if alt.is_available():
                    fallback = alt
                    break

        warning = (
            f"Requested OCR engine '{target.label}' is not currently available on the host. "
            f"Gracefully fell back to '{fallback.label}'."
        )
        return fallback, warning

    # Unknown engine requested
    warning = f"Unknown OCR engine '{req}'. Defaulted to '{_tesseract_engine.label}'."
    return _tesseract_engine, warning


def run_ocr_confidence(
    image: np.ndarray,
    doc_type: str,
    config: Any,
    ocr_engine: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes OCR inspection using the chosen/auto-detected OCR engine.
    Extracts raw text, word confidence metrics, and structured entities.
    """
    # 1. Determine requested engine from call arg or config object
    target_engine_name = ocr_engine or getattr(config, "ocr_engine", "auto")
    engine, fallback_warning = resolve_ocr_engine(target_engine_name)

    if not engine.is_available():
        return {
            "status": "unavailable",
            "engine": engine.name,
            "requested_engine": target_engine_name,
            "reason": f"No OCR engine is operational on host. Please install Tesseract, doctr, or paddleocr.",
            "warning": fallback_warning,
            "avg_word_confidence": 0.0,
            "total_words": 0,
            "raw_text": "",
            "extracted_fields": {},
            "fields_validated": []
        }

    try:
        # 2. Run extraction through selected engine
        result: OCREngineResult = engine.extract(image, config)
        raw_text = result.raw_text
        avg_conf = result.avg_word_confidence
        word_count = result.total_words

        # 3. Determine pass/fail based on confidence threshold
        threshold = getattr(config, "ocr_confidence_threshold", 75.0)
        is_pass = avg_conf >= threshold

        # 4. Extract structured entities (MRZ, dates, emails, phones, amounts, document numbers)
        extracted_fields = OCREntityExtractor.extract_structured_fields(raw_text, doc_type)

        fields_validated = []
        if "mrz" in extracted_fields:
            fields_validated.append("MRZ")
        if "document_number" in extracted_fields or "document_number_candidate" in extracted_fields:
            fields_validated.append("document_number")
        if "dates_found" in extracted_fields:
            fields_validated.append("dates")
        if "full_name" in extracted_fields:
            fields_validated.append("full_name")
        if "amounts_found" in extracted_fields:
            fields_validated.append("amounts")

        final_warning = fallback_warning or result.warning

        return {
            "status": "pass" if is_pass else "fail",
            "engine": engine.name,
            "engine_label": engine.label,
            "requested_engine": target_engine_name,
            "warning": final_warning,
            "avg_word_confidence": round(avg_conf, 2),
            "total_words": word_count,
            "raw_text": raw_text,
            "extracted_fields": extracted_fields,
            "fields_validated": fields_validated,
            "words": result.words[:50]  # sample of first 50 words with boxes
        }

    except Exception as e:
        return {
            "status": "unavailable",
            "engine": engine.name,
            "requested_engine": target_engine_name,
            "reason": f"OCR execution failed: {str(e)}",
            "warning": fallback_warning,
            "avg_word_confidence": 0.0,
            "total_words": 0,
            "raw_text": "",
            "extracted_fields": {},
            "fields_validated": []
        }

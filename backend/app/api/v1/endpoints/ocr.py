from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
from app.services.file_validation import validate_file
from app.utils.image_io import load_image_from_upload
from app.services.pipeline.ocr.engine import run_ocr_confidence, list_ocr_engines
from app.schemas.pipeline_config import get_ideal_defaults

router = APIRouter()

@router.get("/engines", response_model=List[Dict[str, Any]])
async def get_ocr_engines():
    """
    List all supported OCR engine providers (Tesseract, docTR, PaddleOCR, Auto),
    including their availability status on the host system.
    """
    return list_ocr_engines()

@router.post("/extract")
async def extract_ocr_endpoint(
    file: UploadFile = File(...),
    doc_type: str = Form("id_passport"),
    ocr_engine: Optional[str] = Form("auto"),
    confidence_threshold: Optional[int] = Form(75)
):
    """
    Dedicated OCR extraction endpoint for external project integrations.
    Supports dynamic engine selection ('auto', 'tesseract', 'doctr', 'paddleocr').
    Returns full raw extracted text, word confidence, structured entity fields, and engine diagnostics.
    """
    if doc_type not in ["general", "id_passport"]:
        raise HTTPException(status_code=400, detail="Invalid doc_type. Must be 'general' or 'id_passport'")

    # 1. Validate file format / mime
    is_valid, reason = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"reason": reason, "filename": file.filename})

    # 2. Load image
    image = await load_image_from_upload(file)

    # 3. Create config with requested confidence threshold & engine
    cfg = get_ideal_defaults(doc_type)
    if confidence_threshold is not None:
        cfg.ocr_confidence_threshold = confidence_threshold
    if ocr_engine:
        cfg.ocr_engine = ocr_engine

    # 4. Run OCR extraction with chosen engine
    ocr_result = run_ocr_confidence(image, doc_type, cfg, ocr_engine=ocr_engine)
    ocr_result["filename"] = file.filename
    ocr_result["doc_type"] = doc_type

    return ocr_result

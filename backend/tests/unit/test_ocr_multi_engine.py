import numpy as np
import pytest
from app.services.pipeline.ocr.engine import (
    list_ocr_engines,
    resolve_ocr_engine,
    run_ocr_confidence,
    get_ocr_engine_availability
)
from app.schemas.pipeline_config import get_ideal_defaults

def test_list_ocr_engines():
    engines = list_ocr_engines()
    ids = [e["id"] for e in engines]
    assert "auto" in ids
    assert "tesseract" in ids
    assert "doctr" in ids
    assert "paddleocr" in ids

def test_engine_availability_map():
    avail = get_ocr_engine_availability()
    assert "tesseract" in avail
    assert "doctr" in avail
    assert "paddleocr" in avail
    # Tesseract binary is installed and configured on host
    assert avail["tesseract"] is True

def test_resolve_engine_auto():
    engine, warning = resolve_ocr_engine("auto")
    assert engine is not None
    assert engine.is_available() is True
    assert warning is None

def test_resolve_engine_tesseract():
    engine, warning = resolve_ocr_engine("tesseract")
    assert engine.name == "tesseract"
    assert warning is None

def test_resolve_engine_fallback_when_unavailable():
    # If doctr or paddleocr are not installed, test graceful fallback
    avail = get_ocr_engine_availability()
    if not avail["doctr"]:
        engine, warning = resolve_ocr_engine("doctr")
        assert engine is not None
        assert engine.is_available() is True
        assert warning is not None
        assert "not currently available" in warning

def test_run_ocr_confidence_execution():
    # Create clean synthetic image with simple white canvas
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    cfg = get_ideal_defaults("general")
    cfg.ocr_engine = "auto"

    res = run_ocr_confidence(img, "general", cfg)
    assert "status" in res
    assert "engine" in res
    assert "raw_text" in res
    assert "avg_word_confidence" in res

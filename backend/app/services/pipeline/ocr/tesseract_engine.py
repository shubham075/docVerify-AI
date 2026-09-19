import os
import shutil
import pytesseract
import numpy as np
import cv2
from typing import Any, List, Dict
from app.services.pipeline.ocr.base import BaseOCREngine, OCREngineResult

class TesseractEngine(BaseOCREngine):
    """
    Tesseract OCR Engine Provider (CPU native binary).
    """

    def __init__(self):
        self._configured = False
        self._configure_binary()

    def _configure_binary(self):
        if shutil.which("tesseract"):
            self._configured = True
            return

        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                pytesseract.pytesseract.tesseract_cmd = cand
                tessdata = os.path.join(os.path.dirname(cand), "tessdata")
                if os.path.exists(tessdata) and "TESSDATA_PREFIX" not in os.environ:
                    os.environ["TESSDATA_PREFIX"] = tessdata
                self._configured = True
                break

    @property
    def name(self) -> str:
        return "tesseract"

    @property
    def label(self) -> str:
        return "Tesseract OCR"

    @property
    def description(self) -> str:
        return "Fast, deterministic C++ binary engine with Leptonica preprocessing."

    def is_available(self) -> bool:
        if not self._configured:
            self._configure_binary()
        return self._configured or shutil.which("tesseract") is not None

    def extract(self, image: np.ndarray, config: Any = None) -> OCREngineResult:
        if not self.is_available():
            raise RuntimeError("Tesseract OCR binary not found on host system.")

        # Grayscale & Adaptive thresholding for optimal OCR binarization
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Word-level detail and bounding boxes
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)

        words_list = []
        valid_confidences = []
        for i, (conf, text) in enumerate(zip(data.get('conf', []), data.get('text', []))):
            cleaned = text.strip()
            if str(conf) != '-1' and cleaned:
                conf_val = float(conf)
                valid_confidences.append(conf_val)
                words_list.append({
                    "text": cleaned,
                    "confidence": conf_val,
                    "box": [
                        data['left'][i],
                        data['top'][i],
                        data['left'][i] + data['width'][i],
                        data['top'][i] + data['height'][i]
                    ]
                })

        raw_text = pytesseract.image_to_string(thresh).strip()
        if not raw_text:
            raw_text = pytesseract.image_to_string(image).strip()

        avg_conf = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0

        return OCREngineResult(
            engine=self.name,
            raw_text=raw_text,
            avg_word_confidence=float(avg_conf),
            total_words=len(valid_confidences),
            words=words_list,
            lines=[l for l in raw_text.split('\n') if l.strip()]
        )

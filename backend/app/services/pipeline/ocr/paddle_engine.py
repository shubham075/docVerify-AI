import cv2
import numpy as np
from typing import Any, List, Dict, Optional
from app.services.pipeline.ocr.base import BaseOCREngine, OCREngineResult

class PaddleOCREngine(BaseOCREngine):
    """
    Baidu PaddleOCR Engine Provider.
    High-accuracy PP-OCRv4 pipeline with direction angle classification and robust multilingual support.
    Supports both rapidocr-onnxruntime (ONNX Runtime PP-OCRv4) and native paddleocr.
    """

    def __init__(self):
        self._ocr = None
        self._backend = None
        self._available = None

    @property
    def name(self) -> str:
        return "paddleocr"

    @property
    def label(self) -> str:
        return "PaddleOCR"

    @property
    def description(self) -> str:
        return "Ultra-lightweight and high-precision PP-OCRv4 with angle classification and multilingual support."

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            from rapidocr_onnxruntime import RapidOCR  # noqa: F401
            self._backend = "rapidocr"
            self._available = True
            return True
        except ImportError:
            pass

        try:
            from paddleocr import PaddleOCR  # noqa: F401
            self._backend = "paddleocr"
            self._available = True
            return True
        except Exception:
            self._available = False
            return False

    def _get_ocr(self):
        if self._ocr is None:
            if not self.is_available():
                raise RuntimeError(
                    "PaddleOCR is not installed. Install with: pip install rapidocr-onnxruntime or paddleocr."
                )
            if self._backend == "rapidocr":
                from rapidocr_onnxruntime import RapidOCR
                self._ocr = RapidOCR()
            else:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang="en")
        return self._ocr

    def extract(self, image: np.ndarray, config: Any = None) -> OCREngineResult:
        if not self.is_available():
            raise RuntimeError(
                "PaddleOCR is not installed. Please install rapidocr-onnxruntime or select Tesseract."
            )

        ocr_instance = self._get_ocr()
        words_list = []
        confidences = []
        lines_text = []

        if self._backend == "rapidocr":
            # RapidOCR (PP-OCRv4 ONNX) execution
            result, _ = ocr_instance(image)
            if result:
                for item in result:
                    # item format: [box_pts, text, confidence]
                    if len(item) >= 3:
                        box_pts = item[0]
                        text = str(item[1]).strip()
                        conf = float(item[2])
                    elif len(item) == 2:
                        box_pts = item[0]
                        text = str(item[1]).strip()
                        conf = 0.90
                    else:
                        continue

                    if text:
                        conf_pct = conf * 100.0 if conf <= 1.0 else conf
                        confidences.append(conf_pct)
                        lines_text.append(text)

                        try:
                            xs = [p[0] for p in box_pts]
                            ys = [p[1] for p in box_pts]
                            box = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
                        except Exception:
                            box = []

                        words_list.append({
                            "text": text,
                            "confidence": round(conf_pct, 2),
                            "box": box
                        })
        else:
            # Native PaddleOCR execution
            result = ocr_instance.ocr(image, cls=True)
            if result and len(result) > 0:
                page_result = result[0]
                if page_result:
                    for line_item in page_result:
                        if len(line_item) >= 2:
                            box_pts = line_item[0]
                            text_tuple = line_item[1]
                            text = text_tuple[0].strip()
                            conf = float(text_tuple[1])

                            if text:
                                conf_pct = conf * 100.0 if conf <= 1.0 else conf
                                confidences.append(conf_pct)
                                lines_text.append(text)

                                try:
                                    xs = [p[0] for p in box_pts]
                                    ys = [p[1] for p in box_pts]
                                    box = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
                                except Exception:
                                    box = []

                                words_list.append({
                                    "text": text,
                                    "confidence": round(conf_pct, 2),
                                    "box": box
                                })

        raw_text = "\n".join(lines_text).strip()
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        total_words = sum(len(line.split()) for line in lines_text) if lines_text else 0

        return OCREngineResult(
            engine=self.name,
            raw_text=raw_text,
            avg_word_confidence=round(avg_conf, 2),
            total_words=total_words,
            words=words_list,
            lines=lines_text
        )


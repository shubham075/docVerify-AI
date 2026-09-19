import cv2
import numpy as np
from typing import Any, List, Dict, Optional
from app.services.pipeline.ocr.base import BaseOCREngine, OCREngineResult

class DocTrEngine(BaseOCREngine):
    """
    Mindee docTR Deep Learning OCR Engine Provider.
    End-to-end document text detection (e.g. DBNet) and recognition (e.g. CRNN/SAR).
    """

    def __init__(self):
        self._predictor = None
        self._available = None

    @property
    def name(self) -> str:
        return "doctr"

    @property
    def label(self) -> str:
        return "docTR (Mindee)"

    @property
    def description(self) -> str:
        return "Deep-learning end-to-end OCR (DBNet + CRNN) with high layout and multi-font accuracy."

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import doctr  # noqa: F401
            from doctr.models import ocr_predictor  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False
        return self._available

    def _get_predictor(self):
        if self._predictor is None:
            if not self.is_available():
                raise RuntimeError(
                    "docTR is not installed. Install with: pip install \"python-doctr[torch]\" or pip install doctr."
                )
            from doctr.models import ocr_predictor
            # Load pretrained model with CPU execution
            self._predictor = ocr_predictor(pretrained=True)
        return self._predictor

    def extract(self, image: np.ndarray, config: Any = None) -> OCREngineResult:
        if not self.is_available():
            raise RuntimeError(
                "docTR is not installed. Please install python-doctr or select Tesseract."
            )

        predictor = self._get_predictor()

        # docTR expects RGB format
        if len(image.shape) == 2:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        elif image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image

        # Run inference on document image
        result = predictor([rgb_image])

        words_list = []
        confidences = []
        lines_text = []

        h, w = image.shape[:2]

        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_words = []
                    for word in line.words:
                        val = word.value.strip()
                        if val:
                            conf_pct = float(word.confidence * 100.0)
                            confidences.append(conf_pct)
                            line_words.append(val)

                            # word.geometry is relative ((xmin, ymin), (xmax, ymax))
                            geo = word.geometry
                            box = [
                                int(geo[0][0] * w),
                                int(geo[0][1] * h),
                                int(geo[1][0] * w),
                                int(geo[1][1] * h)
                            ]
                            words_list.append({
                                "text": val,
                                "confidence": round(conf_pct, 2),
                                "box": box
                            })
                    if line_words:
                        lines_text.append(" ".join(line_words))

        raw_text = "\n".join(lines_text).strip()
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return OCREngineResult(
            engine=self.name,
            raw_text=raw_text,
            avg_word_confidence=round(avg_conf, 2),
            total_words=len(words_list),
            words=words_list,
            lines=lines_text
        )

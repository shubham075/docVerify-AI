from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class OCREngineResult:
    """Standardized output structure for any OCR engine implementation."""
    engine: str
    raw_text: str
    avg_word_confidence: float
    total_words: int
    words: List[Dict[str, Any]] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)
    warning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseOCREngine(ABC):
    """Abstract interface for all document OCR engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Engine identifier: 'tesseract', 'doctr', 'paddleocr'."""
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        """Human-readable display name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief engine description and technical profile."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the underlying library or binary is installed and operational."""
        pass

    @abstractmethod
    def extract(self, image: np.ndarray, config: Any) -> OCREngineResult:
        """
        Executes text extraction on image.
        Returns standardized OCREngineResult.
        """
        pass

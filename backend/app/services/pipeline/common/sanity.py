import cv2
import numpy as np
from app.core.settings import settings

def check_resolution(image: np.ndarray, min_long_edge: int) -> tuple[bool, int]:
    """
    Checks if the longest edge of the image meets the minimum resolution.
    Returns (is_valid, long_edge_px).
    """
    h, w = image.shape[:2]
    long_edge = max(h, w)
    return long_edge >= min_long_edge, long_edge

def check_brightness(image: np.ndarray, b_min: int, b_max: int) -> tuple[bool, float]:
    """
    Checks if the mean luma of the image is within the allowed range.
    Returns (is_valid, mean_luma).
    """
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    mean_luma = np.mean(gray)
    return (b_min <= mean_luma <= b_max), float(mean_luma)

def canonical_resize(image: np.ndarray, target_width: int) -> np.ndarray:
    """
    Resizes the image to a canonical width while maintaining aspect ratio.
    """
    h, w = image.shape[:2]
    aspect_ratio = h / w
    target_height = int(target_width * aspect_ratio)
    return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)

def apply_denoise(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Applies Gaussian blur to reduce high-frequency noise before gradient calculation.
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

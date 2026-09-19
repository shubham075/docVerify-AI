import cv2
import numpy as np
from typing import Tuple

def run_glare_check(image: np.ndarray, config) -> Tuple[bool, float, str]:
    """
    Checks for excessive glare using HSV thresholding.
    Returns (is_pass, glare_area_pct, reason).
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define Glare: High Value (Brightness) and Low Saturation (Whitish)
    # Value > threshold AND Saturation < threshold
    lower_glare = np.array([0, 0, config.glare_value_threshold])
    upper_glare = np.array([180, config.glare_saturation_threshold, 255])

    mask = cv2.inRange(hsv, lower_glare, upper_glare)
    glare_pixels = cv2.countNonZero(mask)
    total_pixels = image.shape[0] * image.shape[1]

    glare_area_pct = (glare_pixels / total_pixels) * 100.0

    if glare_area_pct > config.glare_max_area_pct:
        return False, glare_area_pct, f"Excessive glare detected: {glare_area_pct:.2f}%"

    return True, glare_area_pct, "success"

def get_glare_mask(image: np.ndarray, config) -> np.ndarray:
    """
    Returns a binary mask of glare pixels to be used for ignoring them during scoring.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_glare = np.array([0, 0, config.glare_value_threshold])
    upper_glare = np.array([180, config.glare_saturation_threshold, 255])
    return cv2.inRange(hsv, lower_glare, upper_glare)

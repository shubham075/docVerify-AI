import cv2
import numpy as np
from typing import Tuple, Optional
from app.services.pipeline.common.sanity import canonical_resize

def detect_boundary(image: np.ndarray, config) -> Tuple[np.ndarray, float, bool]:
    """
    Detects document boundaries and performs perspective rectification.
    Returns (rectified_image, confidence, fallback_used).
    """
    # Preprocessing for contour detection
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return _fallback_center_crop(image, config), 0.0, True

    # Get the largest contour by area
    c = max(contours, key=cv2.contourArea)

    # Approximate the contour to a polygon
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # We need exactly 4 points for a quadrilateral
    if len(approx) == 4:
        # Calculate confidence based on area ratio and "squareness"
        area_doc = cv2.contourArea(approx)
        area_img = image.shape[0] * image.shape[1]
        ratio = area_doc / area_img

        # Simple confidence: ratio should be reasonable (e.g., 0.2 to 0.9)
        confidence = 1.0 if 0.2 <= ratio <= 0.9 else ratio * 2.0 # Rough heuristic

        if confidence >= config.boundary_confidence_threshold:
            rectified = _warp_perspective(image, approx)
            return rectified, confidence, False

    return _fallback_center_crop(image, config), 0.0, True

def _warp_perspective(image: np.ndarray, approx: np.ndarray) -> np.ndarray:
    """
    Warps the image based on detected corners to a canonical ID aspect ratio.
    """
    # Reshape and order points: top-left, top-right, bottom-right, bottom-left
    pts = approx.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")

    # Sort by sum (x+y) for top-left and bottom-right
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # Sort by difference (y-x) for top-right and bottom-left
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # Target dimensions (Canonical ID aspect ratio ~ 1.58 : 1)
    width = 600
    height = int(width / 1.58)
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (width, height))

def _fallback_center_crop(image: np.ndarray, config) -> np.ndarray:
    """
    Fallback: crops the center percentage of the image if needed.
    If the image is already pre-cropped to ID card aspect ratio, preserves full image.
    """
    h, w = image.shape[:2]
    aspect = w / h
    if 1.2 <= aspect <= 1.9:
        return image

    pct = config.fallback_center_crop_pct / 100.0
    start_x = int(w * (1 - pct) / 2)
    start_y = int(h * (1 - pct) / 2)
    end_x = int(start_x + w * pct)
    end_y = int(start_y + h * pct)

    return image[start_y:end_y, start_x:end_x]

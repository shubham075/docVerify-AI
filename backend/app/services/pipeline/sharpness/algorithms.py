import cv2
import numpy as np

def compute_laplacian_score(image: np.ndarray) -> float:
    """
    Computes the variance of the Laplacian, a standard measure of image sharpness.
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(np.var(laplacian))

def compute_tenengrad_score(image: np.ndarray) -> float:
    """
    Computes the Tenengrad gradient magnitude.
    Better for photographed documents as it's more robust to noise.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Sobel operators
    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    # Magnitude = sqrt(sx^2 + sy^2)
    magnitude = np.sqrt(sx**2 + sy**2)
    # Scaled to 0-300 calibration range consistent with pipeline thresholds (PASS > 120, REJECT <= 60)
    return float(np.mean(magnitude) * 10.0)

def compute_anisotropy_ratio(image: np.ndarray) -> float:
    """
    Computes the anisotropy ratio: min(Sx, Sy) / max(Sx, Sy).
    Lower values indicate strong directional blur (e.g., motion blur).
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    mean_sx = np.mean(np.abs(sx))
    mean_sy = np.mean(np.abs(sy))

    if mean_sx == 0 or mean_sy == 0:
        return 0.0

    return float(min(mean_sx, mean_sy) / max(mean_sx, mean_sy))

import cv2
import numpy as np
from typing import Tuple, List, Optional
from app.services.pipeline.sharpness.algorithms import compute_laplacian_score, compute_tenengrad_score

def run_tiled_sharpness(
    image: np.ndarray,
    config,
    anisotropy: bool = False
) -> Tuple[str, float, Optional[float]]:
    """
    Performs spatially-aware tiled sharpness scoring to ignore blank margins.

    Args:
        image: Input image (NumPy array).
        config: Configuration object (with tile_grid_rows, tile_grid_cols, etc.).
        anisotropy: Whether to calculate anisotropy ratio.

    Returns:
        (status, final_score, anisotropy_ratio)
    """
    h, w = image.shape[:2]
    rows = config.tile_grid_rows
    cols = config.tile_grid_cols

    tile_h = h // rows
    tile_w = w // cols

    valid_scores = []

    # 1. Grid Division & Blank Tile Removal
    for r in range(rows):
        for c in range(cols):
            y1, y2 = r * tile_h, (r + 1) * tile_h
            x1, x2 = c * tile_w, (c + 1) * tile_w
            tile = image[y1:y2, x1:x2]

            # Use variance as a proxy for content (blank tiles have low variance)
            if len(tile.shape) == 3:
                tile_gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            else:
                tile_gray = tile

            if np.var(tile_gray) < config.blank_tile_variance_threshold:
                continue # Skip blank tile

            # 2. Local Scoring
            if config.sharpness_algorithm == "laplacian":
                score = compute_laplacian_score(tile_gray)
            else:
                score = compute_tenengrad_score(tile_gray)

            valid_scores.append(score)

    if not valid_scores:
        return "reject", 0.0, None # Entire image is blank/constant

    # 3. Percentile Aggregation
    # Instead of mean, we use a lower percentile to be conservative about blur
    valid_scores.sort()
    idx = int(len(valid_scores) * (config.sharpness_percentile / 100.0))
    idx = max(0, min(idx, len(valid_scores) - 1))
    final_score = valid_scores[idx]

    # 4. Anisotropy (Optional)
    anisotropy_ratio = None
    if anisotropy:
        from app.services.pipeline.sharpness.algorithms import compute_anisotropy_ratio
        anisotropy_ratio = compute_anisotropy_ratio(image)

    # 5. Status Determination
    if final_score > config.sharp_pass_threshold:
        status = "pass"
    elif final_score <= config.blurry_reject_threshold:
        status = "reject"
    else:
        status = "borderline"

    return status, float(final_score), anisotropy_ratio

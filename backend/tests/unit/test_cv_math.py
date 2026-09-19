import pytest
import numpy as np
import cv2
import os
from app.services.pipeline.sharpness.algorithms import compute_laplacian_score, compute_tenengrad_score, compute_anisotropy_ratio
from app.services.pipeline.sharpness.tiled_scoring import run_tiled_sharpness

def create_synthetic_image(sharp=True, blurry=False, blank_margin=False):
    """Creates a synthetic image for testing sharpness."""
    img = np.zeros((1000, 1000), dtype=np.uint8)

    # Define content area
    if blank_margin:
        y1, y2, x1, x2 = 200, 800, 200, 800
    else:
        y1, y2, x1, x2 = 0, 1000, 0, 1000

    # Create a pattern (checkerboard)
    content = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
    for i in range(0, content.shape[0], 20):
        for j in range(0, content.shape[1], 20):
            if (i//20 + j//20) % 2 == 0:
                content[i:i+20, j:j+20] = 255

    if blurry:
        content = cv2.GaussianBlur(content, (15, 15), 0)

    img[y1:y2, x1:x2] = content
    return img

def test_laplacian_sharpness():
    sharp_img = create_synthetic_image(sharp=True)
    blurry_img = create_synthetic_image(blurry=True)

    sharp_score = compute_laplacian_score(sharp_img)
    blurry_score = compute_laplacian_score(blurry_img)

    assert sharp_score > blurry_score, f"Sharp image ({sharp_score}) should have higher score than blurry ({blurry_score})"

def test_tenengrad_sharpness():
    sharp_img = create_synthetic_image(sharp=True)
    blurry_img = create_synthetic_image(blurry=True)

    sharp_score = compute_tenengrad_score(sharp_img)
    blurry_score = compute_tenengrad_score(blurry_img)

    assert sharp_score > blurry_score

def test_tiled_scoring_blank_margins():
    # Image with large blank margins (1000x1000)
    # Content is at [200:800, 200:800]
    img_with_margins = create_synthetic_image(blank_margin=True)

    class MockConfig:
        sharpness_algorithm = "laplacian"
        tile_grid_rows = 4
        tile_grid_cols = 4
        blank_tile_variance_threshold = 10.0
        sharpness_percentile = 50
        sharp_pass_threshold = 100.0
        blurry_reject_threshold = 20.0

    config = MockConfig()

    status_margin, score_margin, _ = run_tiled_sharpness(img_with_margins, config)

    # Verify the system didn't just return 0 (meaning it found content)
    assert score_margin > 0, "Should have found content in the center of the image"
    assert status_margin == "pass", "Center content is sharp, should be a PASS"

def test_anisotropy_directional_blur():
    # Create a vertically blurred image
    img = np.zeros((500, 500), dtype=np.uint8)
    for i in range(0, 500, 10):
        img[i:i+5, :] = 255

    # This image has high vertical gradients but zero horizontal gradients
    ratio = compute_anisotropy_ratio(img)
    assert ratio < 0.2, f"Directional blur should have low anisotropy ratio: {ratio}"

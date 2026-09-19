import cv2
import numpy as np
from typing import Tuple, Dict, Any
from app.services.pipeline.common.sanity import check_resolution, check_brightness, canonical_resize, apply_denoise
from app.services.pipeline.sharpness.tiled_scoring import run_tiled_sharpness
from app.services.pipeline.id_passport.boundary import detect_boundary
from app.services.pipeline.id_passport.glare import run_glare_check

def run_id_passport_pipeline(image: np.ndarray, config) -> Dict[str, Any]:
    """
    Orchestrates the ID/Passport quality verification pipeline.
    """
    results = {"stages": {}}

    # 1. Sanity Check
    results["stages"]["sanity"] = {"status": "pass"}

    if getattr(config, "enable_resolution_check", True):
        res_ok, res_val = check_resolution(image, config.min_resolution_long_edge_px)
        results["stages"]["sanity"]["resolution_px"] = res_val
        if not res_ok:
            results["stages"]["sanity"]["status"] = "fail"
            return {"status": "REJECT", "final_reason": f"Resolution too low: {res_val}px", "stages": results["stages"]}
    else:
        results["stages"]["sanity"]["resolution_check"] = "skipped"

    if getattr(config, "enable_brightness_check", True):
        b_ok, b_val = check_brightness(image, config.brightness_min, config.brightness_max)
        results["stages"]["sanity"]["brightness"] = b_val
        if not b_ok:
            results["stages"]["sanity"]["status"] = "fail"
            return {"status": "REJECT", "final_reason": f"Brightness out of range: {b_val:.2f}", "stages": results["stages"]}
    else:
        results["stages"]["sanity"]["brightness_check"] = "skipped"

    # 2. Boundary Detection & Rectification
    if getattr(config, "enable_boundary_detection", True):
        rectified_img, confidence, fallback = detect_boundary(image, config)
        results["stages"]["boundary_detection"] = {
            "status": "pass",
            "confidence": confidence,
            "fallback_used": fallback
        }
    else:
        rectified_img = image
        results["stages"]["boundary_detection"] = {"status": "skipped", "reason": "Boundary detection disabled"}

    # 3. Glare Check
    if getattr(config, "enable_glare_mask", True):
        glare_ok, glare_val, glare_reason = run_glare_check(rectified_img, config)
        results["stages"]["glare"] = {"status": "pass" if glare_ok else "fail", "glare_area_pct": glare_val}
        if not glare_ok:
            return {"status": "REJECT", "final_reason": glare_reason, "stages": results["stages"]}
    else:
        results["stages"]["glare"] = {"status": "skipped", "reason": "Glare check disabled"}

    # 4. Sharpness (Spatially Aware) & Anisotropy Check
    if getattr(config, "enable_sharpness_check", True):
        sharp_status, sharp_score, anisotropy = run_tiled_sharpness(rectified_img, config, anisotropy=True)
        results["stages"]["sharpness"] = {
            "status": sharp_status,
            "score": sharp_score,
            "anisotropy_ratio": anisotropy
        }

        # Directional blur check
        if getattr(config, "enable_anisotropy_check", True) and anisotropy is not None and anisotropy < config.anisotropy_ratio_flag_threshold:
            results["stages"]["sharpness"]["status"] = "reject"
            return {"status": "REJECT", "final_reason": f"Directional blur detected: ratio {anisotropy:.2f}", "stages": results["stages"]}

        if sharp_status == "reject":
            return {"status": "REJECT", "final_reason": "Image is too blurry", "stages": results["stages"]}

        final_status = "PASS" if sharp_status == "pass" else "BORDERLINE"
        final_reason = "Sharpness within acceptable range" if final_status == "PASS" else "Sharpness borderline"
    else:
        results["stages"]["sharpness"] = {"status": "skipped", "reason": "Sharpness check disabled"}
        final_status = "PASS"
        final_reason = "Document passed active validation checks"

    return {
        "status": final_status,
        "final_reason": final_reason,
        "stages": results["stages"]
    }

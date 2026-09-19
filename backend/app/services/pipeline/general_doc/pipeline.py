import cv2
import numpy as np
from typing import Tuple, Dict, Any
from app.services.pipeline.common.sanity import check_resolution, check_brightness, canonical_resize, apply_denoise
from app.services.pipeline.sharpness.tiled_scoring import run_tiled_sharpness

def run_general_doc_pipeline(image: np.ndarray, config) -> Dict[str, Any]:
    """
    Orchestrates the General Document quality verification pipeline.
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

    # 2. Preprocessing
    image = canonical_resize(image, config.canonical_resize_width_px)
    if config.enable_denoise:
        image = apply_denoise(image, config.denoise_kernel_size)

    # 3. Sharpness (Spatially Aware)
    if getattr(config, "enable_sharpness_check", True):
        sharp_status, sharp_score, _ = run_tiled_sharpness(image, config, anisotropy=False)
        results["stages"]["sharpness"] = {
            "status": sharp_status,
            "score": sharp_score
        }

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

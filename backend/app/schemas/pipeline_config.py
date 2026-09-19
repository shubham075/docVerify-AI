from typing import List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

class SharpnessAlgorithm(str, Enum):
    LAPLACIAN = "laplacian"
    TENENGRAD = "tenengrad"

class PipelineConfigBase(BaseModel):
    """Common configuration fields for all document pipelines with on/off toggles."""
    # Sanity checks
    enable_resolution_check: bool = Field(default=True, description="Enable minimum resolution validation")
    min_resolution_long_edge_px: int = Field(..., description="Reject files below this resolution")
    
    enable_brightness_check: bool = Field(default=True, description="Enable mean luma/brightness bounds validation")
    brightness_min: int = Field(..., ge=0, le=255, description="Mean luma floor")
    brightness_max: int = Field(..., ge=0, le=255, description="Mean luma ceiling")
    
    # Preprocessing
    canonical_resize_width_px: int = Field(..., description="Normalized width for scoring")
    enable_denoise: bool = Field(default=True, description="Enable Gaussian kernel denoising")
    denoise_kernel_size: int = Field(default=3, description="Gaussian kernel size (must be odd)")
    
    # Sharpness scoring
    enable_sharpness_check: bool = Field(default=True, description="Enable tiled sharpness quality scoring")
    sharpness_algorithm: SharpnessAlgorithm
    tile_grid_rows: int = Field(default=3)
    tile_grid_cols: int = Field(default=3)
    blank_tile_variance_threshold: float = Field(default=100.0)
    sharpness_percentile: int = Field(..., ge=0, le=100)
    sharp_pass_threshold: float = Field(...)
    blurry_reject_threshold: float = Field(...)
    
    # OCR verification (Independent primary stage, not a fallback)
    enable_ocr: bool = Field(default=True, description="Enable OCR text extraction and confidence verification")
    ocr_engine: str = Field(default="auto", description="OCR engine provider: 'auto', 'tesseract', 'doctr', 'paddleocr'")
    ocr_confidence_threshold: int = Field(..., ge=0, le=100)
    ocr_only_on_borderline: Optional[bool] = Field(default=None, description="Deprecated. OCR is now an independent stage.")

class GeneralDocConfig(PipelineConfigBase):
    """Configuration specific to general document pipelines."""
    enable_boundary_detection: bool = Field(default=False)
    enable_glare_mask: bool = Field(default=False)
    pdf_pages_to_check: str = Field(default="all_up_to_limit") # e.g., 'first_page_only', 'all_up_to_limit'
    pdf_max_pages_checked: int = Field(default=10)

class IDPassportConfig(PipelineConfigBase):
    """Configuration specific to ID and Passport pipelines."""
    enable_boundary_detection: bool = Field(default=True)
    boundary_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    fallback_center_crop_pct: int = Field(default=60, ge=0, le=100)
    enable_glare_mask: bool = Field(default=True)
    glare_value_threshold: int = Field(default=250, ge=0, le=255)
    glare_saturation_threshold: int = Field(default=25, ge=0, le=255)
    glare_max_area_pct: float = Field(default=1.5)
    enable_anisotropy_check: bool = Field(default=True)
    anisotropy_ratio_flag_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    ocr_field_set: List[str] = Field(default=["MRZ", "full_name", "dob", "expiry_date", "document_number"])

def get_ideal_defaults(doc_type: str):
    """
    Returns the ideal calibration defaults as specified in the implementation plan.
    """
    if doc_type == "general":
        return GeneralDocConfig(
            enable_resolution_check=True,
            min_resolution_long_edge_px=1500,
            enable_brightness_check=True,
            brightness_min=40,
            brightness_max=220,
            canonical_resize_width_px=1200,
            enable_denoise=True,
            denoise_kernel_size=3,
            enable_sharpness_check=True,
            sharpness_algorithm=SharpnessAlgorithm.LAPLACIAN,
            tile_grid_rows=3,
            tile_grid_cols=3,
            blank_tile_variance_threshold=100.0,
            sharpness_percentile=25,
            sharp_pass_threshold=100.0,
            blurry_reject_threshold=40.0,
            enable_ocr=True,
            ocr_engine="auto",
            ocr_confidence_threshold=75,
            enable_boundary_detection=False,
            enable_glare_mask=False,
            pdf_pages_to_check="all_up_to_limit",
            pdf_max_pages_checked=10
        )
    elif doc_type == "id_passport":
        return IDPassportConfig(
            enable_resolution_check=True,
            min_resolution_long_edge_px=1200,
            enable_brightness_check=True,
            brightness_min=40,
            brightness_max=220,
            canonical_resize_width_px=1200,
            enable_denoise=True,
            denoise_kernel_size=3,
            enable_sharpness_check=True,
            sharpness_algorithm=SharpnessAlgorithm.TENENGRAD,
            tile_grid_rows=4,
            tile_grid_cols=4,
            blank_tile_variance_threshold=100.0,
            sharpness_percentile=20,
            sharp_pass_threshold=100.0,
            blurry_reject_threshold=55.0,
            enable_ocr=True,
            ocr_engine="auto",
            ocr_confidence_threshold=80,
            enable_boundary_detection=True,
            boundary_confidence_threshold=0.7,
            fallback_center_crop_pct=60,
            enable_glare_mask=True,
            glare_value_threshold=250,
            glare_saturation_threshold=25,
            glare_max_area_pct=1.5,
            enable_anisotropy_check=True,
            anisotropy_ratio_flag_threshold=0.35,
            ocr_field_set=["MRZ", "full_name", "dob", "expiry_date", "document_number"]
        )
    else:
        raise ValueError(f"Unsupported doc_type: {doc_type}")

from fastapi import APIRouter
from app.api.v1.endpoints import config, verify, ocr
from app.core.settings import settings
from app.services.pipeline.ocr.engine import get_ocr_engine_availability

router = APIRouter()
router.include_router(config.router, prefix="/config", tags=["configuration"])
router.include_router(verify.router, prefix="/verify", tags=["verification"])
router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])

@router.get("/health", tags=["system"])
async def health_check():
    """
    Microservice health and readiness check for orchestrators / load balancers.
    Reports API status and live availability of all OCR engine providers.
    """
    engine_status = get_ocr_engine_availability()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "base_url": settings.BASE_URL,
        "api_v1_url": settings.API_V1_URL,
        "version": "1.0.0",
        "ocr_engines": engine_status
    }

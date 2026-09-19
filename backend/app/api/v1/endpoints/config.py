from fastapi import APIRouter, Query, HTTPException, Body
from app.schemas.pipeline_config import get_ideal_defaults
from app.services.config_store import get_active_defaults, save_custom_config, reset_custom_config, load_custom_config
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()

class SaveConfigRequest(BaseModel):
    doc_type: str
    config: Dict[str, Any]

@router.get("/defaults")
async def get_config_defaults(doc_type: str = Query(..., pattern="^(general|id_passport)$")):
    """
    Returns the active default config object (custom saved if available, otherwise factory).
    """
    try:
        defaults = get_active_defaults(doc_type)
        is_custom = load_custom_config(doc_type) is not None
        result = defaults.model_dump()
        result["_is_custom"] = is_custom
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/factory-defaults")
async def get_factory_defaults(doc_type: str = Query(..., pattern="^(general|id_passport)$")):
    """
    Returns the immutable calibrated factory defaults.
    """
    try:
        defaults = get_ideal_defaults(doc_type)
        return defaults.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/save")
async def save_config(payload: SaveConfigRequest):
    """
    Saves and persists customized configuration parameters for the doc_type to custom_config.json.
    """
    if payload.doc_type not in ["general", "id_passport"]:
        raise HTTPException(status_code=400, detail="Invalid doc_type")
    try:
        saved = save_custom_config(payload.doc_type, payload.config)
        saved["_is_custom"] = True
        return {"status": "success", "message": "Configuration saved to server", "data": saved}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save configuration: {str(e)}")

@router.post("/reset")
async def reset_config(doc_type: str = Query(..., pattern="^(general|id_passport)$")):
    """
    Clears custom saved configuration from custom_config.json and restores factory defaults.
    """
    try:
        reset_custom_config(doc_type)
        factory = get_ideal_defaults(doc_type)
        result = factory.model_dump()
        result["_is_custom"] = False
        return {"status": "success", "message": "Restored factory defaults", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to reset configuration: {str(e)}")


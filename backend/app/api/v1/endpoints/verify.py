import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from app.core.settings import settings
from app.schemas.pipeline_config import PipelineConfigBase, GeneralDocConfig, IDPassportConfig
from app.services.config_store import get_active_defaults
from app.services.file_validation import validate_file, validate_bulk_payload
from app.services.orchestrator import run_pipeline_orchestrator
from app.utils.image_io import load_image_from_upload

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)

@router.post("", include_in_schema=True)
@router.post("/", include_in_schema=False)
async def verify_single(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    config: Optional[str] = Form(None)
):
    """
    Single file quality verification.
    """
    if doc_type not in ["general", "id_passport"]:
        raise HTTPException(status_code=400, detail="Invalid doc_type")

    # 1. Validation
    is_valid, reason = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"reason": reason, "filename": file.filename})

    # 2. Config Handling
    # If config is provided as JSON string, merge it with defaults
    final_config = get_active_defaults(doc_type)
    if config:
        import json
        try:
            overrides = json.loads(config)
            updated_data = final_config.dict()
            updated_data.update(overrides)
            if doc_type == "general":
                final_config = GeneralDocConfig(**updated_data)
            else:
                final_config = IDPassportConfig(**updated_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid config format: {str(e)}")

    # 3. Processing (Offload to Executor)
    import asyncio
    loop = asyncio.get_event_loop()

    image = await load_image_from_upload(file)

    # Offload to executor to avoid blocking event loop
    result = await loop.run_in_executor(
        executor,
        run_pipeline_orchestrator,
        image,
        doc_type,
        final_config
    )

    result["filename"] = file.filename
    return result

@router.post("/bulk")
async def verify_bulk(
    files: List[UploadFile] = File(...),
    doc_type: str = Form(...),
    config: Optional[str] = Form(None)
):
    """
    Bulk file quality verification using parallel process pool.
    """
    if doc_type not in ["general", "id_passport"]:
        raise HTTPException(status_code=400, detail="Invalid doc_type")

    # 1. Bulk Validation
    is_valid, reason = validate_bulk_payload(files)
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    # 2. Config Handling
    final_config = get_active_defaults(doc_type)
    if config:
        import json
        overrides = json.loads(config)
        updated_data = final_config.dict()
        updated_data.update(overrides)
        if doc_type == "general":
            final_config = GeneralDocConfig(**updated_data)
        else:
            final_config = IDPassportConfig(**updated_data)

    # 3. Parallel Processing
    import asyncio
    loop = asyncio.get_event_loop()

    tasks = []
    for file in files:
        image = await load_image_from_upload(file)
        # Create a future for each file
        tasks.append(loop.run_in_executor(
            executor,
            run_pipeline_orchestrator,
            image,
            doc_type,
            final_config
        ))

    results = await asyncio.gather(*tasks)

    # Zip results with filenames for response
    final_response = []
    for filename, res in zip([f.filename for f in files], results):
        res["filename"] = filename
        final_response.append(res)

    return final_response

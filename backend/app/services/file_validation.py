import magic
import os
from fastapi import HTTPException, UploadFile
from app.core.settings import settings
from typing import Tuple

class FileValidationException(HTTPException):
    def __init__(self, reason: str, filename: str):
        super().__init__(status_code=400, detail={"reason": reason, "filename": filename})

def validate_file(file: UploadFile) -> Tuple[bool, str]:
    """
    Validates an uploaded file against size, type, and corruption constraints.
    Returns (is_valid, reason).
    """
    # 1. Zero-byte check and Size check (per-file)
    file.file.seek(0, os.SEEK_END)
    file_size_bytes = file.file.tell()
    file.file.seek(0) # Reset pointer

    if file_size_bytes == 0:
        return False, "empty_file"

    file_size_mb = file_size_bytes / (1024 * 1024)
    if file_size_mb > settings.MAX_SINGLE_FILE_SIZE_MB:
        return False, "file_too_large"

    # 3. MIME-type sniffing (using python-magic with fallback)
    header = file.file.read(2048)
    file.file.seek(0)
    try:
        mime_type = magic.from_buffer(header, mime=True)
    except Exception:
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file.filename or "")
        if not mime_type:
            mime_type = file.content_type

    # If magic returned octet-stream, check file extension / content_type
    if mime_type == "application/octet-stream" and file.content_type:
        mime_type = file.content_type

    if mime_type not in settings.ALLOWED_MIME_TYPES:
        return False, f"unsupported_mime_type_{mime_type}"

    # 4. Corruption check
    # Basic check: can we open it?
    try:
        if mime_type == "application/pdf":
            import fitz # PyMuPDF
            doc = fitz.open(stream=file.file.read(), filetype="pdf")
            file.file.seek(0)
            if doc.page_count == 0:
                return False, "corrupt_pdf_no_pages"
            doc.close()
        else:
            import cv2
            import numpy as np
            file_bytes = np.frombuffer(file.file.read(), np.uint8)
            file.file.seek(0)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                return False, "unreadable_image"
    except Exception:
        return False, "unreadable_file"

    return True, "success"

def validate_bulk_payload(files: list[UploadFile]) -> Tuple[bool, str]:
    """
    Validates the overall bulk upload constraints.
    """
    if len(files) > settings.MAX_FILES_PER_BULK_UPLOAD:
        return False, "too_many_files"

    total_size_mb = 0
    for file in files:
        # Use approximate size from header if available, otherwise read
        file.file.seek(0, os.SEEK_END)
        total_size_mb += file.file.tell() / (1024 * 1024)
        file.file.seek(0)

    if total_size_mb > settings.MAX_TOTAL_BULK_PAYLOAD_MB:
        return False, "total_payload_too_large"

    return True, "success"

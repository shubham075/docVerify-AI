import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # API & Server Configuration
    PROJECT_NAME: str = "DocVerify AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Host, Port & Base URL (Configurable via .env, not hardcoded)
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    BASE_URL: str = "http://127.0.0.1:8000"
    API_V1_STR: str = "/api/v1"

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = ["*"]

    # Upload Limits
    MAX_SINGLE_FILE_SIZE_MB: int = 15
    MAX_FILES_PER_BULK_UPLOAD: int = 25
    MAX_TOTAL_BULK_PAYLOAD_MB: int = 150
    MAX_PDF_PAGES_CHECKED: int = 10

    # Allowed MIME Types
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/bmp"
    ]

    # Storage
    TEMP_UPLOAD_DIR: str = "temp_uploads"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @property
    def API_V1_URL(self) -> str:
        clean_base = self.BASE_URL.rstrip('/')
        return f"{clean_base}{self.API_V1_STR}"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

# Ensure temp directory exists
os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)

import json
import os
from typing import Dict, Any, Optional, Union
from app.schemas.pipeline_config import get_ideal_defaults, GeneralDocConfig, IDPassportConfig

CONFIG_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "custom_config.json"
)

def _read_all_configs() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE_PATH):
        return {}
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_all_configs(data: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving config file: {e}")

def load_custom_config(doc_type: str) -> Optional[Dict[str, Any]]:
    """
    Returns custom saved configuration dictionary for doc_type if exists.
    """
    all_configs = _read_all_configs()
    return all_configs.get(doc_type)

def save_custom_config(doc_type: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and persists custom configuration dictionary to custom_config.json.
    """
    # Validate against Pydantic schema
    factory = get_ideal_defaults(doc_type)
    merged = factory.model_dump()
    merged.update(config_data)

    if doc_type == "general":
        validated = GeneralDocConfig(**merged)
    else:
        validated = IDPassportConfig(**merged)

    all_configs = _read_all_configs()
    all_configs[doc_type] = validated.model_dump()
    _write_all_configs(all_configs)
    return all_configs[doc_type]

def reset_custom_config(doc_type: Optional[str] = None) -> None:
    """
    Removes custom configuration for doc_type (or all if doc_type is None).
    """
    if doc_type is None:
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                os.remove(CONFIG_FILE_PATH)
            except Exception:
                pass
    else:
        all_configs = _read_all_configs()
        if doc_type in all_configs:
            del all_configs[doc_type]
            _write_all_configs(all_configs)

def get_active_defaults(doc_type: str) -> Union[GeneralDocConfig, IDPassportConfig]:
    """
    Returns active defaults: custom saved defaults if present, else ideal factory defaults.
    """
    factory = get_ideal_defaults(doc_type)
    custom = load_custom_config(doc_type)
    if not custom:
        return factory

    try:
        merged = factory.model_dump()
        merged.update(custom)
        if doc_type == "general":
            return GeneralDocConfig(**merged)
        else:
            return IDPassportConfig(**merged)
    except Exception:
        # Fallback to factory if custom config corrupted or incompatible
        return factory

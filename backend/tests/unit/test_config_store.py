import pytest
import os
from app.services.config_store import (
    get_active_defaults,
    save_custom_config,
    reset_custom_config,
    load_custom_config,
    CONFIG_FILE_PATH
)
from app.schemas.pipeline_config import get_ideal_defaults

def test_config_store_lifecycle():
    # Clean state before test
    reset_custom_config("id_passport")
    
    # 1. Initial active defaults should equal factory defaults
    factory = get_ideal_defaults("id_passport")
    active = get_active_defaults("id_passport")
    assert active.brightness_min == factory.brightness_min
    assert active.enable_ocr == True

    # 2. Save custom modification
    save_custom_config("id_passport", {
        "brightness_min": 15,
        "enable_ocr": False,
        "sharp_pass_threshold": 120.0
    })

    # 3. Active defaults should reflect custom values
    custom_active = get_active_defaults("id_passport")
    assert custom_active.brightness_min == 15
    assert custom_active.enable_ocr == False
    assert custom_active.sharp_pass_threshold == 120.0

    # 4. Reset custom config
    reset_custom_config("id_passport")
    restored = get_active_defaults("id_passport")
    assert restored.brightness_min == factory.brightness_min
    assert restored.enable_ocr == True
    assert restored.sharp_pass_threshold == factory.sharp_pass_threshold

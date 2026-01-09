# File: app/admin_api/routes/runtime.py
# Version: v0.1.0
# Purpose: runtime info endpoints (deployment mode, config path)

from __future__ import annotations

from fastapi import APIRouter

from app.core.deployment import get_deployment_mode
from app.core.runtime_config import DEFAULT_CONFIG_PATH

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


@router.get("")
def runtime_info() -> dict:
    mode = get_deployment_mode().value
    return {
        "deployment_mode": mode,
        "config_path": DEFAULT_CONFIG_PATH,
    }

# END_OF_FILE

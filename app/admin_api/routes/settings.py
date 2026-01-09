# File: app/admin_api/routes/settings.py
# Version: v0.1.0
# Purpose: Settings endpoints (read/write) for Admin UI

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.admin_api.help_registry import HELP_REGISTRY
from app.admin_api.schemas import FieldHelpOut, SettingItemOut
from app.admin_api.services import get_effective_value, get_field_help, set_setting
from app.services.settings.defaults import DEFAULTS
from app.services.settings.repo import SettingsRepo

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingUpdateIn(BaseModel):
    value: Any


@router.get("/{tenant_id}", response_model=List[SettingItemOut])
def list_settings(tenant_id: str) -> List[SettingItemOut]:
    repo = SettingsRepo()
    items: List[SettingItemOut] = []

    # For MVP we expose only keys known in DEFAULTS and keys referenced in HELP_REGISTRY.
    keys = set(DEFAULTS.keys())
    for page in HELP_REGISTRY.values():
        for f in page.get("fields", []) or []:
            if f.get("key"):
                keys.add(f["key"])

    for key in sorted(keys):
        val = get_effective_value(repo, tenant_id, key)
        meta = get_field_help(key)
        help_out = FieldHelpOut(**meta) if meta else None
        items.append(SettingItemOut(tenant_id=tenant_id, key=key, value=val, help=help_out))

    return items


@router.put("/{tenant_id}/{key}", response_model=SettingItemOut)
def update_setting(tenant_id: str, key: str, body: SettingUpdateIn) -> SettingItemOut:
    repo = SettingsRepo()

    try:
        set_setting(repo, tenant_id, key, body.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    meta = get_field_help(key)
    help_out = FieldHelpOut(**meta) if meta else None
    val = get_effective_value(repo, tenant_id, key)
    return SettingItemOut(tenant_id=tenant_id, key=key, value=val, help=help_out)

# END_OF_FILE

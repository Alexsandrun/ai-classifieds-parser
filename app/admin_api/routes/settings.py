# File: app/admin_api/routes/settings.py
# Version: v0.2.0
# Changes:
#  - enforce allowlist keys
#  - admin-only updates with token (RBAC MVP)
#  - audit log settings changes
# Purpose: Settings endpoints (read/write) for Admin UI

from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.admin_api.auth import ActorContext, require_min_role
from app.admin_api.help_registry import HELP_REGISTRY
from app.admin_api.schemas import FieldHelpOut, SettingItemOut
from app.admin_api.services import get_effective_value, get_field_help, known_keys, set_setting
from app.services.settings.defaults import DEFAULTS
from app.services.settings.repo import SettingsRepo
from app.services.audit.repo import AuditRepo

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingUpdateIn(BaseModel):
    value: Any


@router.get("/{tenant_id}", response_model=List[SettingItemOut])
def list_settings(tenant_id: str) -> List[SettingItemOut]:
    repo = SettingsRepo()
    items: List[SettingItemOut] = []

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
def update_setting(
    request: Request,
    tenant_id: str,
    key: str,
    body: SettingUpdateIn,
    actor: ActorContext = require_min_role("admin"),
) -> SettingItemOut:
    # allowlist key
    if key not in known_keys():
        raise HTTPException(status_code=400, detail="Unknown/forbidden setting key")

    repo = SettingsRepo()
    audit = AuditRepo(dsn=repo.dsn)

    old_val = get_effective_value(repo, tenant_id, key)

    try:
        new_val = set_setting(repo, tenant_id, key, body.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # audit event
    ip = ""
    if request.client:
        ip = request.client.host or ""
    ua = request.headers.get("user-agent", "")

    try:
        audit.write_event(
            tenant_id=tenant_id,
            event_type="settings.update",
            actor_id=actor.actor_id or "",
            actor_role=actor.role,
            ip=ip,
            user_agent=ua,
            details={
                "key": key,
                "old_value": old_val,
                "new_value": new_val,
            },
        )
    except Exception:
        # audit must never break admin action (but we can alert later)
        pass

    meta = get_field_help(key)
    help_out = FieldHelpOut(**meta) if meta else None
    val = get_effective_value(repo, tenant_id, key)
    return SettingItemOut(tenant_id=tenant_id, key=key, value=val, help=help_out)

# END_OF_FILE

# File: app/admin_api/services.py
# Version: v0.1.0
# Purpose: glue between settings repo and help registry (validation + defaults)

from __future__ import annotations

from typing import Any, Dict, Optional

from app.admin_api.help_registry import HELP_REGISTRY
from app.services.settings.defaults import DEFAULTS
from app.services.settings.repo import SettingsRepo


def get_field_help(key: str) -> Optional[dict]:
    for page in HELP_REGISTRY.values():
        for f in page.get("fields", []) or []:
            if f.get("key") == key:
                return f
    return None


def validate_value(key: str, value: Any) -> Any:
    """
    Validate (lightweight) against Help Registry constraints:
      - min/max for int
      - allowed for strings/enums
    """
    meta = get_field_help(key)
    if not meta:
        # if unknown key - allow, but admin UI later may restrict
        return value

    if "allowed" in meta and meta["allowed"]:
        s = str(value)
        if s not in meta["allowed"]:
            raise ValueError(f"Value '{s}' not allowed for {key}. Allowed: {meta['allowed']}")
        return s

    if "min" in meta or "max" in meta:
        try:
            n = int(value)
        except Exception as e:
            raise ValueError(f"Value for {key} must be int") from e

        if "min" in meta and n < int(meta["min"]):
            raise ValueError(f"Value for {key} must be >= {meta['min']}")
        if "max" in meta and n > int(meta["max"]):
            raise ValueError(f"Value for {key} must be <= {meta['max']}")
        return n

    return value


def get_effective_value(repo: SettingsRepo, tenant_id: str, key: str) -> Any:
    v = repo.get_json(tenant_id=tenant_id, key=key)
    if v is None and key in DEFAULTS:
        return DEFAULTS[key]
    return v


def set_setting(repo: SettingsRepo, tenant_id: str, key: str, value: Any) -> None:
    v2 = validate_value(key, value)
    repo.set_json(tenant_id=tenant_id, key=key, value=v2)

# END_OF_FILE

# File: app/admin_api/services.py
# Version: v0.2.0
# Changes:
#  - add allowlist for settings keys
#  - stricter validation (types/ranges/allowed)
#  - payload size guard
# Purpose: glue between settings repo and help registry (validation + defaults)

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Set

from app.admin_api.help_registry import HELP_REGISTRY
from app.services.settings.defaults import DEFAULTS
from app.services.settings.repo import SettingsRepo


def known_keys() -> Set[str]:
    """
    Allowlist of setting keys that can be modified via Admin API.
    Only keys in DEFAULTS or referenced by HELP_REGISTRY are allowed.
    """
    keys: Set[str] = set(DEFAULTS.keys())
    for page in HELP_REGISTRY.values():
        for f in page.get("fields", []) or []:
            k = f.get("key")
            if k:
                keys.add(str(k))
    return keys


def get_field_help(key: str) -> Optional[dict]:
    for page in HELP_REGISTRY.values():
        for f in page.get("fields", []) or []:
            if f.get("key") == key:
                return f
    return None


def _payload_size_guard(value: Any, max_bytes: int = 10_000) -> None:
    """
    Prevent stuffing huge payloads into settings (DoS / disk bloat).
    """
    try:
        raw = json.dumps(value, ensure_ascii=False)
        if len(raw.encode("utf-8", errors="ignore")) > max_bytes:
            raise ValueError(f"Setting payload too large (>{max_bytes} bytes)")
    except TypeError:
        # Non-JSON-serializable values are not allowed
        raise ValueError("Setting value must be JSON-serializable")


def validate_value(key: str, value: Any) -> Any:
    """
    Validate value using:
      1) Allowlist key check
      2) Help Registry constraints (min/max, allowed)
      3) Known strict rules for some keys
    """
    if key not in known_keys():
        raise ValueError("Unknown/forbidden setting key")

    _payload_size_guard(value)

    meta = get_field_help(key)

    # Strict rule examples (add more as we grow):
    if key in ("leads.ttl_days", "leads.max_pending", "leads.claim_timeout_minutes"):
        try:
            n = int(value)
        except Exception as e:
            raise ValueError(f"Value for {key} must be int") from e
        # Apply registry min/max if present
        if meta:
            if "min" in meta and n < int(meta["min"]):
                raise ValueError(f"Value for {key} must be >= {meta['min']}")
            if "max" in meta and n > int(meta["max"]):
                raise ValueError(f"Value for {key} must be <= {meta['max']}")
        return n

    if key == "leads.overflow_policy":
        s = str(value)
        allowed = ["DROP_OLDEST_NEW", "REJECT"]
        if s not in allowed:
            raise ValueError(f"Value '{s}' not allowed for {key}. Allowed: {allowed}")
        return s

    # Generic rules via help metadata (if any)
    if meta:
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

    # Default: accept JSON primitives/objects (still size-guarded)
    return value


def get_effective_value(repo: SettingsRepo, tenant_id: str, key: str) -> Any:
    v = repo.get_json(tenant_id=tenant_id, key=key)
    if v is None and key in DEFAULTS:
        return DEFAULTS[key]
    return v


def set_setting(repo: SettingsRepo, tenant_id: str, key: str, value: Any) -> Any:
    v2 = validate_value(key, value)
    repo.set_json(tenant_id=tenant_id, key=key, value=v2)
    return v2

# END_OF_FILE

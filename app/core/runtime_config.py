# File: app/core/runtime_config.py
# Version: v0.1.0
# Purpose: runtime config loader (default out-of-box) + canonical config path

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATH = "config/runtime.json"

_DEFAULTS: Dict[str, Any] = {
    "deployment_mode": "single_tenant",
}


def load_runtime_config(path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """
    Loads runtime config JSON from disk.
    If missing/broken -> returns defaults (must never crash app/tests).
    """
    p = Path(path)
    if not p.exists():
        return dict(_DEFAULTS)

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(_DEFAULTS)
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except Exception:
        return dict(_DEFAULTS)

# END_OF_FILE

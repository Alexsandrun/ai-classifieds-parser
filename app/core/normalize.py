# File: app/core/normalize.py
# Version: v0.1.0
# Purpose: normalization helpers (phones, names, etc.)

from __future__ import annotations

import re
from typing import Optional


def normalize_phone_e164(phone_raw: Optional[str]) -> Optional[str]:
    """
    Minimal placeholder (country-agnostic):
    - keep digits only
    - strip leading zeros
    - if plausible length -> return "+<digits>"

    NOTE: real implementation should be country-aware (region rules).
    """
    if not phone_raw:
        return None
    digits = re.sub(r"\D+", "", phone_raw)
    if not digits:
        return None
    digits = digits.lstrip("0")
    if len(digits) < 9:
        return None
    return "+" + digits


def normalize_name(name_raw: Optional[str]) -> Optional[str]:
    if not name_raw:
        return None
    s = name_raw.strip().lower()
    return s or None

# END_OF_FILE

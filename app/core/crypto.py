# File: app/core/crypto.py
# Version: v0.1.0
# Purpose: deterministic hashing helpers (sha256, phone_hash)

from __future__ import annotations

import hashlib
from typing import Optional

from app.core.config import TENANT_SALT


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def phone_hash_e164(phone_e164: Optional[str], *, tenant_salt: str = TENANT_SALT) -> Optional[str]:
    """
    Canonical phone hash:
      sha256(tenant_salt + ":" + phone_e164) -> hex
    """
    if not phone_e164:
        return None
    return sha256_hex(f"{tenant_salt}:{phone_e164}")

# END_OF_FILE

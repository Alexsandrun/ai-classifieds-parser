# File: app/admin_api/auth.py
# Version: v0.2.3
# Changes:
#  - accept admin token in header X-AICP-Token (as tests expect)
#  - keep backward compatibility with X-AICP-Admin-Token
#  - require_min_role() returns callable (NOT Depends) to avoid double-wrapping crashes
#  - enforce AICP_ADMIN_TOKEN (read env at request-time; tests monkeypatch after import)
#  - allow token to elevate effective role to "admin"
# Purpose: FastAPI auth helpers (role gating + admin token guard)

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from fastapi import Header, HTTPException

Role = Literal["viewer", "agent", "admin", "system"]

ROLE_RANK: Dict[str, int] = {
    "viewer": 10,
    "agent": 20,
    "admin": 30,
    "system": 40,
}

HDR_ACTOR = "X-AICP-Actor"
HDR_ROLE = "X-AICP-Role"
HDR_TOKEN = "X-AICP-Token"  # canonical token header
HDR_ADMIN_TOKEN_LEGACY = "X-AICP-Admin-Token"  # legacy / backwards compatible


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    role: Role


def _norm_role(value: Optional[str]) -> Role:
    v = (value or "").strip().lower()
    if v in ("viewer", "agent", "admin", "system"):
        return v  # type: ignore[return-value]
    return "viewer"


def _expected_admin_token() -> str:
    """
    Read env at request-time (tests use monkeypatch.setenv after imports).
    Empty token => token not configured => do not enforce.
    """
    return os.environ.get("AICP_ADMIN_TOKEN", "").strip()


def get_actor_context(*, x_aicp_actor: Optional[str], x_aicp_role: Optional[str], token_ok: bool) -> ActorContext:
    actor_id = (x_aicp_actor or "").strip()[:200]
    role = _norm_role(x_aicp_role)

    # If token is valid, elevate effective role to admin (role header becomes optional).
    if token_ok and ROLE_RANK[role] < ROLE_RANK["admin"]:
        role = "admin"

    return ActorContext(actor_id=actor_id, role=role)


def require_min_role(min_role: Role):
    """
    Returns a dependency callable (routes should do Depends(require_min_role("admin"))).
    Enforces:
      - role rank
      - token for admin+ endpoints when configured
      - token can elevate role to admin
    """
    min_role = _norm_role(min_role)

    def _dep(
        x_aicp_actor: Optional[str] = Header(default=None, alias=HDR_ACTOR),
        x_aicp_role: Optional[str] = Header(default=None, alias=HDR_ROLE),
        x_aicp_token: Optional[str] = Header(default=None, alias=HDR_TOKEN),
        x_aicp_admin_token_legacy: Optional[str] = Header(default=None, alias=HDR_ADMIN_TOKEN_LEGACY),
    ) -> ActorContext:
        expected = _expected_admin_token()

        # accept both headers; canonical is X-AICP-Token
        provided = x_aicp_token if (x_aicp_token is not None) else x_aicp_admin_token_legacy
        token_ok = True
        if expected:
            token_ok = (provided or "") == expected

        # For admin endpoints: require token if configured
        if ROLE_RANK[min_role] >= ROLE_RANK["admin"] and expected and not token_ok:
            raise HTTPException(status_code=403, detail="Forbidden")

        ctx = get_actor_context(x_aicp_actor=x_aicp_actor, x_aicp_role=x_aicp_role, token_ok=token_ok)

        if ROLE_RANK[ctx.role] < ROLE_RANK[min_role]:
            raise HTTPException(status_code=403, detail="Forbidden")

        return ctx

    return _dep


# END_OF_FILE

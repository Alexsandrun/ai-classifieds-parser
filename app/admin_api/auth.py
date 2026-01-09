# File: app/admin_api/auth.py
# Version: v0.1.0
# Purpose: simple RBAC for Admin API (MVP). Replace later with SSO/OIDC.

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    role: str


def _role_rank(role: str) -> int:
    # viewer < ops < admin < superadmin
    order = {"viewer": 0, "ops": 1, "admin": 2, "superadmin": 3}
    return order.get(role, -1)


def get_actor_context(
    x_aicp_actor: Optional[str] = Header(default=""),
    x_aicp_role: Optional[str] = Header(default="viewer"),
) -> ActorContext:
    actor_id = (x_aicp_actor or "").strip()[:200]
    role = (x_aicp_role or "viewer").strip().lower()
    if role not in ("viewer", "ops", "admin", "superadmin"):
        role = "viewer"
    return ActorContext(actor_id=actor_id, role=role)


def require_min_role(
    min_role: str,
    x_aicp_token: Optional[str] = Header(default=""),
    x_aicp_actor: Optional[str] = Header(default=""),
    x_aicp_role: Optional[str] = Header(default="viewer"),
) -> ActorContext:
    """
    MVP auth:
      - any GET is allowed by route itself (viewer)
      - mutating endpoints require role >= admin AND token match.
    Headers:
      - X-AICP-Token: must match env AICP_ADMIN_TOKEN
      - X-AICP-Role: admin/superadmin
      - X-AICP-Actor: free-form id (username/email)
    """
    ctx = get_actor_context(x_aicp_actor=x_aicp_actor, x_aicp_role=x_aicp_role)

    if _role_rank(ctx.role) < _role_rank(min_role):
        raise HTTPException(status_code=403, detail="Insufficient role")

    expected = os.environ.get("AICP_ADMIN_TOKEN", "")
    if not expected or not x_aicp_token or x_aicp_token != expected:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    return ctx

# END_OF_FILE

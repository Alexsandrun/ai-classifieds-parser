# File: app/services/audit/repo.py
# Version: v0.1.0
# Purpose: Postgres audit writer for admin actions

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import psycopg


class AuditRepo:
    def __init__(self, *, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")

    def write_event(
        self,
        *,
        tenant_id: str,
        event_type: str,
        actor_id: str,
        actor_role: str,
        ip: str,
        user_agent: str,
        details: Dict[str, Any],
    ) -> None:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_events (tenant_id, event_type, actor_id, actor_role, ip, user_agent, details)
                    VALUES (%(t)s, %(etype)s, %(aid)s, %(arole)s, %(ip)s, %(ua)s, %(details)s::jsonb)
                    """,
                    {
                        "t": tenant_id,
                        "etype": event_type,
                        "aid": (actor_id or "")[:200],
                        "arole": (actor_role or "")[:50],
                        "ip": (ip or "")[:100],
                        "ua": (user_agent or "")[:500],
                        "details": psycopg.types.json.Jsonb(details),
                    },
                )
            conn.commit()

# END_OF_FILE

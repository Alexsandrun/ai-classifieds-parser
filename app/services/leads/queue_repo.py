# File: app/services/leads/queue_repo.py
# Version: v0.1.0
# Purpose: Postgres-backed leads queue (enqueue/claim/ack/expire/purge)

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import psycopg


@dataclass(frozen=True)
class ClaimedLead:
    lead_id: str
    created_at_utc: datetime
    expires_at_utc: datetime
    payload: Dict[str, Any]


class LeadsQueueRepo:
    """
    Queue semantics:
      - enqueue: inserts NEW lead with expires_at_utc
      - claim_batch: atomically claims oldest NEW leads (FIFO), returns payloads + claim_token
      - ack_delivered: marks delivered (only for same claim_token)
      - expire_overdue: marks NEW/CLAIMED -> EXPIRED when expires_at passed
      - purge_old: deletes old DELIVERED/EXPIRED/DROPPED/FAILED (policy-driven)
    """

    def __init__(self, *, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")

    def enqueue(
        self,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        ttl_days: int,
        lead_id: Optional[str] = None,
    ) -> str:
        lead_id = lead_id or str(uuid.uuid4())
        payload_json = json.dumps(payload, ensure_ascii=False)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO leads_queue (lead_id, tenant_id, expires_at_utc, status, payload)
                    VALUES (
                      %(lead_id)s,
                      %(tenant_id)s,
                      NOW() + (%(ttl_days)s::text || ' days')::interval,
                      'NEW',
                      %(payload)s::jsonb
                    )
                    """,
                    {
                        "lead_id": lead_id,
                        "tenant_id": tenant_id,
                        "ttl_days": int(ttl_days),
                        "payload": payload_json,
                    },
                )
            conn.commit()
        return lead_id

    def claim_batch(
        self,
        *,
        tenant_id: str,
        limit: int,
    ) -> Tuple[str, List[ClaimedLead]]:
        """
        Claims up to `limit` NEW non-expired leads (oldest first).
        Returns (claim_token, leads).
        """
        claim_token = str(uuid.uuid4())
        limit = int(limit)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH picked AS (
                      SELECT lead_id
                      FROM leads_queue
                      WHERE tenant_id = %(tenant_id)s
                        AND status = 'NEW'
                        AND expires_at_utc > NOW()
                      ORDER BY created_at_utc ASC
                      LIMIT %(limit)s
                      FOR UPDATE SKIP LOCKED
                    )
                    UPDATE leads_queue q
                    SET status = 'CLAIMED',
                        claim_token = %(claim_token)s,
                        claimed_at_utc = NOW()
                    FROM picked
                    WHERE q.lead_id = picked.lead_id
                    RETURNING q.lead_id, q.created_at_utc, q.expires_at_utc, q.payload
                    """,
                    {"tenant_id": tenant_id, "limit": limit, "claim_token": claim_token},
                )
                rows = cur.fetchall()

            conn.commit()

        leads: List[ClaimedLead] = []
        for lead_id, created_at, expires_at, payload in rows:
            leads.append(
                ClaimedLead(
                    lead_id=str(lead_id),
                    created_at_utc=created_at,
                    expires_at_utc=expires_at,
                    payload=dict(payload) if isinstance(payload, dict) else payload,
                )
            )

        return claim_token, leads

    def ack_delivered(
        self,
        *,
        tenant_id: str,
        claim_token: str,
        lead_ids: Sequence[str],
    ) -> int:
        if not lead_ids:
            return 0

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE leads_queue
                    SET status = 'DELIVERED',
                        delivered_at_utc = NOW()
                    WHERE tenant_id = %(tenant_id)s
                      AND claim_token = %(claim_token)s
                      AND lead_id = ANY(%(lead_ids)s)
                      AND status = 'CLAIMED'
                    """,
                    {"tenant_id": tenant_id, "claim_token": claim_token, "lead_ids": list(lead_ids)},
                )
                n = cur.rowcount
            conn.commit()
        return int(n)

    def mark_failed(
        self,
        *,
        tenant_id: str,
        lead_id: str,
        error: str,
        keep_claim_token: bool = True,
    ) -> int:
        """
        Marks lead as FAILED and increments attempts.
        """
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE leads_queue
                    SET status = 'FAILED',
                        attempts = attempts + 1,
                        last_error = %(error)s,
                        claim_token = CASE WHEN %(keep_claim_token)s THEN claim_token ELSE NULL END
                    WHERE tenant_id = %(tenant_id)s
                      AND lead_id = %(lead_id)s
                    """,
                    {"tenant_id": tenant_id, "lead_id": lead_id, "error": error, "keep_claim_token": bool(keep_claim_token)},
                )
                n = cur.rowcount
            conn.commit()
        return int(n)

    def expire_overdue(self, *, tenant_id: str) -> int:
        """
        NEW or CLAIMED and expired -> EXPIRED
        """
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE leads_queue
                    SET status = 'EXPIRED'
                    WHERE tenant_id = %(tenant_id)s
                      AND status IN ('NEW','CLAIMED')
                      AND expires_at_utc <= NOW()
                    """,
                    {"tenant_id": tenant_id},
                )
                n = cur.rowcount
            conn.commit()
        return int(n)

    def purge_old(
        self,
        *,
        tenant_id: str,
        older_than_days: int,
        statuses: Sequence[str] = ("DELIVERED", "EXPIRED", "DROPPED", "FAILED"),
    ) -> int:
        """
        Hard-delete old rows to reclaim storage.
        """
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM leads_queue
                    WHERE tenant_id = %(tenant_id)s
                      AND status = ANY(%(statuses)s)
                      AND created_at_utc < NOW() - (%(days)s::text || ' days')::interval
                    """,
                    {"tenant_id": tenant_id, "statuses": list(statuses), "days": int(older_than_days)},
                )
                n = cur.rowcount
            conn.commit()
        return int(n)

# END_OF_FILE

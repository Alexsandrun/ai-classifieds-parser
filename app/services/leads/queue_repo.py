# File: app/services/leads/queue_repo.py
# Version: v0.2.0
# Changes:
#  - add overflow guard (max_pending) + DROP_OLDEST_NEW policy
#  - add release_stale_claims (claim timeout)
#  - allow TTL/limits from tenant_settings via SettingsRepo (optional)
# Purpose: Postgres-backed leads queue (enqueue/claim/ack/expire/purge)

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import psycopg

from app.services.settings.defaults import (
    KEY_LEADS_CLAIM_TIMEOUT_MIN,
    KEY_LEADS_MAX_PENDING,
    KEY_LEADS_OVERFLOW_POLICY,
    KEY_LEADS_TTL_DAYS,
)
from app.services.settings.repo import SettingsRepo


@dataclass(frozen=True)
class ClaimedLead:
    lead_id: str
    created_at_utc: datetime
    expires_at_utc: datetime
    payload: Dict[str, Any]


class LeadsQueueRepo:
    """
    Queue semantics:
      - enqueue: inserts NEW lead with expires_at_utc (TTL)
      - claim_batch: atomically claims oldest NEW leads (FIFO)
      - ack_delivered: marks delivered (only for same claim_token)
      - expire_overdue: marks NEW/CLAIMED -> EXPIRED when expires_at passed
      - release_stale_claims: CLAIMED too long -> NEW (client died)
      - purge_old: deletes old DELIVERED/EXPIRED/DROPPED/FAILED (storage cleanup)

    Guardrails:
      - max_pending cap (NEW+CLAIMED)
      - overflow policy: DROP_OLDEST_NEW or REJECT
    """

    def __init__(self, *, dsn: Optional[str] = None, settings: Optional[SettingsRepo] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")
        self.settings = settings or SettingsRepo(dsn=self.dsn)

    # ---- settings helpers ----

    def _ttl_days(self, tenant_id: str, fallback: int) -> int:
        return self.settings.get_int(tenant_id=tenant_id, key=KEY_LEADS_TTL_DAYS, default=fallback, min_v=1, max_v=90)

    def _max_pending(self, tenant_id: str, fallback: int) -> int:
        return self.settings.get_int(tenant_id=tenant_id, key=KEY_LEADS_MAX_PENDING, default=fallback, min_v=100, max_v=2_000_000)

    def _claim_timeout_min(self, tenant_id: str, fallback: int) -> int:
        return self.settings.get_int(tenant_id=tenant_id, key=KEY_LEADS_CLAIM_TIMEOUT_MIN, default=fallback, min_v=1, max_v=24 * 60)

    def _overflow_policy(self, tenant_id: str, fallback: str = "DROP_OLDEST_NEW") -> str:
        v = self.settings.get_str(tenant_id=tenant_id, key=KEY_LEADS_OVERFLOW_POLICY, default=fallback)
        return v if v in ("DROP_OLDEST_NEW", "REJECT") else fallback

    # ---- core operations ----

    def enqueue(
        self,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        ttl_days: Optional[int] = None,
        lead_id: Optional[str] = None,
    ) -> str:
        lead_id = lead_id or str(uuid.uuid4())

        ttl = ttl_days if ttl_days is not None else self._ttl_days(tenant_id, fallback=14)
        max_pending = self._max_pending(tenant_id, fallback=50_000)
        overflow_policy = self._overflow_policy(tenant_id)

        payload_json = json.dumps(payload, ensure_ascii=False)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # 1) overflow guard before insert
                self._apply_overflow_guard(cur, tenant_id=tenant_id, max_pending=max_pending, policy=overflow_policy)

                # 2) insert lead
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
                        "ttl_days": int(ttl),
                        "payload": payload_json,
                    },
                )
            conn.commit()

        return lead_id

    def _apply_overflow_guard(self, cur: psycopg.Cursor, *, tenant_id: str, max_pending: int, policy: str) -> None:
        # Count pending (NEW+CLAIMED)
        cur.execute(
            """
            SELECT COUNT(*)
            FROM leads_queue
            WHERE tenant_id=%(t)s AND status IN ('NEW','CLAIMED')
            """,
            {"t": tenant_id},
        )
        row = cur.fetchone()
        pending = int(row[0]) if row and row[0] is not None else 0

        if pending < max_pending:
            return

        if policy == "REJECT":
            raise RuntimeError(f"leads_queue overflow: pending={pending} max_pending={max_pending} policy=REJECT")

        # DROP_OLDEST_NEW: drop enough NEW rows to make room for 1 new item
        excess = pending - max_pending + 1
        if excess <= 0:
            return

        # Drop only NEW (do not touch CLAIMED)
        cur.execute(
            """
            WITH to_drop AS (
              SELECT lead_id
              FROM leads_queue
              WHERE tenant_id=%(t)s AND status='NEW'
              ORDER BY created_at_utc ASC
              LIMIT %(excess)s
              FOR UPDATE SKIP LOCKED
            )
            UPDATE leads_queue
            SET status='DROPPED',
                last_error='overflow_drop_oldest_new'
            WHERE tenant_id=%(t)s AND lead_id IN (SELECT lead_id FROM to_drop)
            """,
            {"t": tenant_id, "excess": int(excess)},
        )

        # If we couldn't drop any NEW, we must reject to prevent infinite growth while client holds CLAIMED forever
        if cur.rowcount == 0:
            raise RuntimeError(f"leads_queue overflow: no NEW to drop (client stuck). pending={pending} max_pending={max_pending}")

    def claim_batch(
        self,
        *,
        tenant_id: str,
        limit: int,
    ) -> Tuple[str, List[ClaimedLead]]:
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

    def release_stale_claims(self, *, tenant_id: str, claim_timeout_minutes: Optional[int] = None) -> int:
        timeout_min = claim_timeout_minutes if claim_timeout_minutes is not None else self._claim_timeout_min(tenant_id, fallback=30)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE leads_queue
                    SET status='NEW',
                        claim_token=NULL,
                        claimed_at_utc=NULL
                    WHERE tenant_id=%(t)s
                      AND status='CLAIMED'
                      AND claimed_at_utc IS NOT NULL
                      AND claimed_at_utc < NOW() - (%(min)s::text || ' minutes')::interval
                      AND expires_at_utc > NOW()
                    """,
                    {"t": tenant_id, "min": int(timeout_min)},
                )
                n = cur.rowcount
            conn.commit()
        return int(n)

    def expire_overdue(self, *, tenant_id: str) -> int:
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

# File: tests/test_leads_queue.py
# Version: v0.1.0
# Purpose: integration test for leads queue (skips if PG not available)

from __future__ import annotations

import os

import pytest
import psycopg

from app.services.leads.queue_repo import LeadsQueueRepo


def _pg_available(dsn: str) -> bool:
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


def test_enqueue_claim_ack_flow():
    dsn = os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")
    if not _pg_available(dsn):
        pytest.skip("Postgres is not available for integration test")

    repo = LeadsQueueRepo(dsn=dsn)

    lead_id = repo.enqueue(tenant_id="default", payload={"listing_uid": "manual:x1", "score": 0.1}, ttl_days=7)
    claim_token, leads = repo.claim_batch(tenant_id="default", limit=10)

    assert any(lead.lead_id == lead_id for lead in leads)

    n = repo.ack_delivered(tenant_id="default", claim_token=claim_token, lead_ids=[lead_id])
    assert n == 1

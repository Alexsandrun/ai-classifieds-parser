# File: app/services/storage/pg_repo.py
# Version: v0.1.0
# Purpose: Postgres repository for current-state upserts

from __future__ import annotations

import json
import os
from typing import Optional

import psycopg

from app.core.contracts import Decision, ListingCanonical


class PostgresRepo:
    def __init__(self, *, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")

    def upsert_listing_current(
        self,
        *,
        tenant_id: str,
        listing: ListingCanonical,
        cluster_id: str,
        decision: Decision,
    ) -> None:
        reasons_json = json.dumps(decision.reasons, ensure_ascii=False)
        evidence_json = json.dumps(decision.evidence, ensure_ascii=False)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO listings_current (
                      tenant_id, listing_uid, source, source_listing_id, url,
                      title, description, published_at_utc, price, currency,
                      phone_hash, contact_name_norm, cluster_id,
                      decision_action, risk_score, reasons, evidence, updated_at_utc
                    )
                    VALUES (
                      %(tenant_id)s, %(listing_uid)s, %(source)s, %(source_listing_id)s, %(url)s,
                      %(title)s, %(description)s, %(published_at_utc)s, %(price)s, %(currency)s,
                      %(phone_hash)s, %(contact_name_norm)s, %(cluster_id)s,
                      %(decision_action)s, %(risk_score)s, %(reasons)s::jsonb, %(evidence)s::jsonb, NOW()
                    )
                    ON CONFLICT (listing_uid) DO UPDATE SET
                      tenant_id = EXCLUDED.tenant_id,
                      source = EXCLUDED.source,
                      source_listing_id = EXCLUDED.source_listing_id,
                      url = EXCLUDED.url,
                      title = EXCLUDED.title,
                      description = EXCLUDED.description,
                      published_at_utc = EXCLUDED.published_at_utc,
                      price = EXCLUDED.price,
                      currency = EXCLUDED.currency,
                      phone_hash = EXCLUDED.phone_hash,
                      contact_name_norm = EXCLUDED.contact_name_norm,
                      cluster_id = EXCLUDED.cluster_id,
                      decision_action = EXCLUDED.decision_action,
                      risk_score = EXCLUDED.risk_score,
                      reasons = EXCLUDED.reasons,
                      evidence = EXCLUDED.evidence,
                      updated_at_utc = NOW()
                    """,
                    {
                        "tenant_id": tenant_id,
                        "listing_uid": listing.listing_uid,
                        "source": listing.source,
                        "source_listing_id": listing.source_listing_id,
                        "url": listing.url,
                        "title": listing.title,
                        "description": listing.description,
                        "published_at_utc": listing.published_at_utc,
                        "price": listing.price,
                        "currency": listing.currency,
                        "phone_hash": listing.phone_hash,
                        "contact_name_norm": listing.contact_name_norm,
                        "cluster_id": cluster_id,
                        "decision_action": decision.action.value,
                        "risk_score": float(decision.risk_score),
                        "reasons": reasons_json,
                        "evidence": evidence_json,
                    },
                )
            conn.commit()

# END_OF_FILE

# File: app/main.py
# Version: v0.1.0
# Purpose: smoke pipeline (raw -> canon -> identity -> decision)

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.contracts import (
    Decision,
    DecisionAction,
    DecisionPacket,
    IdentityResult,
    IdentityResultPacket,
    ListingCanonical,
    ListingCanonicalPacket,
    ListingRaw,
    ListingRawPacket,
    Meta,
    guard_iface,
)

TENANT_SALT = "dev-tenant-salt-change-me"

IFACE_INGEST_RAW_ID = "IFACE-INGEST-RAW-001"
IFACE_INGEST_RAW_VER = "v0.1.0"

IFACE_PROCESS_CANON_ID = "IFACE-PROCESS-CANON-001"
IFACE_PROCESS_CANON_VER = "v0.1.0"

IFACE_IDENTITY_ID = "IFACE-IDENTITY-CLUSTER-001"
IFACE_IDENTITY_VER = "v0.1.0"

IFACE_DECISION_ID = "IFACE-DECISION-001"
IFACE_DECISION_VER = "v0.1.0"


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def normalize_phone_e164(phone_raw: Optional[str]) -> Optional[str]:
    if not phone_raw:
        return None
    digits = re.sub(r"\D+", "", phone_raw)
    if not digits:
        return None
    digits = digits.lstrip("0")
    if len(digits) < 9:
        return None
    return "+" + digits


def canonize(raw_pkt: ListingRawPacket) -> ListingCanonicalPacket:
    guard_iface(raw_pkt.meta, IFACE_INGEST_RAW_ID, IFACE_INGEST_RAW_VER, mode="STRICT")

    r = raw_pkt.data
    listing_uid = f"{r.source}:{r.source_listing_id}"

    phone_e164 = normalize_phone_e164(r.phone_raw)
    phone_hash = _sha256_hex(TENANT_SALT + ":" + phone_e164) if phone_e164 else None

    pub_utc: Optional[datetime] = None
    if r.published_at:
        pub_utc = r.published_at.astimezone(timezone.utc) if r.published_at.tzinfo else r.published_at.replace(tzinfo=timezone.utc)

    canon = ListingCanonical(
        listing_uid=listing_uid,
        source=r.source,
        source_listing_id=r.source_listing_id,
        url=r.url,
        title=r.title or "",
        description=r.description or "",
        published_at_utc=pub_utc,
        price=r.price,
        currency=r.currency,
        phone_e164=phone_e164,
        phone_hash=phone_hash,
        contact_name_norm=(r.contact_name or "").strip().lower() or None,
    )

    meta = Meta.now(
        iface_id=IFACE_PROCESS_CANON_ID,
        iface_version=IFACE_PROCESS_CANON_VER,
        trace_id=raw_pkt.meta.trace_id,
        producer="canonizer",
    )
    return ListingCanonicalPacket(meta=meta, data=canon)


def identity_cluster(canon_pkt: ListingCanonicalPacket) -> IdentityResultPacket:
    guard_iface(canon_pkt.meta, IFACE_PROCESS_CANON_ID, IFACE_PROCESS_CANON_VER, mode="STRICT")

    c = canon_pkt.data
    cluster_id = None
    confidence = 0.0
    signals = []

    if c.phone_hash:
        cluster_id = "cl_" + c.phone_hash[:16]
        confidence = 0.95
        signals.append("PHONE_HASH_PRESENT")

    meta = Meta.now(
        iface_id=IFACE_IDENTITY_ID,
        iface_version=IFACE_IDENTITY_VER,
        trace_id=canon_pkt.meta.trace_id,
        producer="identity_cluster",
    )
    return IdentityResultPacket(meta=meta, data=IdentityResult(cluster_id=cluster_id, confidence=confidence, signals=signals))


def decide(canon_pkt: ListingCanonicalPacket, ident_pkt: IdentityResultPacket) -> DecisionPacket:
    guard_iface(canon_pkt.meta, IFACE_PROCESS_CANON_ID, IFACE_PROCESS_CANON_VER, mode="STRICT")
    guard_iface(ident_pkt.meta, IFACE_IDENTITY_ID, IFACE_IDENTITY_VER, mode="STRICT")

    risk = 0.05
    reasons = ["BASELINE_OK"]
    evidence = []
    if ident_pkt.data.cluster_id and ident_pkt.data.confidence >= 0.9:
        evidence.append(f"cluster_id={ident_pkt.data.cluster_id} conf={ident_pkt.data.confidence}")

    meta = Meta.now(
        iface_id=IFACE_DECISION_ID,
        iface_version=IFACE_DECISION_VER,
        trace_id=canon_pkt.meta.trace_id,
        producer="decision_engine",
    )
    return DecisionPacket(
        meta=meta,
        data=Decision(action=DecisionAction.ALLOW, risk_score=risk, reasons=reasons, evidence=evidence),
    )


def demo() -> DecisionPacket:
    trace_id = str(uuid.uuid4())

    raw = ListingRaw(
        source="manual",
        source_listing_id="demo-001",
        url="https://example.com/listing/demo-001",
        title="2к квартира, центр",
        description="Срочно. Без комиссии.",
        published_at=datetime.now(timezone.utc),
        price=1200.0,
        currency="USD",
        contact_name="Agent",
        phone_raw="+38 (067) 123-45-67",
        raw_payload={"note": "demo"},
    )

    raw_pkt = ListingRawPacket(
        meta=Meta.now(
            iface_id=IFACE_INGEST_RAW_ID,
            iface_version=IFACE_INGEST_RAW_VER,
            trace_id=trace_id,
            producer="demo_ingest",
        ),
        data=raw,
    )

    canon_pkt = canonize(raw_pkt)
    ident_pkt = identity_cluster(canon_pkt)
    return decide(canon_pkt, ident_pkt)


if __name__ == "__main__":
    print(demo().model_dump())

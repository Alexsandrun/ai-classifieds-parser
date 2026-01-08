# File: tests/test_lists.py
# Version: v0.1.0
# Purpose: blacklist/whitelist matching + CSV import

from pathlib import Path

from app.main import (
    IFACE_DECISION_ID,
    IFACE_DECISION_VER,
    canonize,
    decide,
    identity_cluster,
)
from app.core.contracts import ListingRaw, ListingRawPacket, Meta
from app.services.lists.blacklist_store import BlacklistStore
from app.services.lists.whitelist_store import WhitelistStore
from app.services.lists.import_csv import import_csv_to_store


def _make_raw_pkt(phone_raw: str) -> ListingRawPacket:
    raw = ListingRaw(
        source="manual",
        source_listing_id="x1",
        url=None,
        title="t",
        description="d",
        published_at=None,
        price=None,
        currency=None,
        contact_name="Agent",
        phone_raw=phone_raw,
        raw_payload=None,
    )
    return ListingRawPacket(
        meta=Meta.now(
            iface_id="IFACE-INGEST-RAW-001",
            iface_version="v0.1.0",
            trace_id="test-trace",
            producer="test",
        ),
        data=raw,
    )


def test_blacklist_blocks_by_phone_hash():
    bl = BlacklistStore()
    bl.add_phone(phone_e164="+380671234567", category="FRAUD", notes="known bad", source="test")

    raw_pkt = _make_raw_pkt("+38 (067) 123-45-67")
    canon_pkt = canonize(raw_pkt)
    ident_pkt = identity_cluster(canon_pkt)

    decision_pkt = decide(canon_pkt, ident_pkt, blacklist=bl, whitelist=None)

    assert decision_pkt.meta.iface_id == IFACE_DECISION_ID
    assert decision_pkt.meta.iface_version == IFACE_DECISION_VER
    assert decision_pkt.data.action.value == "BLOCK"
    assert "BLACKLIST_PHONE" in decision_pkt.data.reasons


def test_whitelist_allows_by_phone_hash():
    wl = WhitelistStore()
    wl.add_phone(phone_e164="+380671234567", label="INTERNAL_AGENT", notes="staff", source="test")

    raw_pkt = _make_raw_pkt("+38 (067) 123-45-67")
    canon_pkt = canonize(raw_pkt)
    ident_pkt = identity_cluster(canon_pkt)

    decision_pkt = decide(canon_pkt, ident_pkt, blacklist=None, whitelist=wl)

    assert decision_pkt.data.action.value == "ALLOW"
    assert "WHITELIST_PHONE" in decision_pkt.data.reasons


def test_import_csv_to_blacklist(tmp_path: Path):
    csv_path = tmp_path / "bl.csv"
    csv_path.write_text("phone,category,notes\n+38 (067) 123-45-67,FRAUD,test\n", encoding="utf-8")

    bl = BlacklistStore()
    n = import_csv_to_store(path=csv_path, target="blacklist", blacklist=bl)
    assert n == 1

    raw_pkt = _make_raw_pkt("+38 (067) 123-45-67")
    canon_pkt = canonize(raw_pkt)
    assert bl.is_blacklisted_phone_hash(canon_pkt.data.phone_hash)

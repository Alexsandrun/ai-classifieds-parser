# File: app/services/lists/blacklist_store.py
# Version: v0.1.0
# Purpose: Blacklist storage + matching against ListingCanonical.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.contracts import ListingCanonical
from app.core.crypto import phone_hash_e164


class BlacklistEntry(BaseModel):
    """
    We store phone_hash as primary key.
    phone_e164 is optional (agency may allow storing it); hash is enough for matching.
    """
    model_config = ConfigDict(extra="forbid")

    phone_hash: str
    phone_e164: Optional[str] = None

    category: str = "UNKNOWN"  # e.g. FRAUD / SCAM / COMPETITOR_AGENT / RESELLER / OTHER
    notes: str = ""
    source: str = "manual"     # import/manual/api
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    added_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BlacklistMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matched: bool
    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class BlacklistStore:
    def __init__(self) -> None:
        self._by_phone_hash: Dict[str, BlacklistEntry] = {}

    def add_phone(
        self,
        *,
        phone_e164: str,
        category: str = "UNKNOWN",
        notes: str = "",
        source: str = "manual",
        confidence: float = 1.0,
        store_phone_e164: bool = False,
    ) -> BlacklistEntry:
        phash = phone_hash_e164(phone_e164)
        if not phash:
            raise ValueError("Invalid phone_e164 for hashing")
        entry = BlacklistEntry(
            phone_hash=phash,
            phone_e164=(phone_e164 if store_phone_e164 else None),
            category=category,
            notes=notes,
            source=source,
            confidence=confidence,
        )
        self._by_phone_hash[phash] = entry
        return entry

    def add_entry(self, entry: BlacklistEntry) -> None:
        self._by_phone_hash[entry.phone_hash] = entry

    def is_blacklisted_phone_hash(self, phone_hash: Optional[str]) -> bool:
        return bool(phone_hash) and (phone_hash in self._by_phone_hash)

    def match_listing(self, listing: ListingCanonical) -> BlacklistMatch:
        """
        Current MVP rule:
          if listing.phone_hash in blacklist => matched
        """
        if listing.phone_hash and listing.phone_hash in self._by_phone_hash:
            e = self._by_phone_hash[listing.phone_hash]
            return BlacklistMatch(
                matched=True,
                reasons=["BLACKLIST_PHONE"],
                evidence=[f"category={e.category} conf={e.confidence} source={e.source}"],
            )
        return BlacklistMatch(matched=False)

    def save_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.model_dump() for e in self._by_phone_hash.values()]
        path.write_text(__import__("json").dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> "BlacklistStore":
        store = cls()
        if not path.exists():
            return store
        raw = __import__("json").loads(path.read_text(encoding="utf-8"))
        for item in raw:
            store.add_entry(BlacklistEntry(**item))
        return store

# END_OF_FILE

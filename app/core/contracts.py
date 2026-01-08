# File: app/core/contracts.py
# Version: v0.1.0
# Changes: initial canonical contracts + interface meta + version guard
# Purpose: Canonical DTO + packet meta shared between modules.

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Meta(BaseModel):
    """
    Canonical metadata for any packet passed between modules.

    Required contract:
      - iface_id: stable interface id
      - iface_version: SemVer string like "v0.1.0" (NOT float)
      - trace_id: correlation id across pipeline
      - created_at: UTC datetime
      - producer: module name that produced the packet
    """
    model_config = ConfigDict(extra="forbid")

    iface_id: str
    iface_version: str
    trace_id: str
    created_at: datetime
    producer: str

    @staticmethod
    def now(*, iface_id: str, iface_version: str, trace_id: str, producer: str) -> "Meta":
        return Meta(
            iface_id=iface_id,
            iface_version=iface_version,
            trace_id=trace_id,
            created_at=datetime.now(timezone.utc),
            producer=producer,
        )


def guard_iface(meta: Meta, expected_id: str, expected_version: str, mode: Literal["STRICT", "WARN"] = "STRICT") -> None:
    """
    Interface version guard.

    STRICT: mismatch -> ValueError
    WARN: mismatch -> prints warning (replace with logger later)
    """
    if meta.iface_id == expected_id and meta.iface_version == expected_version:
        return

    msg = f"IFACE mismatch: got {meta.iface_id}/{meta.iface_version}, expected {expected_id}/{expected_version}"
    if mode == "STRICT":
        raise ValueError(msg)
    print("WARN:", msg)


class ListingRaw(BaseModel):
    """
    Raw listing as close to the source as possible (HTML/API/manual input).
    """
    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Source id e.g. avito, olx, manual")
    source_listing_id: str = Field(..., description="Listing id on the source (page id, internal id)")
    url: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[datetime] = None

    price: Optional[float] = None
    currency: Optional[str] = None

    contact_name: Optional[str] = None
    phone_raw: Optional[str] = None

    raw_payload: Optional[Dict[str, Any]] = Field(default=None, description="Optional raw parsed payload (JSON-like)")


class ListingRawPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    data: ListingRaw


class ListingCanonical(BaseModel):
    """
    Normalized/clean listing, safe for scoring & dedup.
    """
    model_config = ConfigDict(extra="forbid")

    listing_uid: str = Field(..., description="Stable internal id: source:source_listing_id")
    source: str
    source_listing_id: str
    url: Optional[str] = None

    title: str = ""
    description: str = ""
    published_at_utc: Optional[datetime] = None

    price: Optional[float] = None
    currency: Optional[str] = None

    phone_e164: Optional[str] = Field(default=None, description="Normalized phone (E.164) if known")
    phone_hash: Optional[str] = Field(default=None, description="sha256(tenant_salt + phone_e164)")
    contact_name_norm: Optional[str] = None


class ListingCanonicalPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    data: ListingCanonical


class IdentityResult(BaseModel):
    """
    SoftSeller Cluster ID = internal 'actor' cluster id inferred from weak signals.
    Purpose: group listings that likely belong to the same seller/agent even if they rotate phones.

    cluster_id is best-effort; confidence is 0..1; signals are explainability evidence.
    """
    model_config = ConfigDict(extra="forbid")

    cluster_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    signals: List[str] = Field(default_factory=list)


class IdentityResultPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    data: IdentityResult


class DecisionAction(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class Decision(BaseModel):
    """
    Final decision with explainability.
    risk_score: 0..1
    """
    model_config = ConfigDict(extra="forbid")

    action: DecisionAction
    risk_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class DecisionPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    data: Decision

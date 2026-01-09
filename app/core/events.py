# File: app/core/events.py
# Version: v0.1.0
# Purpose: canonical Event DTO for append-only analytics (ClickHouse)

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.contracts import DecisionAction, Meta


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = "default"

    event: str  # e.g. decision_made / blacklist_hit / snapshot_written
    source: str = ""
    listing_uid: str = ""
    cluster_id: str = ""

    action: Optional[DecisionAction] = None
    risk_score: float = 0.0

    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

    payload: Dict[str, Any] = Field(default_factory=dict)


class EventPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    data: Event

# END_OF_FILE

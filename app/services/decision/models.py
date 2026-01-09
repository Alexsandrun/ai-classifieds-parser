from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, ConfigDict

DecisionAction = Literal["ACCEPT", "DROP"]


class DecisionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: DecisionAction
    score: float = Field(ge=0.0, le=1.0)

    reason_codes: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)

    hard_block: bool = False
    soft_block: bool = False

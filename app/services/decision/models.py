# File: app/services/decision/models.py
# Version: v0.1.0
# Changes: initial decision models (score + explainability)
# Purpose: canonical decision output for filtering pipeline

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


DecisionAction = Literal["ACCEPT", "DROP"]


class DecisionResult(BaseModel):
    """
    Output of filtering decision.

    action:
      - ACCEPT: becomes a lead
      - DROP: ignored/rejected

    score:
      - 0..1 suspicion score (higher = more likely agent/fraud/spam)
      - For DROP by hard match, score can be 1.0
    """
    model_config = ConfigDict(extra="forbid")

    action: DecisionAction
    score: float = Field(ge=0.0, le=1.0)

    reason_codes: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)

    # convenience flags for UI/analytics
    hard_block: bool = False
    soft_block: bool = False

# END_OF_FILE

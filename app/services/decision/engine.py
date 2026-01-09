# File: app/services/decision/engine.py
# Version: v0.1.0
# Purpose: Decision Engine v0.1 (hard match + soft text heuristics + explainability)

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.services.decision.lists_facade import ListsFacade
from app.services.decision.models import DecisionResult


# ----------------------------
# Reason codes (canonical v0.1)
# ----------------------------
RC_BLACKLIST_PHONE = "BLACKLIST_PHONE_MATCH"
RC_WHITELIST_OWN = "WHITELIST_OWN_PHONE"          # own employees/own agents => skip lead
RC_AGENT_TEXT = "AGENT_TEXT_PATTERN"
RC_FRAUD_TEXT = "FRAUD_TEXT_PATTERN"


def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


@dataclass(frozen=True)
class DecisionConfig:
    """
    v0.1: small, fast and explainable.
    Later will be driven by tenant settings.
    """
    soft_block_threshold: float = 0.70  # score >= threshold => DROP
    agent_text_weight: float = 0.75
    fraud_text_weight: float = 0.90


AGENT_PATTERNS = [
    r"\bагент(ство)?\b",
    r"\bриелтор\b",
    r"\bкомисси(я|онные)\b",
    r"\bпосредник\b",
    r"\bуслуги\b.*\bриелтор",
    r"\bбез\s*посредников\b",  # often used by agents too; keep as weak signal later (v0.1 treat as signal)
    r"\bагентам?\s*не\s*беспокоить\b",  # can be owner, but many agents write it too; keep weak signal later
]

FRAUD_PATTERNS = [
    r"\bпредоплат[аы]\b",
    r"\bзадаток\b",
    r"\bскидк[аи]\b.*\bтолько\s*сегодня\b",
    r"\bперевод\b.*\bна\s*карт",
]


def _pattern_hit(text: str, patterns: list[str]) -> Optional[str]:
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return p
    return None


class DecisionEngine:
    def __init__(self, lists: ListsFacade, *, cfg: Optional[DecisionConfig] = None) -> None:
        self.lists = lists
        self.cfg = cfg or DecisionConfig()

    def decide(self, listing: Dict[str, Any]) -> DecisionResult:
        """
        listing (dict) expected keys (best effort):
          - phone_e164: str | None
          - text: str | None   (title+description combined ideally)
        """
        phone = (listing.get("phone_e164") or "").strip()
        text = _norm_text(str(listing.get("text") or ""))

        evidence: Dict[str, Any] = {}

        # 1) Own whitelist => skip (DROP)
        if phone and self.lists.is_whitelisted_phone(phone):
            return DecisionResult(
                action="DROP",
                score=0.0,
                reason_codes=[RC_WHITELIST_OWN],
                evidence={"phone_e164": phone},
                hard_block=True,
                soft_block=False,
            )

        # 2) Blacklist hard match => DROP
        if phone and self.lists.is_blacklisted_phone(phone):
            return DecisionResult(
                action="DROP",
                score=1.0,
                reason_codes=[RC_BLACKLIST_PHONE],
                evidence={"phone_e164": phone},
                hard_block=True,
                soft_block=False,
            )

        # 3) Soft heuristics (text patterns)
        score = 0.0
        reason_codes: list[str] = []

        hit_agent = _pattern_hit(text, AGENT_PATTERNS) if text else None
        if hit_agent:
            score = max(score, self.cfg.agent_text_weight)
            reason_codes.append(RC_AGENT_TEXT)
            evidence["agent_pattern"] = hit_agent

        hit_fraud = _pattern_hit(text, FRAUD_PATTERNS) if text else None
        if hit_fraud:
            score = max(score, self.cfg.fraud_text_weight)
            reason_codes.append(RC_FRAUD_TEXT)
            evidence["fraud_pattern"] = hit_fraud

        # Decide
        if score >= self.cfg.soft_block_threshold:
            return DecisionResult(
                action="DROP",
                score=min(1.0, score),
                reason_codes=reason_codes,
                evidence=evidence,
                hard_block=False,
                soft_block=True,
            )

        return DecisionResult(
            action="ACCEPT",
            score=min(1.0, score),
            reason_codes=reason_codes,
            evidence=evidence,
            hard_block=False,
            soft_block=False,
        )

# END_OF_FILE

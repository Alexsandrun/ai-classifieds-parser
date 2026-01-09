# File: app/services/decision/lists_facade.py
# Version: v0.1.0
# Purpose: abstraction layer for blacklist/whitelist checks (fast & swappable)

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol


class ListsFacade(Protocol):
    """
    Minimal interface needed by DecisionEngine.
    Whitelist semantics in our project = "own/known agents => skip" (DROP).
    """
    def is_blacklisted_phone(self, phone_e164: str) -> bool: ...
    def is_whitelisted_phone(self, phone_e164: str) -> bool: ...


@dataclass
class InMemoryListsFacade:
    black_phones: set[str]
    white_phones: set[str]

    def is_blacklisted_phone(self, phone_e164: str) -> bool:
        return phone_e164 in self.black_phones

    def is_whitelisted_phone(self, phone_e164: str) -> bool:
        return phone_e164 in self.white_phones


def _try_call(obj: Any, method: str, *args: Any) -> Optional[Any]:
    fn = getattr(obj, method, None)
    if callable(fn):
        return fn(*args)
    return None


@dataclass
class StoreListsFacade:
    """
    Adapter for existing stores in app/services/lists/*.
    We intentionally support several possible method names to avoid refactors.
    """
    blacklist_store: Any
    whitelist_store: Any

    def is_blacklisted_phone(self, phone_e164: str) -> bool:
        # common method patterns
        for m in ("is_phone_blocked", "is_blacklisted_phone", "contains_phone", "has_phone", "match_phone_e164", "match_phone"):
            v = _try_call(self.blacklist_store, m, phone_e164)
            if isinstance(v, bool):
                return v

        # fallback: try known attributes
        idx = getattr(self.blacklist_store, "phone_e164_set", None) or getattr(self.blacklist_store, "phones_e164", None)
        if isinstance(idx, set):
            return phone_e164 in idx

        return False

    def is_whitelisted_phone(self, phone_e164: str) -> bool:
        for m in ("is_phone_whitelisted", "is_whitelisted_phone", "contains_phone", "has_phone", "match_phone_e164", "match_phone"):
            v = _try_call(self.whitelist_store, m, phone_e164)
            if isinstance(v, bool):
                return v

        idx = getattr(self.whitelist_store, "phone_e164_set", None) or getattr(self.whitelist_store, "phones_e164", None)
        if isinstance(idx, set):
            return phone_e164 in idx

        return False

# END_OF_FILE

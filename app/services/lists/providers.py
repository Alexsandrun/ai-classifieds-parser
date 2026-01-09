# File: app/services/lists/providers.py
# Version: v0.1.0
# Purpose: provider switch for lists (blacklist/whitelist) by deployment mode

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.deployment import DeploymentMode, get_deployment_mode


@dataclass(frozen=True)
class ListsProviders:
    """
    Wiring object: holds concrete list providers.

    Design goal:
      - SINGLE_TENANT: uses agency/client-managed lists (stored/managed on that instance)
      - VENDOR_FEED: uses only vendor-managed lists (no agency imports exist on this instance)
    """
    blacklist: object
    whitelist: object
    mode: DeploymentMode


def get_lists_providers(*, mode: Optional[DeploymentMode] = None) -> ListsProviders:
    """
    Returns the correct provider set for current deployment mode.
    IMPORTANT: This function does not create/keep 'disabled' lists in DB.
    In vendor_feed mode we simply never instantiate/use agency-import related providers.
    """
    mode = mode or get_deployment_mode()

    # Local imports: avoids import-time coupling and keeps startup flexible.
    from app.services.lists.blacklist_store import BlacklistStore
    from app.services.lists.whitelist_store import WhitelistStore

    if mode == DeploymentMode.VENDOR_FEED:
        # Vendor feed server: vendor-only lists.
        # For MVP we reuse the same store classes, but the instance/data on this server is vendor-owned only.
        # Later we can swap to specialized vendor index (e.g., redis/bloom/cached sets) without changing callers.
        blacklist = BlacklistStore()
        whitelist = WhitelistStore()
        return ListsProviders(blacklist=blacklist, whitelist=whitelist, mode=mode)

    # Single-tenant dedicated server: agency/client-managed lists.
    blacklist = BlacklistStore()
    whitelist = WhitelistStore()
    return ListsProviders(blacklist=blacklist, whitelist=whitelist, mode=mode)

# File: app/core/deployment.py
# Version: v0.1.0
# Purpose: deployment mode selector (single tenant vs vendor feed)

from __future__ import annotations

import os
from enum import Enum


class DeploymentMode(str, Enum):
    SINGLE_TENANT = "single_tenant"   # customer dedicated / on-prem
    VENDOR_FEED = "vendor_feed"       # our multi-client feed server (vendor-only lists)


def get_deployment_mode() -> DeploymentMode:
    raw = (os.environ.get("AICP_DEPLOYMENT_MODE", "") or "").strip().lower()
    if raw == DeploymentMode.VENDOR_FEED.value:
        return DeploymentMode.VENDOR_FEED
    return DeploymentMode.SINGLE_TENANT

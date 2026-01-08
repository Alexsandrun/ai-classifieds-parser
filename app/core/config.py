# File: app/core/config.py
# Version: v0.1.0
# Purpose: runtime config (tenant salt, data paths)

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
LISTS_DIR = DATA_DIR / "lists"

TENANT_SALT = os.environ.get("AICP_TENANT_SALT", "dev-tenant-salt-change-me")

# END_OF_FILE

# File: app/services/settings/repo.py
# Version: v0.1.0
# Purpose: tenant settings repo (jsonb key/value) + typed helpers

from __future__ import annotations



import os
from dataclasses import dataclass
from typing import Any, Optional

import psycopg
from psycopg.types.json import Jsonb



@dataclass(frozen=True)
class SettingItem:
    tenant_id: str
    key: str
    value: Any


class SettingsRepo:
    """
    Single source of truth for runtime policies (later controlled by Admin UI).
    Stores jsonb values under (tenant_id, key).
    """

    def __init__(self, *, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")

    def get_json(self, *, tenant_id: str, key: str) -> Optional[Any]:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT value FROM tenant_settings WHERE tenant_id=%(t)s AND key=%(k)s",
                    {"t": tenant_id, "k": key},
                )
                row = cur.fetchone()
                if not row:
                    return None
                return row[0]

    def set_json(self, *, tenant_id: str, key: str, value: Any) -> None:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tenant_settings (tenant_id, key, value, updated_at_utc)
                    VALUES (%(t)s, %(k)s, %(v)s::jsonb, NOW())
                    ON CONFLICT (tenant_id, key) DO UPDATE SET
                      value = EXCLUDED.value,
                      updated_at_utc = NOW()
                    """,
                    {"t": tenant_id, "k": key, "v": Jsonb(value)},
                )
            conn.commit()

    # ---- typed helpers (safe defaults) ----

    def get_int(self, *, tenant_id: str, key: str, default: int, min_v: int | None = None, max_v: int | None = None) -> int:
        v = self.get_json(tenant_id=tenant_id, key=key)
        if v is None:
            return default
        try:
            n = int(v)
        except Exception:
            return default
        if min_v is not None and n < min_v:
            n = min_v
        if max_v is not None and n > max_v:
            n = max_v
        return n

    def get_str(self, *, tenant_id: str, key: str, default: str) -> str:
        v = self.get_json(tenant_id=tenant_id, key=key)
        return default if v is None else str(v)

# END_OF_FILE

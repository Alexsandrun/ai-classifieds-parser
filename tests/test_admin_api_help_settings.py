# File: tests/test_admin_api_help_settings.py
# Version: v0.1.0
# Purpose: basic API tests for help/settings endpoints

from __future__ import annotations

import os
import pytest
import psycopg
from fastapi.testclient import TestClient

from app.admin_api.main import app


def _pg_available(dsn: str) -> bool:
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


def test_help_page():
    c = TestClient(app)
    r = c.get("/api/help/leads")
    assert r.status_code == 200
    data = r.json()
    assert data["page_id"] == "leads"
    assert "fields" in data
    assert any(f["key"] == "leads.ttl_days" for f in data["fields"])


def test_settings_validation_skips_without_pg():
    dsn = os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")
    if not _pg_available(dsn):
        pytest.skip("Postgres not available for settings tests")

    c = TestClient(app)

    # invalid: ttl too small
    r = c.put("/api/settings/default/leads.ttl_days", json={"value": 0})
    assert r.status_code == 400

    # valid
    r = c.put("/api/settings/default/leads.ttl_days", json={"value": 14})
    assert r.status_code == 200

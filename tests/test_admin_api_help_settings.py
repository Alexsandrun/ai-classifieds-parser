# File: tests/test_admin_api_help_settings.py
# Version: v0.2.0
# Changes:
#  - settings PUT requires admin token/role
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
    assert any(f["key"] == "leads.ttl_days" for f in data["fields"])


def test_settings_put_requires_admin_token(monkeypatch):
    dsn = os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")
    if not _pg_available(dsn):
        pytest.skip("Postgres not available for settings tests")

    monkeypatch.setenv("AICP_ADMIN_TOKEN", "dev_admin_token")

    c = TestClient(app)

    # No token -> forbidden
    r = c.put("/api/settings/default/leads.ttl_days", json={"value": 14})
    assert r.status_code == 403

    # With token + admin role -> OK
    headers = {
        "X-AICP-Token": "dev_admin_token",
        "X-AICP-Role": "admin",
        "X-AICP-Actor": "test-admin",
    }
    r = c.put("/api/settings/default/leads.ttl_days", headers=headers, json={"value": 14})
    assert r.status_code == 200

    # Invalid value -> 400
    r = c.put("/api/settings/default/leads.ttl_days", headers=headers, json={"value": 0})
    assert r.status_code == 400

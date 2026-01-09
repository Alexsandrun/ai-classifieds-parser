# File: tests/test_runtime.py
# Version: v0.1.0
# Purpose: verify runtime endpoint works

from __future__ import annotations

from fastapi.testclient import TestClient

from app.admin_api.main import app


def test_runtime_endpoint():
    c = TestClient(app)
    r = c.get("/api/runtime")
    assert r.status_code == 200
    data = r.json()
    assert data["deployment_mode"] in ("single_tenant", "vendor_feed")
    assert "config_path" in data

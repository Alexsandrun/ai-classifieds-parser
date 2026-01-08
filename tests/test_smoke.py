# File: tests/test_smoke.py
# Version: v0.1.1
# Purpose: smoke test for demo pipeline (DecisionPacket meta)

from app.main import demo, IFACE_DECISION_ID, IFACE_DECISION_VER


def test_demo_pipeline_returns_decision_packet():
    pkt = demo()
    assert pkt.meta.iface_id == IFACE_DECISION_ID
    assert pkt.meta.iface_version == IFACE_DECISION_VER
    assert 0.0 <= pkt.data.risk_score <= 1.0

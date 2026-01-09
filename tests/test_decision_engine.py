# File: tests/test_decision_engine.py
# Version: v0.1.0
# Purpose: Decision Engine v0.1 tests

from __future__ import annotations

from app.services.decision.engine import (
    DecisionEngine,
    RC_BLACKLIST_PHONE,
    RC_WHITELIST_OWN,
    RC_AGENT_TEXT,
    RC_FRAUD_TEXT,
)
from app.services.decision.lists_facade import InMemoryListsFacade


def test_drop_on_whitelist_own_phone():
    lists = InMemoryListsFacade(black_phones=set(), white_phones={"+380991112233"})
    eng = DecisionEngine(lists)
    res = eng.decide({"phone_e164": "+380991112233", "text": "Owner listing"})
    assert res.action == "DROP"
    assert RC_WHITELIST_OWN in res.reason_codes


def test_drop_on_blacklist_phone():
    lists = InMemoryListsFacade(black_phones={"+380991112233"}, white_phones=set())
    eng = DecisionEngine(lists)
    res = eng.decide({"phone_e164": "+380991112233", "text": "Any"})
    assert res.action == "DROP"
    assert RC_BLACKLIST_PHONE in res.reason_codes
    assert res.score == 1.0


def test_soft_drop_on_agent_text():
    lists = InMemoryListsFacade(black_phones=set(), white_phones=set())
    eng = DecisionEngine(lists)
    res = eng.decide({"phone_e164": "", "text": "Работаю риелтор, комиссия 3%."})
    assert res.action == "DROP"
    assert RC_AGENT_TEXT in res.reason_codes


def test_soft_drop_on_fraud_text():
    lists = InMemoryListsFacade(black_phones=set(), white_phones=set())
    eng = DecisionEngine(lists)
    res = eng.decide({"phone_e164": "", "text": "Нужна предоплата, перевод на карту."})
    assert res.action == "DROP"
    assert RC_FRAUD_TEXT in res.reason_codes


def test_accept_clean_text():
    lists = InMemoryListsFacade(black_phones=set(), white_phones=set())
    eng = DecisionEngine(lists)
    res = eng.decide({"phone_e164": "", "text": "Сдам квартиру, собственник. Центр."})
    assert res.action == "ACCEPT"

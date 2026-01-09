# File: tests/test_backup_monitor_logic.py
# Version: v0.1.0
# Purpose: unit tests for backup monitoring logic

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.backup.monitor_logic import BackupEvalInput, eval_backup


def test_stale_when_no_success():
    now = datetime.now(timezone.utc)
    res = eval_backup(
        BackupEvalInput(
            job_id="pg_daily",
            title="PG Daily",
            target_hint="S3",
            max_staleness_hours=36,
            fail_warn_threshold=3,
            fail_crit_threshold=6,
            severity_on_stale="CRITICAL",
            severity_on_fail="WARN",
            last_success_at=None,
            last_run_status="FAIL",
            last_run_at=now - timedelta(hours=1),
            consecutive_failures=2,
            now_utc=now,
        )
    )
    assert res.state == "ALERT"
    assert res.alert_type == "stale"


def test_stale_when_success_too_old():
    now = datetime.now(timezone.utc)
    last_success = now - timedelta(hours=50)
    res = eval_backup(
        BackupEvalInput(
            job_id="pg_daily",
            title="PG Daily",
            target_hint="S3",
            max_staleness_hours=36,
            fail_warn_threshold=3,
            fail_crit_threshold=6,
            severity_on_stale="CRITICAL",
            severity_on_fail="WARN",
            last_success_at=last_success,
            last_run_status="FAIL",
            last_run_at=now - timedelta(hours=2),
            consecutive_failures=5,
            now_utc=now,
        )
    )
    assert res.state == "ALERT"
    assert res.alert_type == "stale"


def test_fail_escalation_warn():
    now = datetime.now(timezone.utc)
    last_success = now - timedelta(hours=10)
    res = eval_backup(
        BackupEvalInput(
            job_id="pg_daily",
            title="PG Daily",
            target_hint="S3",
            max_staleness_hours=36,
            fail_warn_threshold=3,
            fail_crit_threshold=6,
            severity_on_stale="CRITICAL",
            severity_on_fail="WARN",
            last_success_at=last_success,
            last_run_status="FAIL",
            last_run_at=now - timedelta(minutes=10),
            consecutive_failures=3,
            now_utc=now,
        )
    )
    assert res.state == "ALERT"
    assert res.alert_type == "fail"


def test_ok_when_recent_success_no_failures():
    now = datetime.now(timezone.utc)
    last_success = now - timedelta(hours=1)
    res = eval_backup(
        BackupEvalInput(
            job_id="pg_daily",
            title="PG Daily",
            target_hint="S3",
            max_staleness_hours=36,
            fail_warn_threshold=3,
            fail_crit_threshold=6,
            severity_on_stale="CRITICAL",
            severity_on_fail="WARN",
            last_success_at=last_success,
            last_run_status="SUCCESS",
            last_run_at=now - timedelta(hours=1),
            consecutive_failures=0,
            now_utc=now,
        )
    )
    assert res.state == "OK"
    assert res.alert_type == "none"

# File: app/services/backup/monitor_logic.py
# Version: v0.1.0
# Purpose: pure decision logic for backup monitoring (stale/fail/recovered)

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class BackupEvalInput:
    job_id: str
    title: str
    target_hint: str

    max_staleness_hours: int
    fail_warn_threshold: int
    fail_crit_threshold: int

    severity_on_stale: str  # WARN/CRITICAL
    severity_on_fail: str   # WARN/CRITICAL

    last_success_at: Optional[datetime]
    last_run_status: Optional[str]
    last_run_at: Optional[datetime]
    consecutive_failures: int

    now_utc: datetime


@dataclass(frozen=True)
class BackupEvalResult:
    state: str               # OK/ALERT
    alert_type: str          # none/stale/fail
    severity: str            # INFO/WARN/CRITICAL
    message: str


def _hours_since(now: datetime, t: Optional[datetime]) -> Optional[float]:
    if t is None:
        return None
    return (now - t).total_seconds() / 3600.0


def eval_backup(inp: BackupEvalInput) -> BackupEvalResult:
    now = inp.now_utc
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    hrs_since_success = _hours_since(now, inp.last_success_at)

    # 1) STALE: no success ever OR too old
    if inp.last_success_at is None:
        # If never succeeded, treat as stale (alert), but message is explicit.
        sev = inp.severity_on_stale
        msg = (
            f"🔴 Backup missing: {inp.job_id}\n"
            f"{inp.title}\n"
            f"Target: {inp.target_hint or '-'}\n"
            f"Last success: never\n"
            f"Last run: {inp.last_run_status or 'none'}\n"
            f"Consecutive fails: {inp.consecutive_failures}\n"
            f"Action: проверь бэкап-сервер/доступ/оплату/место"
        )
        return BackupEvalResult(state="ALERT", alert_type="stale", severity=sev, message=msg)

    if hrs_since_success is not None and hrs_since_success > float(inp.max_staleness_hours):
        sev = inp.severity_on_stale
        msg = (
            f"🔴 Backup stale: {inp.job_id}\n"
            f"{inp.title}\n"
            f"Target: {inp.target_hint or '-'}\n"
            f"Last success: {inp.last_success_at.isoformat()}\n"
            f"Stale for: {hrs_since_success:.1f}h (limit {inp.max_staleness_hours}h)\n"
            f"Last run: {inp.last_run_status or 'none'} at {inp.last_run_at.isoformat() if inp.last_run_at else '-'}\n"
            f"Consecutive fails: {inp.consecutive_failures}\n"
            f"Action: проверь ключи/оплату/место/сеть"
        )
        return BackupEvalResult(state="ALERT", alert_type="stale", severity=sev, message=msg)

    # 2) FAIL escalation (even if not stale yet)
    if inp.consecutive_failures >= inp.fail_crit_threshold:
        sev = "CRITICAL"
        msg = (
            f"🔴 Backup failing (CRIT): {inp.job_id}\n"
            f"{inp.title}\n"
            f"Last success: {inp.last_success_at.isoformat()}\n"
            f"Consecutive fails: {inp.consecutive_failures}\n"
            f"Action: срочно проверь бэкап/доступ/место"
        )
        return BackupEvalResult(state="ALERT", alert_type="fail", severity=sev, message=msg)

    if inp.consecutive_failures >= inp.fail_warn_threshold:
        sev = inp.severity_on_fail
        msg = (
            f"🟠 Backup failing: {inp.job_id}\n"
            f"{inp.title}\n"
            f"Last success: {inp.last_success_at.isoformat()}\n"
            f"Consecutive fails: {inp.consecutive_failures}\n"
            f"Action: проверь бэкап/доступ/место"
        )
        return BackupEvalResult(state="ALERT", alert_type="fail", severity=sev, message=msg)

    # OK
    msg = (
        f"✅ Backup OK: {inp.job_id}\n"
        f"{inp.title}\n"
        f"Last success: {inp.last_success_at.isoformat()}\n"
    )
    return BackupEvalResult(state="OK", alert_type="none", severity="INFO", message=msg)

# END_OF_FILE

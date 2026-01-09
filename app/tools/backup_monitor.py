# File: app/tools/backup_monitor.py
# Version: v0.1.0
# Purpose: monitor backup health and send alerts (anti-spam)

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from app.services.backup.monitor_logic import BackupEvalInput, eval_backup
from app.services.backup.monitor_repo import BackupMonitorRepo
from app.services.notify.telegram import TelegramNotifier


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", default="default")
    ap.add_argument("--cooldown-minutes", type=int, default=int(os.environ.get("AICP_ALERT_COOLDOWN_MIN", "360")))
    ap.add_argument("--ensure-default-jobs", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = BackupMonitorRepo()
    if args.ensure_default_jobs:
        ins = repo.ensure_default_jobs(tenant_id=args.tenant)
        print(f"OK: ensured default jobs inserted={ins}")

    tg = TelegramNotifier()

    now = datetime.now(timezone.utc)
    jobs = repo.list_jobs(tenant_id=args.tenant)
    print(f"Monitor: tenant={args.tenant} jobs={len(jobs)} telegram_enabled={tg.enabled} dry_run={args.dry_run}")

    for j in jobs:
        if not j.enabled:
            continue

        st = repo.get_job_stats(tenant_id=j.tenant_id, job_id=j.job_id)
        res = eval_backup(
            BackupEvalInput(
                job_id=j.job_id,
                title=j.title or j.job_id,
                target_hint=j.target_hint or "",
                max_staleness_hours=j.max_staleness_hours,
                fail_warn_threshold=j.fail_warn_threshold,
                fail_crit_threshold=j.fail_crit_threshold,
                severity_on_stale=j.severity_on_stale,
                severity_on_fail=j.severity_on_fail,
                last_success_at=st.last_success_at,
                last_run_status=st.last_run_status,
                last_run_at=st.last_run_at,
                consecutive_failures=st.consecutive_failures,
                now_utc=now,
            )
        )

        # Print summary always
        print(f"- {j.job_id}: state={res.state} type={res.alert_type} severity={res.severity}")

        # Determine alert key & desired stored state
        if res.state == "ALERT":
            alert_key = f"backup:{j.job_id}:{res.alert_type}"
            desired_state = "ALERT"
            send_allowed = repo.should_send_alert(
                tenant_id=j.tenant_id,
                alert_key=alert_key,
                payload_text=res.message,
                cooldown_minutes=args.cooldown_minutes,
                desired_state=desired_state,
            )
            if send_allowed and j.notify_telegram:
                if args.dry_run:
                    print(f"  DRY_RUN would send Telegram: {alert_key}")
                else:
                    ok = tg.send(res.message) if tg.enabled else False
                    print(f"  sent={ok} alert_key={alert_key} (tg_enabled={tg.enabled})")
                    repo.mark_sent(tenant_id=j.tenant_id, alert_key=alert_key, payload_text=res.message, new_state=desired_state)
        else:
            # Recovery message: if any alert state existed, we'd send once on transition.
            # Implemented as: check stale alert key only (common), and if state changed -> send.
            # Here we send "recovered" message for both stale and fail keys.
            for t in ("stale", "fail"):
                alert_key = f"backup:{j.job_id}:{t}"
                desired_state = "OK"
                recovered_msg = f"✅ Backup recovered: {j.job_id}\n{j.title}\nTime: {now.isoformat()}"
                send_allowed = repo.should_send_alert(
                    tenant_id=j.tenant_id,
                    alert_key=alert_key,
                    payload_text=recovered_msg,
                    cooldown_minutes=args.cooldown_minutes,
                    desired_state=desired_state,
                )
                if send_allowed and j.notify_telegram:
                    if args.dry_run:
                        print(f"  DRY_RUN would send Telegram recovery: {alert_key}")
                    else:
                        ok = tg.send(recovered_msg) if tg.enabled else False
                        print(f"  recovery_sent={ok} alert_key={alert_key}")
                        repo.mark_sent(tenant_id=j.tenant_id, alert_key=alert_key, payload_text=recovered_msg, new_state=desired_state)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


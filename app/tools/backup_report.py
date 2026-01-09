# File: app/tools/backup_report.py
# Version: v0.1.0
# Purpose: record backup run (SUCCESS/FAIL) into Postgres

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Optional

from app.services.backup.monitor_repo import BackupMonitorRepo


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    # ISO8601 preferred
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", default="default")
    ap.add_argument("--job", required=True)
    ap.add_argument("--status", required=True, choices=["SUCCESS", "FAIL"])
    ap.add_argument("--started-at", default=None, help="ISO datetime, e.g. 2026-01-09T10:00:00Z")
    ap.add_argument("--ended-at", default=None)
    ap.add_argument("--size-bytes", type=int, default=0)
    ap.add_argument("--artifact", default="")
    ap.add_argument("--error", default="")
    ap.add_argument("--ensure-default-jobs", action="store_true")
    args = ap.parse_args()

    repo = BackupMonitorRepo()

    if args.ensure_default_jobs:
        ins = repo.ensure_default_jobs(tenant_id=args.tenant)
        print(f"OK: ensured default jobs inserted={ins}")

    repo.insert_run(
        tenant_id=args.tenant,
        job_id=args.job,
        status=args.status,
        started_at_utc=_parse_dt(args.started_at),
        ended_at_utc=_parse_dt(args.ended_at),
        size_bytes=int(args.size_bytes),
        artifact_name=args.artifact,
        error_text=args.error,
    )

    print(f"OK: recorded run tenant={args.tenant} job={args.job} status={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


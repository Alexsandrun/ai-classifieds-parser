# File: app/tools/leads_janitor.py
# Version: v0.1.0
# Purpose: expire/purge leads queue (TTL enforcement & storage cleanup)

from __future__ import annotations

import argparse

from app.services.leads.queue_repo import LeadsQueueRepo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", default="default")
    ap.add_argument("--purge-older-than-days", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = LeadsQueueRepo()

    # Expire overdue (status NEW/CLAIMED)
    expired = 0
    purged = 0

    if args.dry_run:
        print("DRY_RUN: would expire overdue and purge old leads")
        return 0

    expired = repo.expire_overdue(tenant_id=args.tenant)
    purged = repo.purge_old(tenant_id=args.tenant, older_than_days=args.purge_older_than_days)

    print(f"OK: tenant={args.tenant} expired={expired} purged={purged} purge_older_than_days={args.purge_older_than_days}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


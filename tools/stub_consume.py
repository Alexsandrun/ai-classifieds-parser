# File: tools/stub_consume.py
# Version: v0.1.1
# Changes: fix ruff E741 (rename l->lead); full file rewrite
# Purpose: Claim leads from Postgres queue and optionally ACK them (simulate CRM/agency).

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# --- path bootstrap (allows: uv run python tools/stub_consume.py ...) ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.leads.queue_repo import LeadsQueueRepo  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tenant", default="default")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--ack", action="store_true", help="mark claimed leads as DELIVERED")
    p.add_argument("--pretty", action="store_true", help="pretty-print JSON payload")
    args = p.parse_args()

    dsn = os.environ.get("AICP_PG_DSN")
    repo = LeadsQueueRepo(dsn=dsn)

    claim_token, leads = repo.claim_batch(tenant_id=args.tenant, limit=int(args.limit))

    print(f"OK: claimed {len(leads)} leads tenant={args.tenant} claim_token={claim_token}")

    for lead in leads:
        payload = lead.payload
        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))

    if args.ack and leads:
        n = repo.ack_delivered(
            tenant_id=args.tenant,
            claim_token=claim_token,
            lead_ids=[lead.lead_id for lead in leads],
        )
        print(f"OK: ack_delivered={n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# END_OF_FILE

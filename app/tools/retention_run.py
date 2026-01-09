# File: app/tools/retention_run.py
# Version: v0.1.0
# Purpose: CLI runner for retention manager

from __future__ import annotations

import argparse
from pathlib import Path

from app.services.retention.manager import RetentionManager
from app.services.retention.policy import load_retention_config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/retention.json")
    ap.add_argument("--execute", action="store_true", help="Apply deletions. Default is dry-run.")
    ap.add_argument("--force-mode", choices=["NORMAL", "WARN", "CRITICAL"], default=None)

    ap.add_argument("--ch-host", default="localhost")
    ap.add_argument("--ch-port", type=int, default=8123)
    ap.add_argument("--ch-user", default="aicp")
    ap.add_argument("--ch-password", default="aicp_dev_password")

    args = ap.parse_args()

    cfg = load_retention_config(Path(args.config))
    mgr = RetentionManager(cfg)

    res = mgr.run(
        execute=bool(args.execute),
        force_mode=args.force_mode,
        ch_host=args.ch_host,
        ch_port=args.ch_port,
        ch_user=args.ch_user,
        ch_password=args.ch_password,
    )

    print(f"Retention mode={res.mode} disk_free={res.disk_free_percent:.2f}% execute={bool(args.execute)}")
    print(f"LocalFS deleted bytes (only known for localfs): {res.deleted_bytes_localfs}")

    if not res.actions:
        print("No actions.")
        return 0

    for a in res.actions[:2000]:
        print(f"- [{a.kind}] {a.target_id}: {a.detail}")

    if len(res.actions) > 2000:
        print(f"... ({len(res.actions)} actions total)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


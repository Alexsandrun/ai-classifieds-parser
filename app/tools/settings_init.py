# File: app/tools/settings_init.py
# Version: v0.1.0
# Purpose: initialize tenant_settings with defaults (idempotent)

from __future__ import annotations

import argparse

from app.services.settings.defaults import DEFAULTS
from app.services.settings.repo import SettingsRepo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", default="default")
    ap.add_argument("--force", action="store_true", help="Overwrite existing values")
    args = ap.parse_args()

    repo = SettingsRepo()
    inserted = 0
    skipped = 0
    updated = 0

    for k, v in DEFAULTS.items():
        exists = repo.get_json(tenant_id=args.tenant, key=k)
        if exists is None:
            repo.set_json(tenant_id=args.tenant, key=k, value=v)
            inserted += 1
        elif args.force:
            repo.set_json(tenant_id=args.tenant, key=k, value=v)
            updated += 1
        else:
            skipped += 1

    print(f"OK: tenant={args.tenant} inserted={inserted} updated={updated} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


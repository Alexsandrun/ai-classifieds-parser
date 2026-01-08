# File: app/services/lists/import_csv.py
# Version: v0.1.0
# Purpose: Import CSV (agency exports) into blacklist/whitelist stores.

from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal, Optional

from app.core.normalize import normalize_phone_e164, normalize_name
from app.services.lists.blacklist_store import BlacklistStore
from app.services.lists.whitelist_store import WhitelistStore


def import_csv_to_store(
    *,
    path: Path,
    target: Literal["blacklist", "whitelist"],
    blacklist: Optional[BlacklistStore] = None,
    whitelist: Optional[WhitelistStore] = None,
    default_source: str = "import_csv",
) -> int:
    """
    CSV expected columns (flexible):
      phone (required)
      category / label (optional)
      notes (optional)
      name (optional, currently ignored; reserved for future patterns)

    Delimiter auto-detected by csv.Sniffer when possible.
    Returns number of imported rows.
    """
    if target == "blacklist" and blacklist is None:
        blacklist = BlacklistStore()
    if target == "whitelist" and whitelist is None:
        whitelist = WhitelistStore()

    text = path.read_text(encoding="utf-8", errors="replace")
    sample = text[:4096]

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except Exception:
        dialect = csv.excel

    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    imported = 0

    for row in reader:
        phone_raw = (row.get("phone") or row.get("Phone") or row.get("PHONE") or "").strip()
        phone_e164 = normalize_phone_e164(phone_raw)
        if not phone_e164:
            continue

        notes = (row.get("notes") or row.get("Notes") or row.get("NOTE") or "").strip()
        name = normalize_name(row.get("name") or row.get("Name") or row.get("NAME"))
        if name:
            notes = (notes + f" name={name}").strip()

        if target == "blacklist":
            category = (row.get("category") or row.get("Category") or row.get("CAT") or "UNKNOWN").strip() or "UNKNOWN"
            assert blacklist is not None
            blacklist.add_phone(phone_e164=phone_e164, category=category, notes=notes, source=default_source)
            imported += 1
        else:
            label = (row.get("label") or row.get("Label") or row.get("LABEL") or "INTERNAL_AGENT").strip() or "INTERNAL_AGENT"
            assert whitelist is not None
            whitelist.add_phone(phone_e164=phone_e164, label=label, notes=notes, source=default_source)
            imported += 1

    return imported

# END_OF_FILE

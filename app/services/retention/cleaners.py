# File: app/services/retention/cleaners.py
# Version: v0.1.0
# Purpose: cleanup implementations for local filesystem + ClickHouse partitions

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from app.services.retention.policy import ClickHouseTarget, LocalFSTarget

# ClickHouse client is optional until infra is up.
try:
    import clickhouse_connect  # type: ignore
except Exception:  # pragma: no cover
    clickhouse_connect = None  # type: ignore


@dataclass(frozen=True)
class CleanupAction:
    target_id: str
    kind: str
    detail: str
    estimated_bytes: int = 0


def _safe_under(base: Path, p: Path) -> bool:
    try:
        base = base.resolve()
        p = p.resolve()
        return str(p).startswith(str(base))
    except Exception:
        return False


def cleanup_localfs(
    target: LocalFSTarget,
    *,
    retention_days: int,
    execute: bool,
) -> Tuple[List[CleanupAction], int]:
    """
    Deletes files/dirs under target.path by mtime older than retention_days.
    Safe-guard: only operates inside target.path.
    """
    actions: List[CleanupAction] = []
    deleted_bytes = 0

    base = target.path.resolve()
    if not base.exists():
        return actions, 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    # Walk bottom-up so we can remove empty dirs.
    for root, dirs, files in os.walk(base, topdown=False):
        root_path = Path(root)
        if not _safe_under(base, root_path):
            continue

        # delete old files
        for fn in files:
            fp = root_path / fn
            try:
                st = fp.stat()
                mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                if mtime <= cutoff:
                    actions.append(CleanupAction(target_id=target.id, kind="localfs", detail=f"delete_file {fp}", estimated_bytes=int(st.st_size)))
                    if execute:
                        fp.unlink(missing_ok=True)
                        deleted_bytes += int(st.st_size)
            except FileNotFoundError:
                continue

        # delete empty dirs if their mtime is old-ish (optional)
        for d in dirs:
            dp = root_path / d
            try:
                if not dp.exists():
                    continue
                # If directory is empty after file cleanup, remove it.
                if execute:
                    try:
                        next(dp.iterdir())
                        continue
                    except StopIteration:
                        actions.append(CleanupAction(target_id=target.id, kind="localfs", detail=f"rmdir {dp}", estimated_bytes=0))
                        dp.rmdir()
            except Exception:
                continue

    return actions, deleted_bytes


def _yyyymm_cutoff(retention_months: int) -> str:
    """
    Returns partition cutoff in 'YYYYMM' string. Partitions strictly < cutoff are removed.
    """
    now = datetime.now(timezone.utc)
    # Move back retention_months months (approx by month arithmetic)
    y = now.year
    m = now.month - retention_months
    while m <= 0:
        y -= 1
        m += 12
    return f"{y:04d}{m:02d}"


def cleanup_clickhouse_partitions(
    target: ClickHouseTarget,
    *,
    retention_months: int,
    execute: bool,
    host: str = "localhost",
    port: int = 8123,
    username: str = "aicp",
    password: str = "aicp_dev_password",
) -> Tuple[List[CleanupAction], int]:
    """
    Drops ClickHouse partitions (MergeTree PARTITION BY toYYYYMM(ts)).
    """
    if clickhouse_connect is None:
        return [CleanupAction(target_id=target.id, kind="clickhouse", detail="SKIP: clickhouse_connect not installed")], 0

    client = clickhouse_connect.get_client(host=host, port=port, username=username, password=password, database=target.database)

    cutoff = _yyyymm_cutoff(retention_months)

    parts = client.query(
        """
        SELECT DISTINCT partition
        FROM system.parts
        WHERE database = {db:String} AND table = {tbl:String} AND active = 1
        """,
        parameters={"db": target.database, "tbl": target.table},
    ).result_rows

    partitions = sorted([str(r[0]).strip("'") for r in parts if r and r[0] is not None])

    to_drop = [p for p in partitions if p.isdigit() and len(p) == 6 and p < cutoff]

    actions: List[CleanupAction] = []
    for p in to_drop:
        actions.append(CleanupAction(target_id=target.id, kind="clickhouse", detail=f"drop_partition {target.database}.{target.table} {p}"))

    if execute:
        for p in to_drop:
            client.command(f"ALTER TABLE {target.database}.{target.table} DROP PARTITION '{p}'")

    return actions, 0  # bytes unknown without deeper accounting

# END_OF_FILE

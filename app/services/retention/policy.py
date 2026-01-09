# File: app/services/retention/policy.py
# Version: v0.1.0
# Purpose: retention policy models + disk pressure detection

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

PressureMode = Literal["NORMAL", "WARN", "CRITICAL"]


@dataclass(frozen=True)
class DiskPolicy:
    path: Path
    warn_free_percent: float
    critical_free_percent: float


@dataclass(frozen=True)
class LocalFSTarget:
    id: str
    kind: Literal["localfs"]
    priority: int
    path: Path
    default_retention_days: int
    emergency_retention_days: int
    min_retention_days: int


@dataclass(frozen=True)
class ClickHouseTarget:
    id: str
    kind: Literal["clickhouse"]
    priority: int
    database: str
    table: str
    default_retention_months: int
    emergency_retention_months: int
    min_retention_months: int


Target = LocalFSTarget | ClickHouseTarget


@dataclass(frozen=True)
class RetentionConfig:
    disk: DiskPolicy
    targets: List[Target]


def load_retention_config(path: Path) -> RetentionConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    disk = raw.get("disk") or {}
    disk_policy = DiskPolicy(
        path=Path(disk.get("path") or ".").resolve(),
        warn_free_percent=float(disk.get("warn_free_percent", 20)),
        critical_free_percent=float(disk.get("critical_free_percent", 10)),
    )

    targets: List[Target] = []
    for t in raw.get("targets") or []:
        kind = t.get("kind")
        if kind == "localfs":
            targets.append(
                LocalFSTarget(
                    id=str(t["id"]),
                    kind="localfs",
                    priority=int(t.get("priority", 10)),
                    path=Path(t["path"]).resolve(),
                    default_retention_days=int(t.get("default_retention_days", 14)),
                    emergency_retention_days=int(t.get("emergency_retention_days", 3)),
                    min_retention_days=int(t.get("min_retention_days", 1)),
                )
            )
        elif kind == "clickhouse":
            targets.append(
                ClickHouseTarget(
                    id=str(t["id"]),
                    kind="clickhouse",
                    priority=int(t.get("priority", 50)),
                    database=str(t.get("database", "aicp")),
                    table=str(t["table"]),
                    default_retention_months=int(t.get("default_retention_months", 24)),
                    emergency_retention_months=int(t.get("emergency_retention_months", 6)),
                    min_retention_months=int(t.get("min_retention_months", 3)),
                )
            )
        else:
            raise ValueError(f"Unknown target kind: {kind}")

    return RetentionConfig(disk=disk_policy, targets=targets)


@dataclass(frozen=True)
class DiskStats:
    path: Path
    total_bytes: int
    free_bytes: int
    free_percent: float
    mode: PressureMode


def get_disk_stats(policy: DiskPolicy) -> DiskStats:
    du = shutil.disk_usage(policy.path)
    total = int(du.total)
    free = int(du.free)
    free_percent = (free / total * 100.0) if total else 0.0

    if free_percent <= policy.critical_free_percent:
        mode: PressureMode = "CRITICAL"
    elif free_percent <= policy.warn_free_percent:
        mode = "WARN"
    else:
        mode = "NORMAL"

    return DiskStats(
        path=policy.path,
        total_bytes=total,
        free_bytes=free,
        free_percent=free_percent,
        mode=mode,
    )


def select_retention_value(
    *,
    mode: PressureMode,
    default_value: int,
    emergency_value: int,
    min_value: int,
) -> int:
    v = default_value if mode == "NORMAL" else emergency_value
    if v < min_value:
        return min_value
    return v

# END_OF_FILE

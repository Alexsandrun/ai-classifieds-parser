# File: app/services/retention/manager.py
# Version: v0.1.0
# Purpose: retention manager (daily cleanup + emergency mode)

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.services.retention.cleaners import CleanupAction, cleanup_clickhouse_partitions, cleanup_localfs
from app.services.retention.policy import (
    ClickHouseTarget,
    DiskStats,
    LocalFSTarget,
    PressureMode,
    RetentionConfig,
    get_disk_stats,
    select_retention_value,
)

@dataclass(frozen=True)
class RetentionRunResult:
    mode: PressureMode
    disk_free_percent: float
    actions: List[CleanupAction]
    deleted_bytes_localfs: int


class RetentionManager:
    def __init__(self, cfg: RetentionConfig) -> None:
        self.cfg = cfg

    def run(
        self,
        *,
        execute: bool,
        force_mode: Optional[PressureMode] = None,
        ch_host: str = "localhost",
        ch_port: int = 8123,
        ch_user: str = "aicp",
        ch_password: str = "aicp_dev_password",
    ) -> RetentionRunResult:
        ds: DiskStats = get_disk_stats(self.cfg.disk)
        mode: PressureMode = force_mode or ds.mode

        actions: List[CleanupAction] = []
        deleted_bytes_local = 0

        # Higher priority targets still may be cleaned, but with higher retention.
        # Sorting by priority ascending = clean low-priority first is typical.
        for t in sorted(self.cfg.targets, key=lambda x: getattr(x, "priority", 50)):
            if isinstance(t, LocalFSTarget):
                days = select_retention_value(
                    mode=mode,
                    default_value=t.default_retention_days,
                    emergency_value=t.emergency_retention_days,
                    min_value=t.min_retention_days,
                )
                a, deleted = cleanup_localfs(t, retention_days=days, execute=execute)
                actions.extend(a)
                deleted_bytes_local += deleted

            elif isinstance(t, ClickHouseTarget):
                months = select_retention_value(
                    mode=mode,
                    default_value=t.default_retention_months,
                    emergency_value=t.emergency_retention_months,
                    min_value=t.min_retention_months,
                )
                a, _ = cleanup_clickhouse_partitions(
                    t,
                    retention_months=months,
                    execute=execute,
                    host=ch_host,
                    port=ch_port,
                    username=ch_user,
                    password=ch_password,
                )
                actions.extend(a)

        return RetentionRunResult(
            mode=mode,
            disk_free_percent=ds.free_percent,
            actions=actions,
            deleted_bytes_localfs=deleted_bytes_local,
        )

# END_OF_FILE

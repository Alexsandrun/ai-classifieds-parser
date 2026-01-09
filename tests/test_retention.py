# File: tests/test_retention.py
# Version: v0.1.0
# Purpose: retention manager localfs cleanup works and respects retention_days

from __future__ import annotations

import os
import time
from pathlib import Path

from app.services.retention.cleaners import cleanup_localfs
from app.services.retention.policy import LocalFSTarget


def _touch(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x", encoding="utf-8")


def test_localfs_cleanup_deletes_old_files(tmp_path: Path) -> None:
    base = tmp_path / "raw"
    oldf = base / "old.txt"
    newf = base / "new.txt"
    _touch(oldf)
    _touch(newf)

    # Make old file older by changing mtime to 10 days ago
    ten_days = 10 * 24 * 3600
    old_mtime = time.time() - ten_days
    os.utime(oldf, (old_mtime, old_mtime))

    target = LocalFSTarget(
        id="t1",
        kind="localfs",
        priority=10,
        path=base,
        default_retention_days=7,
        emergency_retention_days=3,
        min_retention_days=1,
    )

    actions, deleted_bytes = cleanup_localfs(target, retention_days=7, execute=True)

    assert not oldf.exists()
    assert newf.exists()
    assert deleted_bytes >= 1
    assert any("delete_file" in a.detail for a in actions)

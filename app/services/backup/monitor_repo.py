# File: app/services/backup/monitor_repo.py
# Version: v0.1.0
# Purpose: Postgres repo for backup jobs/runs and alert anti-spam state

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import psycopg


@dataclass(frozen=True)
class BackupJob:
    tenant_id: str
    job_id: str
    enabled: bool
    expected_interval_hours: int
    max_staleness_hours: int
    fail_warn_threshold: int
    fail_crit_threshold: int
    severity_on_stale: str
    severity_on_fail: str
    notify_telegram: bool
    title: str
    target_hint: str
    created_at_utc: datetime


@dataclass(frozen=True)
class BackupJobStats:
    last_success_at: Optional[datetime]
    last_run_status: Optional[str]  # SUCCESS/FAIL
    last_run_at: Optional[datetime]
    consecutive_failures: int


class BackupMonitorRepo:
    def __init__(self, *, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.environ.get("AICP_PG_DSN", "postgresql://aicp:aicp_dev_password@localhost:5432/aicp")

    def ensure_default_jobs(self, tenant_id: str = "default") -> int:
        """
        Creates default jobs if not exist.
        """
        defaults = [
            # Daily critical PG
            ("pg_daily", 24, 36, 3, 6, "CRITICAL", "WARN", True, "Postgres daily backup", "S3/remote repo"),
            # Weekly models/artifacts
            ("models_weekly", 168, 240, 3, 6, "WARN", "WARN", True, "Models/artifacts weekly backup", "S3/remote repo"),
        ]
        inserted = 0
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                for job_id, interval_h, stale_h, fw, fc, sev_stale, sev_fail, notify, title, hint in defaults:
                    cur.execute(
                        """
                        INSERT INTO backup_jobs (
                          tenant_id, job_id, expected_interval_hours, max_staleness_hours,
                          fail_warn_threshold, fail_crit_threshold,
                          severity_on_stale, severity_on_fail,
                          notify_telegram, title, target_hint
                        )
                        VALUES (%(tenant)s, %(job)s, %(int)s, %(stale)s, %(fw)s, %(fc)s, %(sev_stale)s, %(sev_fail)s, %(notify)s, %(title)s, %(hint)s)
                        ON CONFLICT (tenant_id, job_id) DO NOTHING
                        """,
                        {
                            "tenant": tenant_id,
                            "job": job_id,
                            "int": int(interval_h),
                            "stale": int(stale_h),
                            "fw": int(fw),
                            "fc": int(fc),
                            "sev_stale": sev_stale,
                            "sev_fail": sev_fail,
                            "notify": bool(notify),
                            "title": title,
                            "hint": hint,
                        },
                    )
                    inserted += cur.rowcount
            conn.commit()
        return inserted

    def insert_run(
        self,
        *,
        tenant_id: str,
        job_id: str,
        status: str,
        started_at_utc: Optional[datetime],
        ended_at_utc: Optional[datetime],
        size_bytes: int,
        artifact_name: str,
        error_text: str,
    ) -> None:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO backup_runs (
                      tenant_id, job_id, status, started_at_utc, ended_at_utc, size_bytes, artifact_name, error_text
                    )
                    VALUES (
                      %(tenant)s, %(job)s, %(status)s, %(started)s, %(ended)s, %(size)s, %(artifact)s, %(err)s
                    )
                    """,
                    {
                        "tenant": tenant_id,
                        "job": job_id,
                        "status": status,
                        "started": started_at_utc,
                        "ended": ended_at_utc,
                        "size": int(size_bytes),
                        "artifact": artifact_name or "",
                        "err": (error_text or "")[:4000],
                    },
                )
            conn.commit()

    def list_jobs(self, tenant_id: str = "default") -> list[BackupJob]:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT tenant_id, job_id, enabled,
                           expected_interval_hours, max_staleness_hours,
                           fail_warn_threshold, fail_crit_threshold,
                           severity_on_stale, severity_on_fail,
                           notify_telegram, title, target_hint, created_at_utc
                    FROM backup_jobs
                    WHERE tenant_id = %(tenant)s
                    ORDER BY job_id ASC
                    """,
                    {"tenant": tenant_id},
                )
                rows = cur.fetchall()

        jobs: list[BackupJob] = []
        for r in rows:
            jobs.append(
                BackupJob(
                    tenant_id=r[0],
                    job_id=r[1],
                    enabled=bool(r[2]),
                    expected_interval_hours=int(r[3]),
                    max_staleness_hours=int(r[4]),
                    fail_warn_threshold=int(r[5]),
                    fail_crit_threshold=int(r[6]),
                    severity_on_stale=str(r[7]),
                    severity_on_fail=str(r[8]),
                    notify_telegram=bool(r[9]),
                    title=str(r[10] or ""),
                    target_hint=str(r[11] or ""),
                    created_at_utc=r[12],
                )
            )
        return jobs

    def get_job_stats(self, tenant_id: str, job_id: str) -> BackupJobStats:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                # last success
                cur.execute(
                    """
                    SELECT MAX(created_at_utc)
                    FROM backup_runs
                    WHERE tenant_id = %(tenant)s AND job_id = %(job)s AND status='SUCCESS'
                    """,
                    {"tenant": tenant_id, "job": job_id},
                )
                last_success_at = cur.fetchone()[0]

                # last run
                cur.execute(
                    """
                    SELECT status, created_at_utc
                    FROM backup_runs
                    WHERE tenant_id = %(tenant)s AND job_id = %(job)s
                    ORDER BY created_at_utc DESC
                    LIMIT 1
                    """,
                    {"tenant": tenant_id, "job": job_id},
                )
                row = cur.fetchone()
                last_run_status = row[0] if row else None
                last_run_at = row[1] if row else None

                # consecutive failures since last success
                if last_success_at is None:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM backup_runs
                        WHERE tenant_id = %(tenant)s AND job_id = %(job)s AND status='FAIL'
                        """,
                        {"tenant": tenant_id, "job": job_id},
                    )
                else:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM backup_runs
                        WHERE tenant_id = %(tenant)s AND job_id = %(job)s AND status='FAIL'
                          AND created_at_utc > %(last_success)s
                        """,
                        {"tenant": tenant_id, "job": job_id, "last_success": last_success_at},
                    )
                consecutive_failures = int(cur.fetchone()[0])

        return BackupJobStats(
            last_success_at=last_success_at,
            last_run_status=last_run_status,
            last_run_at=last_run_at,
            consecutive_failures=consecutive_failures,
        )

    def _hash_payload(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

    def should_send_alert(
        self,
        *,
        tenant_id: str,
        alert_key: str,
        payload_text: str,
        cooldown_minutes: int,
        desired_state: str,  # OK/ALERT
    ) -> bool:
        """
        Anti-spam gate. Stores last sent timestamp & payload hash per alert_key.
        Sends if:
          - no record
          - state changed
          - cooldown passed AND payload changed
        """
        now = datetime.now(timezone.utc)
        payload_hash = self._hash_payload(payload_text)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT state, last_sent_at_utc, last_payload_hash
                    FROM alerts_state
                    WHERE tenant_id=%(tenant)s AND alert_key=%(key)s
                    """,
                    {"tenant": tenant_id, "key": alert_key},
                )
                row = cur.fetchone()

                if not row:
                    # insert placeholder, allow send
                    cur.execute(
                        """
                        INSERT INTO alerts_state (tenant_id, alert_key, state, last_sent_at_utc, last_payload_hash, updated_at_utc)
                        VALUES (%(tenant)s, %(key)s, %(state)s, NULL, %(ph)s, NOW())
                        ON CONFLICT DO NOTHING
                        """,
                        {"tenant": tenant_id, "key": alert_key, "state": desired_state, "ph": payload_hash},
                    )
                    conn.commit()
                    return True

                prev_state, last_sent_at, prev_hash = row[0], row[1], row[2]

                # state changed -> send immediately
                if str(prev_state) != desired_state:
                    return True

                # if never sent -> send
                if last_sent_at is None:
                    return True

                # cooldown + payload hash changed
                delta_min = (now - last_sent_at).total_seconds() / 60.0
                if delta_min >= float(cooldown_minutes) and str(prev_hash) != payload_hash:
                    return True

        return False

    def mark_sent(
        self,
        *,
        tenant_id: str,
        alert_key: str,
        payload_text: str,
        new_state: str,  # OK/ALERT
    ) -> None:
        now = datetime.now(timezone.utc)
        payload_hash = self._hash_payload(payload_text)

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO alerts_state (tenant_id, alert_key, state, last_sent_at_utc, last_payload_hash, updated_at_utc)
                    VALUES (%(tenant)s, %(key)s, %(state)s, %(sent)s, %(ph)s, NOW())
                    ON CONFLICT (tenant_id, alert_key) DO UPDATE SET
                      state=EXCLUDED.state,
                      last_sent_at_utc=EXCLUDED.last_sent_at_utc,
                      last_payload_hash=EXCLUDED.last_payload_hash,
                      updated_at_utc=NOW()
                    """,
                    {"tenant": tenant_id, "key": alert_key, "state": new_state, "sent": now, "ph": payload_hash},
                )
            conn.commit()

# END_OF_FILE

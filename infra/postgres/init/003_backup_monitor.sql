-- File: infra/postgres/init/003_backup_monitor.sql
-- Version: v0.1.0
-- Purpose: backup monitor tables (jobs, runs, alert_state)

CREATE TABLE IF NOT EXISTS backup_jobs (
  tenant_id              TEXT NOT NULL DEFAULT 'default',
  job_id                 TEXT NOT NULL,
  enabled                BOOLEAN NOT NULL DEFAULT TRUE,

  -- expectations
  expected_interval_hours INTEGER NOT NULL DEFAULT 24,
  max_staleness_hours     INTEGER NOT NULL DEFAULT 36,

  -- fail escalation (consecutive FAIL runs after the last SUCCESS)
  fail_warn_threshold     INTEGER NOT NULL DEFAULT 3,
  fail_crit_threshold     INTEGER NOT NULL DEFAULT 6,

  severity_on_stale       TEXT NOT NULL DEFAULT 'CRITICAL', -- WARN/CRITICAL
  severity_on_fail        TEXT NOT NULL DEFAULT 'WARN',     -- WARN/CRITICAL

  notify_telegram         BOOLEAN NOT NULL DEFAULT TRUE,

  -- meta
  title                   TEXT NOT NULL DEFAULT '',
  target_hint             TEXT NOT NULL DEFAULT '',  -- e.g. "S3 bucket aicp-backups"
  created_at_utc          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at_utc          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  PRIMARY KEY (tenant_id, job_id)
);

CREATE TABLE IF NOT EXISTS backup_runs (
  id               BIGSERIAL PRIMARY KEY,
  tenant_id         TEXT NOT NULL DEFAULT 'default',
  job_id            TEXT NOT NULL,

  status            TEXT NOT NULL, -- SUCCESS/FAIL
  started_at_utc    TIMESTAMPTZ,
  ended_at_utc      TIMESTAMPTZ,
  size_bytes        BIGINT NOT NULL DEFAULT 0,
  artifact_name     TEXT NOT NULL DEFAULT '',
  error_text        TEXT NOT NULL DEFAULT '',

  created_at_utc    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT backup_runs_status_chk CHECK (status IN ('SUCCESS','FAIL'))
);

CREATE INDEX IF NOT EXISTS idx_backup_runs_tenant_job_created
  ON backup_runs (tenant_id, job_id, created_at_utc DESC);

CREATE INDEX IF NOT EXISTS idx_backup_runs_tenant_job_status_created
  ON backup_runs (tenant_id, job_id, status, created_at_utc DESC);

-- Stores anti-spam state and last known state (OK/ALERT)
CREATE TABLE IF NOT EXISTS alerts_state (
  tenant_id          TEXT NOT NULL DEFAULT 'default',
  alert_key          TEXT NOT NULL,   -- e.g. "backup:pg_daily:stale"
  state              TEXT NOT NULL DEFAULT 'OK', -- OK/ALERT
  last_sent_at_utc   TIMESTAMPTZ,
  last_payload_hash  TEXT NOT NULL DEFAULT '',
  updated_at_utc     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (tenant_id, alert_key)
);

-- END_OF_FILE

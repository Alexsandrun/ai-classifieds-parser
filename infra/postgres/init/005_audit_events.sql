-- File: infra/postgres/init/005_audit_events.sql
-- Version: v0.1.0
-- Purpose: audit events for admin actions (settings changes, etc.)

CREATE TABLE IF NOT EXISTS audit_events (
  id              BIGSERIAL PRIMARY KEY,
  tenant_id        TEXT NOT NULL DEFAULT 'default',
  event_type       TEXT NOT NULL, -- e.g. "settings.update"
  actor_id         TEXT NOT NULL DEFAULT '', -- free-form (username/email/id)
  actor_role       TEXT NOT NULL DEFAULT '', -- viewer/ops/admin/superadmin
  ip               TEXT NOT NULL DEFAULT '',
  user_agent       TEXT NOT NULL DEFAULT '',
  details          JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at_utc   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_time
  ON audit_events (tenant_id, created_at_utc DESC);

CREATE INDEX IF NOT EXISTS idx_audit_events_type_time
  ON audit_events (event_type, created_at_utc DESC);

-- END_OF_FILE

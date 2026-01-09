-- File: infra/postgres/init/004_tenant_settings.sql
-- Version: v0.1.0
-- Purpose: per-tenant settings store (jsonb key/value)

CREATE TABLE IF NOT EXISTS tenant_settings (
  tenant_id     TEXT NOT NULL DEFAULT 'default',
  key           TEXT NOT NULL,
  value         JSONB NOT NULL,
  updated_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (tenant_id, key)
);

CREATE INDEX IF NOT EXISTS idx_tenant_settings_tenant
  ON tenant_settings (tenant_id);

-- END_OF_FILE

-- File: infra/postgres/init/001_schema.sql
-- Version: v0.1.0
-- Purpose: OLTP schema (current-state + lists)

CREATE TABLE IF NOT EXISTS listings_current (
  tenant_id           TEXT NOT NULL DEFAULT 'default',
  listing_uid         TEXT PRIMARY KEY,
  source              TEXT NOT NULL,
  source_listing_id   TEXT NOT NULL,
  url                 TEXT,
  title               TEXT,
  description         TEXT,
  published_at_utc    TIMESTAMPTZ,
  price               DOUBLE PRECISION,
  currency            TEXT,
  phone_hash          TEXT,
  contact_name_norm   TEXT,
  cluster_id          TEXT,
  decision_action     TEXT,
  risk_score          DOUBLE PRECISION,
  reasons             JSONB,
  evidence            JSONB,
  updated_at_utc      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listings_current_tenant_source_time
  ON listings_current (tenant_id, source, published_at_utc DESC);

CREATE INDEX IF NOT EXISTS idx_listings_current_phone_hash
  ON listings_current (phone_hash);

CREATE TABLE IF NOT EXISTS blacklist (
  tenant_id      TEXT NOT NULL DEFAULT 'default',
  phone_hash     TEXT PRIMARY KEY,
  category       TEXT NOT NULL DEFAULT 'UNKNOWN',
  notes          TEXT NOT NULL DEFAULT '',
  source         TEXT NOT NULL DEFAULT 'manual',
  confidence     REAL NOT NULL DEFAULT 1.0,
  added_at_utc   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS whitelist (
  tenant_id      TEXT NOT NULL DEFAULT 'default',
  phone_hash     TEXT PRIMARY KEY,
  label          TEXT NOT NULL DEFAULT 'INTERNAL_AGENT',
  notes          TEXT NOT NULL DEFAULT '',
  source         TEXT NOT NULL DEFAULT 'manual',
  confidence     REAL NOT NULL DEFAULT 1.0,
  added_at_utc   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- END_OF_FILE

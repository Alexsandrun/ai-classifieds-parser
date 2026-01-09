-- File: infra/postgres/init/002_leads.sql
-- Version: v0.1.0
-- Purpose: Leads queue with TTL + claim/ack states

CREATE TABLE IF NOT EXISTS leads_queue (
  lead_id         TEXT PRIMARY KEY, -- uuid as text
  tenant_id       TEXT NOT NULL DEFAULT 'default',

  created_at_utc  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at_utc  TIMESTAMPTZ NOT NULL,

  status          TEXT NOT NULL DEFAULT 'NEW',
  claim_token     TEXT,
  claimed_at_utc  TIMESTAMPTZ,
  delivered_at_utc TIMESTAMPTZ,

  attempts        INTEGER NOT NULL DEFAULT 0,
  last_error      TEXT,

  payload         JSONB NOT NULL
);

-- Allowed statuses (cheap check-constraint instead of enum for flexibility)
ALTER TABLE leads_queue
  DROP CONSTRAINT IF EXISTS leads_queue_status_chk;

ALTER TABLE leads_queue
  ADD CONSTRAINT leads_queue_status_chk
  CHECK (status IN ('NEW','CLAIMED','DELIVERED','FAILED','EXPIRED','DROPPED'));

CREATE INDEX IF NOT EXISTS idx_leads_queue_tenant_status_created
  ON leads_queue (tenant_id, status, created_at_utc);

CREATE INDEX IF NOT EXISTS idx_leads_queue_expires
  ON leads_queue (tenant_id, expires_at_utc);

CREATE INDEX IF NOT EXISTS idx_leads_queue_claim_token
  ON leads_queue (tenant_id, claim_token);

-- END_OF_FILE

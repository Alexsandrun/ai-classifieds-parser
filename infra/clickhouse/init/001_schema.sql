-- File: infra/clickhouse/init/001_schema.sql
-- Version: v0.1.0
-- Purpose: OLAP schema (append-only events + listing snapshots)

CREATE DATABASE IF NOT EXISTS aicp;

CREATE TABLE IF NOT EXISTS aicp.events (
  ts            DateTime64(3, 'UTC'),
  tenant_id     String,
  trace_id      String,
  event         LowCardinality(String),
  source        LowCardinality(String),
  listing_uid   String,
  cluster_id    String,
  action        LowCardinality(String),
  risk_score    Float32,
  reasons       Array(String),
  evidence      Array(String),
  payload_json  String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts, trace_id);

CREATE TABLE IF NOT EXISTS aicp.listing_snapshots (
  ts            DateTime64(3, 'UTC'),
  tenant_id     String,
  source        LowCardinality(String),
  listing_uid   String,
  phone_hash    String,
  cluster_id    String,
  price         Float64,
  currency      LowCardinality(String),
  payload_json  String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts, source, listing_uid);

-- END_OF_FILE

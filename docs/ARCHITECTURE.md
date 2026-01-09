# AI Classifieds Parser — Architecture (v0.1)

## Goal
Collect classifieds listings (via parsers / manual input), normalize, deduplicate, detect agents/scammers/resellers, enrich with analytics + AI, and output clean leads to CRM/API with configurable retention and admin UI.

## Modules (logical)
1) Sources (ingest)
- Parsers per site (plugin style) OR manual web UI input.
- Output: ListingRawPacket (canonical fields + meta)

2) Normalization
- Phone normalization to E.164
- Text cleanup, basic feature extraction
- Output: ListingNormalizedPacket

3) Identity & Clustering
- Build seller identity using phone_hash, text patterns, behavior
- Output: IdentityResult, seller_cluster_id

4) Lists (black/white)
- BlackList: confirmed imported + system-detected
- WhiteList: own employees / trusted sellers
- Output: list match flags + reason codes

5) Decision Engine (rules + AI-lite)
- Produces decision + risk_score + reasons
- Supports explainability: reason code + evidence

6) Leads Queue (per tenant)
- Postgres-backed queue: enqueue/claim/ack/TTL/overflow
- TTL and max_pending configurable via settings

7) Admin API (FastAPI)
- Settings (tenant_settings)
- Help registry
- Runtime/health endpoints

8) Retention Manager
- Periodic cleanup based on priorities
- Pressure modes: NORMAL/WARN/CRITICAL based on disk usage thresholds
- Cleans raw HTML store, old leads, old events, etc.

9) Storage
- Postgres: transactional data (settings, queue, audit, backup monitor)
- ClickHouse: large-scale events/analytics
- MinIO/S3: artifacts, backups, raw blobs (TTL)

## Interfaces between modules
All inter-module packets carry Meta:
- iface_id (string)
- iface_version (SemVer string)
- trace_id (string)
- created_at_utc (UTC)

Canonical types live in app/core/contracts.py and are documented in docs/CANONICAL_FIELDS.md.


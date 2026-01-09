# AI Classifieds Parser — Architecture (v0.1)

## Goal
Ingest listings (parsers/manual), normalize, detect agents/scammers/resellers with analytics + AI, and output clean leads to CRM/API with retention + admin UI.

## Modules
1) Sources (ingest)
2) Normalization
3) Identity & Clustering
4) Lists (black/white)
5) Decision Engine (rules + AI-lite)
6) Leads Queue (per tenant)
7) Admin API (FastAPI)
8) Retention Manager
9) Storage (Postgres/ClickHouse/MinIO)

## Interfaces
All packets carry Meta:
- iface_id
- iface_version (SemVer string)
- trace_id
- created_at_utc
Canonical types live in app/core/contracts.py and docs/CANONICAL_FIELDS.md.

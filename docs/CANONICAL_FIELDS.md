# Canonical Fields Dictionary (v0.1)

This file defines canonical names and types used across modules.
If a field exists here, all modules MUST use this exact name and meaning.

## Identity / seller
- tenant_id: string
  - Example: "default"
  - Notes: logical customer/instance identifier

- seller_phone_e164: string
  - Example: "+380501234567"
  - Notes: MUST be normalized to E.164, digits only with leading +

- seller_phone_hash: string
  - Example: "sha256(tenant_salt + seller_phone_e164)"
  - Notes: stable per tenant, used for clustering and blacklist matching

- seller_name: string
  - Example: "Ivan"
  - Notes: raw display name, sanitized

- seller_cluster_id: string
  - Example: "sc_9f1e..."; stable id from clustering
  - Notes: see SoftSeller Cluster section

## Listing / ad
- listing_id: string
  - Example: "avito:123456789" or "siteX:ABCDEF"
  - Notes: prefer stable source-prefixed ids

- source_id: string
  - Example: "avito", "olx", "site_custom"
  - Notes: plugin/source identifier

- listing_url: string
  - Notes: full URL, sanitized

- published_at_utc: datetime (ISO 8601)
  - Example: "2026-01-09T05:00:00Z"
  - Notes: use UTC

- fetched_at_utc: datetime (ISO 8601)
  - Notes: when our system fetched/ingested it

- title: string
- description: string
- price: number | null
- currency: string | null
- location_text: string | null
- images: list[string] | null

## Decision / scoring
- decision: string
  - Values: "ALLOW" | "REVIEW" | "BLOCK"

- risk_score: float
  - Range: 0.0 .. 1.0

- reasons: list[object]
  - Each reason:
    - code: string
    - weight: float
    - evidence: object (small JSON)

- matched_blacklist: bool
- matched_whitelist: bool

## Storage / raw
- raw_html_ref: string | null
  - Notes: reference to short-lived raw page store (TTL days)

- raw_html_ttl_days: int
  - Notes: default 7..30, managed by retention service


# Canonical Fields Dictionary (v0.1)

This file defines canonical names and types used across modules.
If a field exists here, all modules MUST use this exact name and meaning.

## Identity / seller
- tenant_id: string

- seller_phone_e164: string
  Example: "+380501234567"
  Notes: MUST be normalized to E.164

- seller_phone_hash: string
  Example: "sha256(tenant_salt + seller_phone_e164)"

- seller_name: string

- seller_cluster_id: string
  Notes: stable id from clustering (see SoftSeller Cluster)

## Listing / ad
- listing_id: string
  Example: "avito:123456789"

- source_id: string

- listing_url: string

- published_at_utc: datetime (ISO 8601, UTC)
- fetched_at_utc: datetime (ISO 8601, UTC)

- title: string
- description: string
- price: number | null
- currency: string | null
- location_text: string | null
- images: list[string] | null

## Decision / scoring
- decision: "ALLOW" | "REVIEW" | "BLOCK"
- risk_score: float (0.0..1.0)

- reasons: list[object]
  reason fields:
    - code: string
    - weight: float
    - evidence: object (small JSON)

- matched_blacklist: bool
- matched_whitelist: bool

## Storage / raw
- raw_html_ref: string | null
- raw_html_ttl_days: int

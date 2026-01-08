File: docs/interfaces/IFACE-LISTS-MATCH-001.md | v0.1.0
# IFACE-LISTS-MATCH-001: Lists Match (Whitelist/Blacklist)

## Version
- iface_version: v0.1.0

## Purpose
Match ListingCanonical against agency-provided lists:
- Whitelist: internal agents / trusted sources (ALLOW)
- Blacklist: confirmed fraud / competitor agents / resellers (BLOCK)

## Input
- ListingCanonicalPacket
- Required meta:
  - meta.iface_id == IFACE-PROCESS-CANON-001
  - meta.iface_version == v0.1.0
- Required data fields:
  - data.phone_hash (preferred)
  - data.phone_e164 (optional)

## Output
- Match result (inline in Decision reasons/evidence in MVP)
- Reasons:
  - WHITELIST_PHONE
  - BLACKLIST_PHONE

## Validation checklist
- [ ] Canonical hashing rule: sha256(tenant_salt + ":" + phone_e164)
- [ ] Whitelist wins (if both matched)
- [ ] No raw PII in evidence unless explicitly allowed by policy

END_OF_FILE

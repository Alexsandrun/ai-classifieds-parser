# Interface Documentation Template (v0.1)

## Interface header
- iface_id: <string>
- iface_version: vX.Y.Z
- producer: <module>
- consumers: <module(s)>
- purpose: <one line>

## Input payload (canonical fields)
List required fields with types, plus optional fields.

## Output payload
Same.

## Validation rules
- Required fields presence
- Types and ranges
- Max string sizes
- Allowed enums

## Backward compatibility
- If adding fields: always optional first
- If removing/renaming: deprecate in 1 version, remove next major bump

## Example packet
Provide small JSON example (no huge text).


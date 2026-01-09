# AI Classifieds Parser — RULES (canonical)

## 1) File naming rules
- Only: a-z, 0-9, underscore, dash, dot.
- No spaces.
- Avoid shell-sensitive characters: &, |, ;, >, <, $, `, quotes.
- Prefer predictable paths: `app/...`, `docs/...`, `infra/...`, `tests/...`.

## 2) Editing rules
- Prefer full-file replacements for important modules to avoid broken braces/indentation.
- Before edits: create a timestamped backup copy:
  - `cp -a path/file.py path/file.py.bak.YYYY-MM-DD-HHMMSS`
- After edits: run checks:
  - `uv run ruff check .`
  - `uv run mypy app`
  - `AICP_PG_DSN=... uv run pytest -q`

## 3) Interfaces and canonical fields
- All modules exchange data using canonical contracts from `app/core/contracts.py`.
- Canonical field names must not drift. New fields must be added to `docs/CANONICAL_FIELDS.md`.

## 4) Interface versioning (guard)
- Every inter-module packet contains:
  - `meta.iface_id` (stable string id)
  - `meta.iface_version` (SemVer string "vX.Y.Z")
- When producer/consumer versions mismatch:
  - log an error
  - optionally reject packet in strict mode

## 5) Debugging conventions
- Debug logs are allowed.
- Mark removable debug lines with prefix `DBG:` in comments or log messages so they can be grepped/cleaned later.
- Keep admin inputs sanitized (length limits, types, allowed charset).

## 6) Checkpoints
- Every milestone: generate `docs/checkpoints/INVENTORY.md` and `CHECKPOINT_*.md`.
- Commit checkpoints to git so the project can restart from zero.

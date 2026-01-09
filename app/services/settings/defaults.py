# File: app/services/settings/defaults.py
# Version: v0.1.0
# Purpose: canonical default settings keys/values

from __future__ import annotations

# Canonical keys (do not rename casually)
KEY_LEADS_TTL_DAYS = "leads.ttl_days"
KEY_LEADS_MAX_PENDING = "leads.max_pending"
KEY_LEADS_CLAIM_TIMEOUT_MIN = "leads.claim_timeout_minutes"
KEY_LEADS_OVERFLOW_POLICY = "leads.overflow_policy"  # DROP_OLDEST_NEW | REJECT

# Alerts/monitor defaults
KEY_ALERT_COOLDOWN_MIN = "alerts.cooldown_minutes"

DEFAULTS = {
    # Leads
    KEY_LEADS_TTL_DAYS: 14,                # lead relevance window
    KEY_LEADS_MAX_PENDING: 50_000,         # NEW+CLAIMED cap
    KEY_LEADS_CLAIM_TIMEOUT_MIN: 30,       # stale claim -> release back to NEW
    KEY_LEADS_OVERFLOW_POLICY: "DROP_OLDEST_NEW",

    # Alerts
    KEY_ALERT_COOLDOWN_MIN: 360,           # 6h anti-spam default
}

# END_OF_FILE

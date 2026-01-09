# File: app/services/notify/telegram.py
# Version: v0.1.0
# Purpose: Telegram notifier (simple sendMessage via urllib)

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


class TelegramNotifier:
    def __init__(self, *, token: str | None = None, chat_id: str | None = None) -> None:
        self.token = token or os.environ.get("AICP_TG_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("AICP_TG_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        """
        Returns True if request was attempted and Telegram returned ok=true.
        If not configured, returns False (no-op).
        """
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        body = urllib.parse.urlencode(data).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                js = json.loads(raw)
                return bool(js.get("ok"))
        except Exception:
            return False

# END_OF_FILE

# File: app/services/storage/ch_events.py
# Version: v0.1.0
# Purpose: ClickHouse event writer (append-only)

from __future__ import annotations

import json
import os
from datetime import timezone
from typing import List

import clickhouse_connect

from app.core.events import EventPacket


class ClickHouseEventWriter:
    """
    Writes EventPacket into ClickHouse table aicp.events (by default).
    """

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
        table: str = "events",
    ) -> None:
        self.host = host or os.environ.get("AICP_CH_HOST", "localhost")
        self.port = port or int(os.environ.get("AICP_CH_PORT", "8123"))
        self.username = username or os.environ.get("AICP_CH_USER", "aicp")
        self.password = password or os.environ.get("AICP_CH_PASSWORD", "aicp_dev_password")
        self.database = database or os.environ.get("AICP_CH_DB", "aicp")
        self.table = table

        self.client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )

    def insert(self, pkt: EventPacket) -> None:
        e = pkt.data
        ts = e.ts.astimezone(timezone.utc) if e.ts.tzinfo else e.ts.replace(tzinfo=timezone.utc)

        action = e.action.value if e.action else ""
        payload_json = json.dumps(e.payload, ensure_ascii=False, separators=(",", ":"))

        rows: List[list] = [[
            ts,
            e.tenant_id,
            pkt.meta.trace_id,
            e.event,
            e.source,
            e.listing_uid,
            e.cluster_id,
            action,
            float(e.risk_score),
            list(e.reasons),
            list(e.evidence),
            payload_json,
        ]]

        self.client.insert(
            f"{self.database}.{self.table}",
            rows,
            column_names=[
                "ts",
                "tenant_id",
                "trace_id",
                "event",
                "source",
                "listing_uid",
                "cluster_id",
                "action",
                "risk_score",
                "reasons",
                "evidence",
                "payload_json",
            ],
        )

# END_OF_FILE

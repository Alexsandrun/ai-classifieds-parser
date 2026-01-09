# File: app/admin_api/help_registry.py
# Version: v0.1.0
# Purpose: UI Help Registry (canonical field/button help for admin panel)

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


Danger = Literal["safe", "warn", "critical"]


class FieldHelp(TypedDict, total=False):
    key: str
    label: str
    description: str
    recommended: str
    min: int
    max: int
    allowed: List[str]
    danger: Danger
    troubleshooting: str


class PageHelp(TypedDict, total=False):
    page_id: str
    title: str
    summary: str
    runbook: List[str]
    fields: List[FieldHelp]


HELP_REGISTRY: Dict[str, PageHelp] = {
    "leads": {
        "page_id": "leads",
        "title": "Leads Queue",
        "summary": "Настройки очереди лидов: TTL, лимиты, поведение при переполнении, защита от ‘забитого’ сервера.",
        "runbook": [
            "Если лидов нет: проверь Sources/Parsers → ошибки → фильтры/blacklist hits → очередь NEW=0?",
            "Если очередь растёт: уменьши TTL или увеличь max_pending; проверь, что клиент забирает лиды (CLAIMED не висит часами).",
            "Если лиды дропаются: увеличь max_pending или смени overflow policy; проверь диск/нагрузку.",
        ],
        "fields": [
            {
                "key": "leads.ttl_days",
                "label": "TTL лидов (дней)",
                "description": "Сколько дней лид считается актуальным и хранится до EXPIRED. После TTL лид не должен попадать в обработку.",
                "recommended": "7–14 дней, максимум 30 (зависит от рынка и скорости обработки)",
                "min": 1,
                "max": 90,
                "danger": "warn",
                "troubleshooting": "Большой TTL + большой поток = рост базы/диска. Если деградация — уменьшай TTL.",
            },
            {
                "key": "leads.max_pending",
                "label": "Максимум pending (NEW+CLAIMED)",
                "description": "Защитный лимит размера очереди. При превышении применится overflow policy (например, drop oldest).",
                "recommended": "50k–200k для среднего сервера (масштабируется вверх при мощном железе)",
                "min": 100,
                "max": 2000000,
                "danger": "critical",
                "troubleshooting": "Если слишком низко — лиды начнут DROPPED. Если слишком высоко — риск забить диск.",
            },
            {
                "key": "leads.claim_timeout_minutes",
                "label": "Claim timeout (мин)",
                "description": "Если клиент забрал лиды (CLAIMED) и ‘пропал’, через этот таймаут лиды вернутся в NEW (если ещё не истек TTL).",
                "recommended": "15–60 минут",
                "min": 1,
                "max": 1440,
                "danger": "warn",
                "troubleshooting": "Слишком низко → возможна повторная выдача при долгой обработке.",
            },
            {
                "key": "leads.overflow_policy",
                "label": "Overflow policy",
                "description": "Что делать при переполнении очереди.",
                "allowed": ["DROP_OLDEST_NEW", "REJECT"],
                "recommended": "DROP_OLDEST_NEW (по умолчанию) — защищает сервер от бесконечного роста",
                "danger": "critical",
                "troubleshooting": "REJECT может приводить к потерям данных на входе (но контролируемо).",
            },
        ],
    },
    "backups": {
        "page_id": "backups",
        "title": "Backups",
        "summary": "Мониторинг бэкапов, алерты, расписания (движок бэкапа внешний).",
        "runbook": [
            "Если бэкап stale: проверь оплату/доступы/место на target, затем сделай manual run.",
            "Если fail подряд: проверь креды, сетевой доступ, квоты/лимиты у хранилища.",
            "При подозрении взлома: сделать срочный минимальный бэкап Postgres+settings во внешнее хранилище.",
        ],
        "fields": [],
    },
    "retention": {
        "page_id": "retention",
        "title": "Storage & Retention",
        "summary": "Политики хранения и очистки данных (TTL, приоритеты, деградация по диску).",
        "runbook": [
            "Если диск забивается: уменьшай TTL raw/html, усиливай очистку low-priority данных, проверь очереди/логи.",
            "Если нужна отладка: временно увеличь TTL raw/html, но следи за диском и включай алерты.",
        ],
        "fields": [],
    },
}

# END_OF_FILE

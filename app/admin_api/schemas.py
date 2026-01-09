# File: app/admin_api/schemas.py
# Version: v0.1.0
# Purpose: API schemas for admin panel responses

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class FieldHelpOut(BaseModel):
    key: str
    label: str
    description: str
    recommended: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    allowed: Optional[List[str]] = None
    danger: str = Field(default="safe")
    troubleshooting: Optional[str] = None


class SettingItemOut(BaseModel):
    tenant_id: str
    key: str
    value: Any
    help: Optional[FieldHelpOut] = None


class PageHelpOut(BaseModel):
    page_id: str
    title: str
    summary: str
    runbook: List[str] = Field(default_factory=list)
    fields: List[FieldHelpOut] = Field(default_factory=list)

# END_OF_FILE

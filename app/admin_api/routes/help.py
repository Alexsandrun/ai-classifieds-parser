# File: app/admin_api/routes/help.py
# Version: v0.1.0
# Purpose: Help endpoints for Admin UI (page + field metadata)

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.admin_api.help_registry import HELP_REGISTRY
from app.admin_api.schemas import FieldHelpOut, PageHelpOut

router = APIRouter(prefix="/api/help", tags=["help"])


@router.get("/{page_id}", response_model=PageHelpOut)
def get_page_help(page_id: str) -> PageHelpOut:
    page = HELP_REGISTRY.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Unknown page_id")

    fields = [FieldHelpOut(**f) for f in (page.get("fields", []) or [])]
    return PageHelpOut(
        page_id=page.get("page_id", page_id),
        title=page.get("title", page_id),
        summary=page.get("summary", ""),
        runbook=page.get("runbook", []) or [],
        fields=fields,
    )

# END_OF_FILE

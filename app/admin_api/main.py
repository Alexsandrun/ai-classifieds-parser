# File: app/admin_api/main.py
# Version: v0.1.0
# Purpose: FastAPI Admin API entrypoint (help + settings MVP)

from __future__ import annotations

from fastapi import FastAPI

from app.admin_api.routes.help import router as help_router
from app.admin_api.routes.settings import router as settings_router

app = FastAPI(
    title="AI Classifieds Parser - Admin API",
    version="v0.1.0",
)

app.include_router(help_router)
app.include_router(settings_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict:
    return {"ok": True}

# END_OF_FILE

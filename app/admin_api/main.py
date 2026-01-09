# File: app/admin_api/main.py
# Version: v0.2.0
# Changes: add /api/runtime endpoint
# Purpose: FastAPI Admin API entrypoint (help + settings + runtime)

from __future__ import annotations

from fastapi import FastAPI

from app.admin_api.routes.help import router as help_router
from app.admin_api.routes.settings import router as settings_router
from app.admin_api.routes.runtime import router as runtime_router

app = FastAPI(
    title="AI Classifieds Parser - Admin API",
    version="v0.2.0",
)

app.include_router(help_router)
app.include_router(settings_router)
app.include_router(runtime_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict:
    return {"ok": True}

# END_OF_FILE

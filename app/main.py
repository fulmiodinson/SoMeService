from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import some_account, some_account_item, some_account_thumbnail, some_provider

app = FastAPI(
    title="SoMeService",
    description=(
        "Service for tracking social media accounts and their content "
        "(YouTube, Instagram, etc.)."
    ),
    version="1.0.0",
)

# Serve uploaded media files (thumbnails etc.)
media_root = Path(settings.media_root)
media_root.mkdir(parents=True, exist_ok=True)
app.mount(settings.media_url.rstrip("/"), StaticFiles(directory=str(media_root)), name="media")

app.include_router(some_provider.router, prefix="/api/v1")
app.include_router(some_account.router, prefix="/api/v1")
app.include_router(some_account_thumbnail.router, prefix="/api/v1")
app.include_router(some_account_item.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

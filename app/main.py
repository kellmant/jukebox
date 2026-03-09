import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.api import router as api_router
from app.routes.pages import router as pages_router

log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(level=log_level, format="%(asctime)s %(name)s %(levelname)s %(message)s")

app = FastAPI(title="Jukebox From Hell", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)
app.include_router(pages_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

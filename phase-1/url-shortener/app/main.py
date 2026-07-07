from app.models import *
from fastapi import FastAPI

from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)


from app.core.config import settings
from app.core.logger import setup_root_logger
from app.api.url_routes import router
from app.api.exception_handlers import register_exception_handlers

setup_root_logger()

import logging
logger = logging.getLogger(__name__)

logger.info(f"Starting {settings.app_name} in {'debug' if settings.debug else 'production'} mode")

app = FastAPI(title=settings.app_name)

register_exception_handlers(app=app)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Welcome to URL Shortener API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
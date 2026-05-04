"""Compatibility entrypoint for running the API."""

import uvicorn
from config import settings
from core.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api_router


def create_app() -> FastAPI:

    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )

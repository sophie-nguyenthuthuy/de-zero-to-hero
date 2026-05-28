from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.routers import analytics, auth, customers
from app.schemas.schemas import HealthCheck


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Data Engineering Lab — REST API với FastAPI",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(customers.router)
    app.include_router(analytics.router)

    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}

    @app.get("/health", response_model=HealthCheck, tags=["System"])
    async def health():
        db_ok = False
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            pass

        return HealthCheck(
            status="healthy" if db_ok else "degraded",
            version=settings.VERSION,
            db_connected=db_ok,
            timestamp=datetime.now(timezone.utc),
        )

    return app


app = create_app()

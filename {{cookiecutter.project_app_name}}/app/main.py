"""Main FastAPI app instance declaration."""
import uvicorn
import click

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_pagination import add_pagination
from sqlalchemy import text

from app import settings
from app.core.db import AsyncDatabaseContext, async_engine
from app.api.api import api_router
from app.core.config import settings
from app.schemas.common import HealthCheck

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG,
    docs_url="/docs",
)
add_pagination(app)
app.state.settings = settings

app.include_router(api_router)

# Sets all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guards against HTTP Host Header attacks
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)


# HealthCheck
@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    database_ok = True
    try:
        click.secho("Connecting to database...")
        async with async_engine.connect() as db_connection:
            await db_connection.execute(text("SELECT 1"))
        async_engine.dispose()
        click.secho("Database is ready and reachable!", fg="green")
    except OSError:
        click.secho("Failed connection!", fg="red")
        database_ok = False

    return HealthCheck.parse_obj(
        {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "db_connection": "OK" if database_ok else "KO",
        }
    )

@app.on_event("startup")
async def startup_event_manager():
    async_db_context = AsyncDatabaseContext.with_config(settings=settings)
    await async_db_context.check_connection()
    app.state.async_db_context = async_db_context

    # TODO Añadir un admin_backoffice


@app.on_event("shutdown")
async def shutdown_event_manager():
    app.state.async_db_context.close()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)

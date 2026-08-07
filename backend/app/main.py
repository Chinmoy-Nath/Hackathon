from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.database import async_session, init_db
from app.data.seed_data import seed_database
from app.models.models import User
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.campaigns import router as campaigns_router
from app.routes.customers import router as customers_router
from app.routes.vehicles import router as vehicles_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is None:
            await seed_database(session)
    yield


app = FastAPI(
    title="Campaign Intelligence Platform - Tata Motors",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(customers_router)
app.include_router(analytics_router)
app.include_router(vehicles_router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Campaign Intelligence Platform"}

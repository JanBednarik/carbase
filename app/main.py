from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401 — ensures all models are registered before create_all
from app.database import create_db_and_tables
from app.routers import brands, car_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Car Base", lifespan=lifespan)

app.include_router(brands.router)
app.include_router(car_models.router)

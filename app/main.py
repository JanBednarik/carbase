from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401 — ensures all models are registered before create_all
from app.database import create_db_and_tables
from app.routers import api_tokens, brands, car_models, recommend, used_cars


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Car Base", lifespan=lifespan)

app.include_router(api_tokens.router)
app.include_router(brands.router)
app.include_router(car_models.router)
app.include_router(used_cars.router)
app.include_router(recommend.router)

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app import ml_engine
from app.database import get_session
from app.models.used_car import UsedCarRead

router = APIRouter(prefix="/recommend", tags=["recommend"])

SessionDep = Annotated[Session, Depends(get_session)]


class RecommendAttribute(BaseModel):
    name: str
    value: str | int | float
    weight: Annotated[float, Field(ge=0.0, le=1.0)]


class RecommendRequest(BaseModel):
    attributes: list[RecommendAttribute]


@router.post("/", response_model=list[UsedCarRead])
def recommend(request: RecommendRequest, session: SessionDep) -> list[UsedCarRead]:
    # TODO recommendation engine is not implemented yet
    return ml_engine.recommend(session)

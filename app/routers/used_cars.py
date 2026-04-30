from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_scope
from app.database import get_session
from app.models.api_token import ApiToken, Scope
from app.models.car_model import CarModel
from app.models.used_car import UsedCar, UsedCarCreate, UsedCarRead, UsedCarUpdate

router = APIRouter(prefix="/cars", tags=["cars"])

SessionDep = Annotated[Session, Depends(get_session)]
UsedCarWriteDep = Annotated[ApiToken, Depends(require_scope(Scope.used_car_write))]


@router.get("/", response_model=list[UsedCarRead])
def list_used_cars(
    session: SessionDep,
    car_model_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(UsedCar)
    if car_model_id is not None:
        query = query.where(UsedCar.car_model_id == car_model_id)
    return session.exec(query.offset(skip).limit(limit)).all()


@router.post("/", response_model=UsedCarRead, status_code=201)
def create_used_car(car: UsedCarCreate, session: SessionDep, _: UsedCarWriteDep):
    if not session.get(CarModel, car.car_model_id):
        raise HTTPException(status_code=404, detail="Car model not found")
    db_car = UsedCar.model_validate(car)
    session.add(db_car)
    session.commit()
    session.refresh(db_car)
    return db_car


@router.get("/{car_id}", response_model=UsedCarRead)
def get_used_car(car_id: int, session: SessionDep):
    car = session.get(UsedCar, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Used car not found")
    return car


@router.patch("/{car_id}", response_model=UsedCarRead)
def update_used_car(
    car_id: int, car_update: UsedCarUpdate, session: SessionDep, _: UsedCarWriteDep
):
    car = session.get(UsedCar, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Used car not found")
    if car_update.car_model_id is not None and not session.get(
        CarModel, car_update.car_model_id
    ):
        raise HTTPException(status_code=404, detail="Car model not found")
    car.sqlmodel_update(car_update.model_dump(exclude_unset=True))
    session.add(car)
    session.commit()
    session.refresh(car)
    return car


@router.delete("/{car_id}", status_code=204)
def delete_used_car(car_id: int, session: SessionDep, _: UsedCarWriteDep):
    car = session.get(UsedCar, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Used car not found")
    session.delete(car)
    session.commit()

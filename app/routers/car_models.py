from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_scope
from app.database import get_session
from app.models.api_token import ApiToken, Scope
from app.models.brand import Brand
from app.models.car_model import CarModel, CarModelCreate, CarModelRead, CarModelUpdate

router = APIRouter(prefix="/models", tags=["models"])

SessionDep = Annotated[Session, Depends(get_session)]
CarModelWriteDep = Annotated[ApiToken, Depends(require_scope(Scope.car_model_write))]


@router.get("/", response_model=list[CarModelRead])
def list_car_models(
    session: SessionDep, brand_id: int | None = None, skip: int = 0, limit: int = 100
):
    query = select(CarModel)
    if brand_id is not None:
        query = query.where(CarModel.brand_id == brand_id)
    return session.exec(query.offset(skip).limit(limit)).all()


@router.post("/", response_model=CarModelRead, status_code=201)
def create_car_model(car: CarModelCreate, session: SessionDep, _: CarModelWriteDep):
    if not session.get(Brand, car.brand_id):
        raise HTTPException(status_code=404, detail="Brand not found")
    db_car = CarModel.model_validate(car)
    session.add(db_car)
    session.commit()
    session.refresh(db_car)
    return db_car


@router.get("/{model_id}", response_model=CarModelRead)
def get_car_model(model_id: int, session: SessionDep):
    car = session.get(CarModel, model_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.patch("/{model_id}", response_model=CarModelRead)
def update_car_model(
    model_id: int, car_update: CarModelUpdate, session: SessionDep, _: CarModelWriteDep
):
    car = session.get(CarModel, model_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car_update.brand_id is not None and not session.get(Brand, car_update.brand_id):
        raise HTTPException(status_code=404, detail="Brand not found")
    data = car_update.model_dump(exclude_unset=True)
    car.sqlmodel_update(data)
    session.add(car)
    session.commit()
    session.refresh(car)
    return car


@router.delete("/{model_id}", status_code=204)
def delete_car_model(model_id: int, session: SessionDep, _: CarModelWriteDep):
    car = session.get(CarModel, model_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    session.delete(car)
    session.commit()

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_scope
from app.database import get_session
from app.models.api_token import ApiToken, Scope
from app.models.brand import Brand, BrandCreate, BrandRead, BrandUpdate

router = APIRouter(prefix="/brands", tags=["brands"])

SessionDep = Annotated[Session, Depends(get_session)]
BrandWriteDep = Annotated[ApiToken, Depends(require_scope(Scope.brand_write))]


@router.get("/", response_model=list[BrandRead])
def list_brands(session: SessionDep, skip: int = 0, limit: int = 100):
    return session.exec(select(Brand).offset(skip).limit(limit)).all()


@router.post("/", response_model=BrandRead, status_code=201)
def create_brand(brand: BrandCreate, session: SessionDep, _: BrandWriteDep):
    db_brand = Brand.model_validate(brand)
    session.add(db_brand)
    session.commit()
    session.refresh(db_brand)
    return db_brand


@router.get("/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, session: SessionDep):
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.patch("/{brand_id}", response_model=BrandRead)
def update_brand(
    brand_id: int, brand_update: BrandUpdate, session: SessionDep, _: BrandWriteDep
):
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    data = brand_update.model_dump(exclude_unset=True)
    brand.sqlmodel_update(data)
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=204)
def delete_brand(brand_id: int, session: SessionDep, _: BrandWriteDep):
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    session.delete(brand)
    session.commit()

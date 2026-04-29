import enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.used_car import UsedCar


class BodyStyle(str, enum.Enum):
    sedan = "sedan"
    hatchback = "hatchback"
    suv = "suv"
    coupe = "coupe"
    convertible = "convertible"
    wagon = "wagon"
    van = "van"
    pickup = "pickup"


class CarModelBase(SQLModel):
    name: str = Field(index=True)
    year_from: int
    year_to: Optional[int] = None
    doors: int
    body_style: BodyStyle


class CarModel(CarModelBase, table=True):
    __tablename__ = "car_model"

    id: Optional[int] = Field(default=None, primary_key=True)
    brand_id: int = Field(foreign_key="brand.id")
    brand: Optional["Brand"] = Relationship(back_populates="cars")
    used_cars: List["UsedCar"] = Relationship(back_populates="car_model")


class CarModelCreate(CarModelBase):
    brand_id: int


class CarModelRead(CarModelBase):
    id: int
    brand_id: int


class CarModelUpdate(SQLModel):
    name: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    doors: Optional[int] = None
    body_style: Optional[BodyStyle] = None
    brand_id: Optional[int] = None

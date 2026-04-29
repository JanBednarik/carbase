import enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.car_model import CarModel


class Fuel(str, enum.Enum):
    diesel = "Diesel"
    petrol = "Petrol"
    electric = "Electric"
    cng = "CNG"
    lpg = "LPG"


class Transmission(str, enum.Enum):
    manual = "Manual"
    automatic = "Automatic"


class UsedCarBase(SQLModel):
    name: str = Field(index=True)
    year: int
    price: float
    km_driven: int
    fuel: Fuel
    transmission: Transmission


class UsedCar(UsedCarBase, table=True):
    __tablename__ = "used_car"

    id: Optional[int] = Field(default=None, primary_key=True)
    car_model_id: int = Field(foreign_key="car_model.id")
    car_model: Optional["CarModel"] = Relationship(back_populates="used_cars")


class UsedCarCreate(UsedCarBase):
    car_model_id: int


class UsedCarRead(UsedCarBase):
    id: int
    car_model_id: int


class UsedCarUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    km_driven: Optional[int] = None
    fuel: Optional[Fuel] = None
    transmission: Optional[Transmission] = None
    car_model_id: Optional[int] = None

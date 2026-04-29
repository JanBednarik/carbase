import enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.car_model import CarModel


class Continent(str, enum.Enum):
    africa = "Africa"
    antarctica = "Antarctica"
    asia = "Asia"
    europe = "Europe"
    north_america = "North America"
    oceania = "Oceania"
    south_america = "South America"


class BrandBase(SQLModel):
    name: str = Field(index=True)
    country: str
    continent: Continent


class Brand(BrandBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cars: List["CarModel"] = Relationship(back_populates="brand")


class BrandCreate(BrandBase):
    pass


class BrandRead(BrandBase):
    id: int


class BrandUpdate(SQLModel):
    name: Optional[str] = None
    country: Optional[str] = None
    continent: Optional[str] = None

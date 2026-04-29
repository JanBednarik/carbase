import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.brand import Brand, Continent
from app.models.car_model import BodyStyle, CarModel
from app.models.used_car import Fuel, Transmission, UsedCar


class BrandFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Brand
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Brand {n}")
    country = factory.Faker("country")
    continent = factory.Iterator(list(Continent))


class CarModelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = CarModel
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Model {n}")
    brand = factory.SubFactory(BrandFactory)
    year_from = factory.Faker("random_int", min=1950, max=2020)
    year_to = factory.Faker("random_int", min=2021, max=2026)
    doors = factory.Iterator([2, 3, 4, 5])
    body_style = factory.Iterator(list(BodyStyle))


class UsedCarFactory(SQLAlchemyModelFactory):
    class Meta:
        model = UsedCar
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Used Car {n}")
    car_model = factory.SubFactory(CarModelFactory)
    year = factory.Faker("random_int", min=2000, max=2024)
    price = factory.Faker("pyfloat", min_value=1000, max_value=50000, right_digits=2)
    km_driven = factory.Faker("random_int", min=0, max=300000)
    fuel = factory.Iterator(list(Fuel))
    transmission = factory.Iterator(list(Transmission))

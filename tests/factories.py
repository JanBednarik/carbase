import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.brand import Brand, Continent
from app.models.car_model import BodyStyle, CarModel


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

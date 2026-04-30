from fastapi.testclient import TestClient
from sqlmodel import Session
from syrupy.assertion import SnapshotAssertion

from app.models.brand import Continent
from app.models.car_model import BodyStyle, CarModel
from tests.factories import BrandFactory, CarModelFactory


def test_create_car_model(client: TestClient, session: Session):
    brand = BrandFactory()
    response = client.post(
        "/models/",
        json={
            "name": "Corolla",
            "brand_id": brand.id,
            "year_from": 1966,
            "year_to": 2022,
            "doors": 4,
            "body_style": "sedan",
        },
    )
    assert response.status_code == 201
    car_id = response.json()["id"]

    session.expire_all()
    car = session.get(CarModel, car_id)
    assert car is not None
    assert car.name == "Corolla"
    assert car.brand_id == brand.id
    assert car.year_from == 1966
    assert car.year_to == 2022


def test_create_car_model__unknown_brand(client: TestClient):
    response = client.post(
        "/models/",
        json={
            "name": "Corolla",
            "brand_id": 999,
            "year_from": 1966,
            "year_to": 2022,
            "doors": 4,
            "body_style": "sedan",
        },
    )
    assert response.status_code == 404


def test_list_car_models(client: TestClient, snapshot_json: SnapshotAssertion):
    brand = BrandFactory(name="Toyota", country="Japan", continent=Continent.asia)
    CarModelFactory(
        name="Corolla",
        brand=brand,
        year_from=1966,
        year_to=2022,
        doors=4,
        body_style=BodyStyle.sedan,
    )
    CarModelFactory(
        name="Camry",
        brand=brand,
        year_from=1982,
        year_to=2023,
        doors=4,
        body_style=BodyStyle.sedan,
    )

    response = client.get("/models/")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_list_car_models__filter_by_brand(
    client: TestClient, snapshot_json: SnapshotAssertion
):
    toyota = BrandFactory(name="Toyota", country="Japan", continent=Continent.asia)
    ford = BrandFactory(name="Ford", country="USA", continent=Continent.north_america)
    CarModelFactory(
        name="Corolla",
        brand=toyota,
        year_from=1966,
        year_to=2022,
        doors=4,
        body_style=BodyStyle.sedan,
    )
    CarModelFactory(
        name="Mustang",
        brand=ford,
        year_from=1964,
        year_to=2021,
        doors=2,
        body_style=BodyStyle.coupe,
    )

    response = client.get(f"/models/?brand_id={toyota.id}")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_car_model(client: TestClient, snapshot_json: SnapshotAssertion):
    car = CarModelFactory(
        name="Corolla",
        year_from=1966,
        year_to=2022,
        doors=4,
        body_style=BodyStyle.sedan,
    )

    response = client.get(f"/models/{car.id}")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_car_model__not_found(client: TestClient):
    response = client.get("/models/999")
    assert response.status_code == 404


def test_update_car_model(
    client: TestClient, session: Session, snapshot_json: SnapshotAssertion
):
    car = CarModelFactory(
        name="Corolla",
        year_from=1966,
        year_to=2022,
        doors=4,
        body_style=BodyStyle.sedan,
    )

    response = client.patch(f"/models/{car.id}", json={"year_to": 2023})
    assert response.status_code == 200
    assert response.json() == snapshot_json

    session.expire_all()
    updated = session.get(CarModel, car.id)
    assert updated.year_to == 2023
    assert updated.name == car.name


def test_update_car_model__not_found(client: TestClient):
    response = client.patch("/models/999", json={"year_to": 2023})
    assert response.status_code == 404


def test_update_car_model__unknown_brand(client: TestClient):
    car = CarModelFactory()

    response = client.patch(f"/models/{car.id}", json={"brand_id": 999})
    assert response.status_code == 404


def test_delete_car_model(client: TestClient, session: Session):
    car = CarModelFactory()

    response = client.delete(f"/models/{car.id}")
    assert response.status_code == 204

    session.expire_all()
    assert session.get(CarModel, car.id) is None


def test_delete_car_model__not_found(client: TestClient):
    response = client.delete("/models/999")
    assert response.status_code == 404

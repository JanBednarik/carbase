from fastapi.testclient import TestClient
from sqlmodel import Session
from syrupy.assertion import SnapshotAssertion

from app.models.api_token import ApiToken, Scope
from app.models.used_car import Fuel, Transmission, UsedCar
from tests.factories import ApiTokenFactory, CarModelFactory, UsedCarFactory


def _auth(token: ApiToken) -> dict:
    return {"Authorization": f"Bearer {token.token}"}


def test_create_used_car(client: TestClient, session: Session):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    car_model = CarModelFactory()

    response = client.post(
        "/cars/",
        json={
            "name": "2019 Toyota Corolla",
            "car_model_id": car_model.id,
            "year": 2019,
            "price": 15000.0,
            "km_driven": 50000,
            "fuel": "Petrol",
            "transmission": "Manual",
        },
        headers=_auth(auth),
    )

    assert response.status_code == 201
    used_car_id = response.json()["id"]

    session.expire_all()
    used_car = session.get(UsedCar, used_car_id)
    assert used_car is not None
    assert used_car.name == "2019 Toyota Corolla"
    assert used_car.car_model_id == car_model.id
    assert used_car.year == 2019
    assert used_car.price == 15000.0
    assert used_car.km_driven == 50000
    assert used_car.fuel == Fuel.petrol
    assert used_car.transmission == Transmission.manual


def test_create_used_car__unknown_model(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])

    response = client.post(
        "/cars/",
        json={
            "name": "2019 Toyota Corolla",
            "car_model_id": 999,
            "year": 2019,
            "price": 15000.0,
            "km_driven": 50000,
            "fuel": "Petrol",
            "transmission": "Manual",
        },
        headers=_auth(auth),
    )
    assert response.status_code == 404


def test_create_used_car__no_auth(client: TestClient):
    car_model = CarModelFactory()
    response = client.post(
        "/cars/",
        json={
            "name": "2019 Toyota Corolla",
            "car_model_id": car_model.id,
            "year": 2019,
            "price": 15000.0,
            "km_driven": 50000,
            "fuel": "Petrol",
            "transmission": "Manual",
        },
    )
    assert response.status_code == 401


def test_create_used_car__insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    car_model = CarModelFactory()
    response = client.post(
        "/cars/",
        json={
            "name": "2019 Toyota Corolla",
            "car_model_id": car_model.id,
            "year": 2019,
            "price": 15000.0,
            "km_driven": 50000,
            "fuel": "Petrol",
            "transmission": "Manual",
        },
        headers=_auth(auth),
    )
    assert response.status_code == 403


def test_list_used_cars(client: TestClient, snapshot_json: SnapshotAssertion):
    car_model = CarModelFactory()
    UsedCarFactory(
        name="2019 Toyota Corolla",
        car_model=car_model,
        year=2019,
        price=15000.0,
        km_driven=50000,
        fuel=Fuel.petrol,
        transmission=Transmission.manual,
    )
    UsedCarFactory(
        name="2021 Toyota Corolla",
        car_model=car_model,
        year=2021,
        price=22000.0,
        km_driven=15000,
        fuel=Fuel.petrol,
        transmission=Transmission.automatic,
    )

    response = client.get("/cars/")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_list_used_cars__filter_by_model(
    client: TestClient, snapshot_json: SnapshotAssertion
):
    corolla = CarModelFactory()
    mustang = CarModelFactory()
    UsedCarFactory(
        name="2019 Toyota Corolla",
        car_model=corolla,
        year=2019,
        price=15000.0,
        km_driven=50000,
        fuel=Fuel.petrol,
        transmission=Transmission.manual,
    )
    UsedCarFactory(
        name="2018 Ford Mustang",
        car_model=mustang,
        year=2018,
        price=25000.0,
        km_driven=30000,
        fuel=Fuel.petrol,
        transmission=Transmission.automatic,
    )

    response = client.get(f"/cars/?car_model_id={corolla.id}")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_used_car(client: TestClient, snapshot_json: SnapshotAssertion):
    used_car = UsedCarFactory(
        name="2019 Toyota Corolla",
        year=2019,
        price=15000.0,
        km_driven=50000,
        fuel=Fuel.petrol,
        transmission=Transmission.manual,
    )

    response = client.get(f"/cars/{used_car.id}")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_used_car__not_found(client: TestClient):
    response = client.get("/cars/999")
    assert response.status_code == 404


def test_update_used_car(
    client: TestClient, session: Session, snapshot_json: SnapshotAssertion
):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    used_car = UsedCarFactory(
        name="2019 Toyota Corolla",
        year=2019,
        price=15000.0,
        km_driven=50000,
        fuel=Fuel.petrol,
        transmission=Transmission.manual,
    )

    response = client.patch(
        f"/cars/{used_car.id}", json={"price": 13500.0}, headers=_auth(auth)
    )
    assert response.status_code == 200
    assert response.json() == snapshot_json

    session.expire_all()
    updated = session.get(UsedCar, used_car.id)
    assert updated.price == 13500.0
    assert updated.name == used_car.name


def test_update_used_car__not_found(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    response = client.patch("/cars/999", json={"price": 13500.0}, headers=_auth(auth))
    assert response.status_code == 404


def test_update_used_car__unknown_model(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    used_car = UsedCarFactory()
    response = client.patch(
        f"/cars/{used_car.id}", json={"car_model_id": 999}, headers=_auth(auth)
    )
    assert response.status_code == 404


def test_update_used_car__no_auth(client: TestClient):
    used_car = UsedCarFactory()
    response = client.patch(f"/cars/{used_car.id}", json={"price": 13500.0})
    assert response.status_code == 401


def test_update_used_car__insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    used_car = UsedCarFactory()
    response = client.patch(
        f"/cars/{used_car.id}", json={"price": 13500.0}, headers=_auth(auth)
    )
    assert response.status_code == 403


def test_delete_used_car(client: TestClient, session: Session):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    used_car = UsedCarFactory()

    response = client.delete(f"/cars/{used_car.id}", headers=_auth(auth))
    assert response.status_code == 204

    session.expire_all()
    assert session.get(UsedCar, used_car.id) is None


def test_delete_used_car__not_found(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.used_car_write])
    response = client.delete("/cars/999", headers=_auth(auth))
    assert response.status_code == 404


def test_delete_used_car__no_auth(client: TestClient):
    used_car = UsedCarFactory()
    response = client.delete(f"/cars/{used_car.id}")
    assert response.status_code == 401


def test_delete_used_car__insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    used_car = UsedCarFactory()
    response = client.delete(f"/cars/{used_car.id}", headers=_auth(auth))
    assert response.status_code == 403

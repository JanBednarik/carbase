from fastapi.testclient import TestClient
from syrupy.assertion import SnapshotAssertion

from app.models.used_car import Fuel, Transmission
from tests.factories import UsedCarFactory


def test_recommend_empty(client: TestClient):
    response = client.post("/recommend/", json={"attributes": []})
    assert response.status_code == 200
    assert response.json() == []


def test_recommend_returns_used_cars(
    client: TestClient, snapshot_json: SnapshotAssertion
):
    UsedCarFactory(
        name="2019 Toyota Corolla",
        year=2019,
        price=15000.0,
        km_driven=50000,
        fuel=Fuel.petrol,
        transmission=Transmission.manual,
    )

    response = client.post(
        "/recommend/",
        json={"attributes": [{"name": "fuel", "value": "Petrol", "weight": 0.8}]},
    )
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_recommend_invalid_weight(client: TestClient):
    response = client.post(
        "/recommend/",
        json={"attributes": [{"name": "fuel", "value": "Petrol", "weight": 1.5}]},
    )
    assert response.status_code == 422

from fastapi.testclient import TestClient
from sqlmodel import Session
from syrupy.assertion import SnapshotAssertion

from app.models.brand import Brand, Continent
from tests.factories import BrandFactory


def test_create_brand(client: TestClient, session: Session):
    response = client.post(
        "/brands/", json={"name": "Toyota", "country": "Japan", "continent": "Asia"}
    )
    assert response.status_code == 201
    brand_id = response.json()["id"]

    session.expire_all()
    brand = session.get(Brand, brand_id)
    assert brand is not None
    assert brand.name == "Toyota"
    assert brand.country == "Japan"
    assert brand.continent == "Asia"


def test_list_brands(client: TestClient, snapshot_json: SnapshotAssertion):
    BrandFactory(name="Toyota", country="Japan", continent=Continent.asia)
    BrandFactory(name="Ford", country="USA", continent=Continent.north_america)

    response = client.get("/brands/")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_brand(client: TestClient, snapshot_json: SnapshotAssertion):
    brand = BrandFactory(name="Toyota", country="Japan", continent=Continent.asia)

    response = client.get(f"/brands/{brand.id}")
    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_brand__not_found(client: TestClient):
    response = client.get("/brands/999")
    assert response.status_code == 404


def test_update_brand(
    client: TestClient, session: Session, snapshot_json: SnapshotAssertion
):
    brand = BrandFactory(name="Toyota", country="Japan", continent=Continent.asia)

    response = client.patch(f"/brands/{brand.id}", json={"country": "JP"})
    assert response.status_code == 200
    assert response.json() == snapshot_json

    session.expire_all()
    updated = session.get(Brand, brand.id)
    assert updated.country == "JP"
    assert updated.name == brand.name


def test_update_brand__not_found(client: TestClient):
    response = client.patch("/brands/999", json={"country": "JP"})
    assert response.status_code == 404


def test_delete_brand(client: TestClient, session: Session):
    brand = BrandFactory()

    response = client.delete(f"/brands/{brand.id}")
    assert response.status_code == 204

    session.expire_all()
    assert session.get(Brand, brand.id) is None


def test_delete_brand__not_found(client: TestClient):
    response = client.delete("/brands/999")
    assert response.status_code == 404

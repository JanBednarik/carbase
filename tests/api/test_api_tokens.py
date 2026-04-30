from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session
from syrupy.assertion import SnapshotAssertion

from app.models.api_token import ApiToken, Scope
from tests.factories import ApiTokenFactory


def _auth(token: ApiToken) -> dict:
    return {"Authorization": f"Bearer {token.token}"}


def test_create_api_token(client: TestClient, session: Session):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])

    response = client.post(
        "/api-tokens/",
        json={"name": "My Token", "scopes": ["api_token_read"]},
        headers=_auth(auth),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Token"
    assert data["scopes"] == ["api_token_read"]
    assert len(data["token"]) >= 32
    assert data["expires_at"] is not None

    session.expire_all()
    token = session.get(ApiToken, data["id"])
    assert token is not None
    assert token.name == "My Token"
    assert token.scopes == [Scope.api_token_read]


def test_create_api_token_no_scopes(client: TestClient, session: Session):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])

    response = client.post(
        "/api-tokens/",
        json={"name": "Empty Scopes Token"},
        headers=_auth(auth),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["scopes"] == []


def test_create_api_token_no_auth(client: TestClient):
    response = client.post("/api-tokens/", json={"name": "My Token"})
    assert response.status_code == 401


def test_create_api_token_invalid_token(client: TestClient):
    response = client.post(
        "/api-tokens/",
        json={"name": "My Token"},
        headers={"Authorization": "Bearer invalid-token-value"},
    )
    assert response.status_code == 401


def test_create_api_token_expired_token(client: TestClient):
    auth = ApiTokenFactory(
        scopes=[Scope.api_token_write],
        expires_at=date.today() - timedelta(days=1),
    )

    response = client.post(
        "/api-tokens/",
        json={"name": "My Token"},
        headers=_auth(auth),
    )

    assert response.status_code == 401


def test_create_api_token_insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])

    response = client.post(
        "/api-tokens/",
        json={"name": "My Token"},
        headers=_auth(auth),
    )

    assert response.status_code == 403


def test_list_api_tokens(client: TestClient, snapshot_json: SnapshotAssertion):
    auth = ApiTokenFactory(
        name="Auth Token", scopes=[Scope.api_token_read], expires_at=None
    )
    ApiTokenFactory(
        name="Read Token", scopes=[Scope.api_token_read], expires_at=date(2027, 12, 31)
    )
    ApiTokenFactory(
        name="Write Token", scopes=[Scope.api_token_write], expires_at=date(2027, 6, 30)
    )

    response = client.get("/api-tokens/", headers=_auth(auth))

    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_list_api_tokens_no_auth(client: TestClient):
    response = client.get("/api-tokens/")
    assert response.status_code == 401


def test_list_api_tokens_insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])
    response = client.get("/api-tokens/", headers=_auth(auth))
    assert response.status_code == 403


def test_get_api_token(client: TestClient, snapshot_json: SnapshotAssertion):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    target = ApiTokenFactory(
        name="Target Token",
        scopes=[Scope.api_token_write],
        expires_at=date(2027, 12, 31),
    )

    response = client.get(f"/api-tokens/{target.id}", headers=_auth(auth))

    assert response.status_code == 200
    assert response.json() == snapshot_json


def test_get_api_token_not_found(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    response = client.get("/api-tokens/999", headers=_auth(auth))
    assert response.status_code == 404


def test_get_api_token_no_auth(client: TestClient):
    target = ApiTokenFactory()
    response = client.get(f"/api-tokens/{target.id}")
    assert response.status_code == 401


def test_get_api_token_insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])
    target = ApiTokenFactory()
    response = client.get(f"/api-tokens/{target.id}", headers=_auth(auth))
    assert response.status_code == 403


def test_delete_api_token(client: TestClient, session: Session):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])
    target = ApiTokenFactory()

    response = client.delete(f"/api-tokens/{target.id}", headers=_auth(auth))

    assert response.status_code == 204
    session.expire_all()
    assert session.get(ApiToken, target.id) is None


def test_delete_api_token_not_found(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_write])
    response = client.delete("/api-tokens/999", headers=_auth(auth))
    assert response.status_code == 404


def test_delete_api_token_no_auth(client: TestClient):
    target = ApiTokenFactory()
    response = client.delete(f"/api-tokens/{target.id}")
    assert response.status_code == 401


def test_delete_api_token_insufficient_scope(client: TestClient):
    auth = ApiTokenFactory(scopes=[Scope.api_token_read])
    target = ApiTokenFactory()
    response = client.delete(f"/api-tokens/{target.id}", headers=_auth(auth))
    assert response.status_code == 403

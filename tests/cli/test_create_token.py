from datetime import date

from sqlmodel import Session, select
from typer.testing import CliRunner

from app.cli import app
from app.models.api_token import ApiToken, Scope

runner = CliRunner()


def test_create_token(engine):
    result = runner.invoke(app, ["create-token", "My Token"])

    assert result.exit_code == 0
    token_value = result.output.strip()
    assert len(token_value) >= 32

    with Session(engine) as session:
        token = session.exec(select(ApiToken).where(ApiToken.name == "My Token")).one()
        assert token.token == token_value
        assert token.scopes == list(Scope)
        assert token.expires_at is not None


def test_create_token__with_scopes(engine):
    result = runner.invoke(
        app,
        [
            "create-token",
            "Scoped Token",
            "--scopes",
            "brand_write",
            "--scopes",
            "car_model_write",
        ],
    )

    assert result.exit_code == 0

    with Session(engine) as session:
        token = session.exec(
            select(ApiToken).where(ApiToken.name == "Scoped Token")
        ).one()
        assert token.scopes == [Scope.brand_write, Scope.car_model_write]


def test_create_token__with_expires_at(engine):
    result = runner.invoke(
        app, ["create-token", "Expiring Token", "--expires-at", "2027-06-30"]
    )

    assert result.exit_code == 0

    with Session(engine) as session:
        token = session.exec(
            select(ApiToken).where(ApiToken.name == "Expiring Token")
        ).one()
        assert token.expires_at == date(2027, 6, 30)


def test_create_token__invalid_date():
    result = runner.invoke(
        app, ["create-token", "Bad Token", "--expires-at", "not-a-date"]
    )

    assert result.exit_code == 1

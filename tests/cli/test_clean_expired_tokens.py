from datetime import date, timedelta

from sqlmodel import Session, select
from typer.testing import CliRunner

from app.cli import app
from app.models.api_token import ApiToken

runner = CliRunner()


def test_clean_expired_tokens(engine):
    with Session(engine) as session:
        session.add(
            ApiToken(
                name="Expired 1", expires_at=date.today() - timedelta(days=1), scopes=[]
            )
        )
        session.add(
            ApiToken(
                name="Expired 2",
                expires_at=date.today() - timedelta(days=30),
                scopes=[],
            )
        )
        session.add(
            ApiToken(
                name="Valid", expires_at=date.today() + timedelta(days=10), scopes=[]
            )
        )
        session.commit()

    result = runner.invoke(app, ["clean-expired-tokens"])

    assert result.exit_code == 0
    assert "2" in result.output

    with Session(engine) as session:
        remaining = session.exec(select(ApiToken)).all()
        assert len(remaining) == 1
        assert remaining[0].name == "Valid"


def test_clean_expired_tokens__keeps_no_expiry(engine):
    with Session(engine) as session:
        session.add(ApiToken(name="No Expiry", expires_at=None, scopes=[]))
        session.add(
            ApiToken(
                name="Expired", expires_at=date.today() - timedelta(days=1), scopes=[]
            )
        )
        session.commit()

    result = runner.invoke(app, ["clean-expired-tokens"])

    assert result.exit_code == 0

    with Session(engine) as session:
        remaining = session.exec(select(ApiToken)).all()
        assert len(remaining) == 1
        assert remaining[0].name == "No Expiry"


def test_clean_expired_tokens__nothing_to_delete():
    result = runner.invoke(app, ["clean-expired-tokens"])

    assert result.exit_code == 0
    assert "0" in result.output

from datetime import date
from typing import Optional

import typer
from sqlmodel import Session, select

from app.database import engine
from app.models.api_token import ApiToken, Scope

app = typer.Typer()

ALL_SCOPES = list(Scope)


@app.command()
def create_token(
    name: str,
    expires_at: Optional[str] = typer.Option(
        None,
        metavar="YYYY-MM-DD",
        help="Expiration date. Defaults to TOKEN_EXPIRATION_DAYS from env.",
    ),
    scopes: Optional[list[Scope]] = typer.Option(
        None, help="Scope to grant. Repeat for multiple. Defaults to all scopes."
    ),
):
    parsed_expires_at: Optional[date] = None
    if expires_at is not None:
        try:
            parsed_expires_at = date.fromisoformat(expires_at)
        except ValueError:
            typer.echo(
                f"Invalid date format: {expires_at!r}. Expected YYYY-MM-DD.", err=True
            )
            raise typer.Exit(1)

    resolved_scopes = scopes if scopes else ALL_SCOPES

    token = ApiToken(name=name, expires_at=parsed_expires_at, scopes=resolved_scopes)

    with Session(engine) as session:
        session.add(token)
        session.commit()
        session.refresh(token)

    typer.echo(token.token)


@app.command()
def clean_expired_tokens():
    with Session(engine) as session:
        expired = session.exec(
            select(ApiToken).where(ApiToken.expires_at < date.today())
        ).all()
        for token in expired:
            session.delete(token)
        session.commit()

    typer.echo(f"Deleted {len(expired)} expired token(s).")


if __name__ == "__main__":
    app()

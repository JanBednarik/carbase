from datetime import date
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.database import get_session
from app.models.api_token import ApiToken, Scope

_bearer = HTTPBearer()


def require_scope(scope: Scope):
    def dependency(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
        session: Annotated[Session, Depends(get_session)],
    ) -> ApiToken:
        token = session.exec(
            select(ApiToken).where(ApiToken.token == credentials.credentials)
        ).first()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if token.expires_at is not None and token.expires_at < date.today():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )

        if scope not in (token.scopes or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scope"
            )

        return token

    return dependency

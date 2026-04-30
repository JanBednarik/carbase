from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import require_scope
from app.database import get_session
from app.models.api_token import (
    ApiToken,
    ApiTokenCreate,
    ApiTokenCreated,
    ApiTokenRead,
    Scope,
)

router = APIRouter(prefix="/api-tokens", tags=["api-tokens"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/", response_model=ApiTokenCreated, status_code=201)
def create_api_token(
    api_token: ApiTokenCreate,
    session: SessionDep,
    _: Annotated[ApiToken, Depends(require_scope(Scope.api_token_write))],
):
    db_token = ApiToken.model_validate(api_token)
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token


@router.get("/", response_model=list[ApiTokenRead])
def list_api_tokens(
    session: SessionDep,
    _: Annotated[ApiToken, Depends(require_scope(Scope.api_token_read))],
):
    return session.exec(select(ApiToken)).all()


@router.get("/{token_id}", response_model=ApiTokenRead)
def get_api_token(
    token_id: int,
    session: SessionDep,
    _: Annotated[ApiToken, Depends(require_scope(Scope.api_token_read))],
):
    token = session.get(ApiToken, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="API token not found")
    return token


@router.delete("/{token_id}", status_code=204)
def delete_api_token(
    token_id: int,
    session: SessionDep,
    _: Annotated[ApiToken, Depends(require_scope(Scope.api_token_write))],
):
    token = session.get(ApiToken, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="API token not found")
    session.delete(token)
    session.commit()

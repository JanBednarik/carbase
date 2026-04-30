import enum
import os
import secrets
from datetime import date, timedelta
from typing import List, Optional

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class Scope(str, enum.Enum):
    api_token_read = "api_token_read"
    api_token_write = "api_token_write"


def _default_expires_at() -> Optional[date]:
    days = os.environ.get("TOKEN_EXPIRATION_DAYS", "65")
    if days is None:
        return None
    return date.today() + timedelta(days=int(days))


class ApiToken(SQLModel, table=True):
    __tablename__ = "api_token"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    expires_at: Optional[date] = Field(default_factory=_default_expires_at)
    scopes: List[Scope] = Field(default=[], sa_column=Column(sa.ARRAY(sa.String)))

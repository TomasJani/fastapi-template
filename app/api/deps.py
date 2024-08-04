import typing
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from app.core import db, security
from app.core.config import settings
from app.domain import model
from app.models import TokenPayload
from app.service_layer import messagebus, unit_of_work

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> typing.Iterator[Session]:
    with Session(db.engine) as session:
        yield session


def get_current_user(session: "SessionDep", token: "TokenDep") -> model.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(model.User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_active_superuser(current_user: "CurrentUser") -> model.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


SessionFactoryDep = sessionmaker[Session]
UoWDep = unit_of_work.UnitOfWork
MessageBusDep = messagebus.MessageBus
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

CurrentUser = Annotated[model.User, Depends(get_current_user)]
CurrentSuperUser = Annotated[model.User, Depends(get_current_active_superuser)]

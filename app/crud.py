import typing
from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.security import get_password_hash, verify_password
from app.domain import model
from app.models import UserCreate, UserUpdate

# TODO: Move this to UoW and Commands!


def create_user(*, session: Session, user_create: UserCreate) -> model.User:
    db_obj = model.User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: model.User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data: dict[str, typing.Any] = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> model.User | None:
    statement = select(model.User).where(model.User.email == email)
    session_user = session.scalar(statement)
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> model.User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

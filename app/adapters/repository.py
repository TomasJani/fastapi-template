import typing

from sqlalchemy.orm import Session
from sqlmodel import select

from app.domain import model

T = typing.TypeVar("T")


class SeenTracker(typing.Protocol, typing.Generic[T]):
    def add(self, item: T) -> None:
        ...

    def get_all(self) -> typing.Collection[T]:
        ...


class SeenSetTracker(SeenTracker[T]):
    def __init__(self) -> None:
        self._seen: set[T] = set()

    def add(self, item: T) -> None:
        self._seen.add(item)

    def get_all(self) -> set[T]:
        return self._seen


#############
# Protocols #
#############


class EditionRepository(typing.Protocol):
    def add(self, edition: model.Edition) -> None:
        ...

    def get(self, name: str) -> model.Edition | None:
        ...

    def get_seen(self) -> typing.Collection[model.Edition]:
        ...


class UserRepository(typing.Protocol):
    def add(self, user: model.User) -> None:
        ...

    def get(self, email: str) -> model.User | None:
        ...

    def get_seen(self) -> typing.Collection[model.User]:
        ...


class AuthorRepository(typing.Protocol):
    def add(self, user: model.Author) -> None:
        ...

    def get(self, name: str) -> model.Author | None:
        ...

    def get_seen(self) -> typing.Collection[model.Author]:
        ...


###########################
# Concrete Implementation #
###########################


class SqlEditionRepository(EditionRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[model.Edition]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, edition: model.Edition) -> None:
        self.session.add(edition)
        self.seen_tracker.add(edition)

    def get(self, name: str) -> model.Edition | None:
        stmt = select(model.Edition).where(model.Edition.name == name)
        edition = self.session.scalar(stmt)
        return edition

    def get_seen(self) -> typing.Collection[model.Edition]:
        return self.seen_tracker.get_all()


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session, seen_tracker: SeenTracker[model.User]) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, user: model.User) -> None:
        self.session.add(user)
        self.seen_tracker.add(user)

    def get(self, email: str) -> model.User | None:
        stmt = select(model.User).where(model.User.email == email)
        user = self.session.scalar(stmt)
        return user

    def get_seen(self) -> typing.Collection[model.User]:
        return self.seen_tracker.get_all()


class SqlAuthorRepository(AuthorRepository):
    def __init__(
        self, session: Session, seen_tracker: SeenTracker[model.Author]
    ) -> None:
        super().__init__()
        self.session = session
        self.seen_tracker = seen_tracker

    def add(self, user: model.Author) -> None:
        self.session.add(user)
        self.seen_tracker.add(user)

    def get(self, name: str) -> model.Author | None:
        stmt = select(model.Author).where(model.Author.name == name)
        author = self.session.scalar(stmt)
        return author

    def get_seen(self) -> typing.Collection[model.Author]:
        return self.seen_tracker.get_all()

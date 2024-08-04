import typing

import svcs

from app import errors
from app.core.config import settings
from app.core.security import get_password_hash
from app.domain import commands, events, model
from app.utils import generate_new_account_email, send_email

if typing.TYPE_CHECKING:
    from . import unit_of_work


def add_author(
    cmd: commands.CreateAuthor,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        author = model.Author(name=cmd.name, books=[])
        uow.authors.add(author)
        uow.commit()


def add_book(
    cmd: commands.CreateBook,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        edition = uow.editions.get(name=cmd.name)
        if edition is None:
            edition = model.Edition(name=cmd.name, books=[])
            uow.editions.add(edition)
        edition.books.append(model.Book(name=cmd.name, authors=[]))
        uow.commit()


def add_user(
    cmd: commands.CreateUser,
    services: svcs.Container,
) -> None:
    uow = services.get(unit_of_work.UnitOfWork)
    with uow:
        user = uow.users.get(cmd.email)
        if user:
            raise errors.AlreadyExists()

        user = model.User(
            email=cmd.email,
            full_name=cmd.full_name,
            hashed_password=get_password_hash(cmd.password.get_secret_value()),
        )
        uow.users.add(user)
        user.send_verification_email()
        uow.commit()


def send_new_account_email(
    event: events.NotifyNewAccount,
    services: svcs.Container,
) -> None:
    if settings.emails_enabled:
        email_data = generate_new_account_email(
            email_to=event.email, username=event.email
        )
        send_email(
            email_to=event.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )


EVENT_HANDLERS: events.EventHandlersConfig = {
    events.NotifyNewAccount: (send_new_account_email,)
}

COMMAND_HANDLERS: commands.CommandHandlerConfig = {
    commands.CreateAuthor: add_author,
    commands.CreateBook: add_book,
    commands.CreateUser: add_user,
}

import typing

import svcs
from pydantic import BaseModel, EmailStr, Field, SecretStr


class Command(BaseModel):
    pass


class CommandHandler(typing.Protocol):
    def __call__(self, cmd: typing.Any, services: svcs.Container) -> None:
        ...


CommandHandlerConfig = dict[type[Command], CommandHandler]


class CreateAuthor(Command):
    name: str


class CreateBook(Command):
    name: str


class CreateUser(Command):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    password: SecretStr = Field(min_length=8, max_length=40)

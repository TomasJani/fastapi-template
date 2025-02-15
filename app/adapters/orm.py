import logging

import sqlalchemy
from sqlalchemy.orm import registry, relationship

from app.domain import model

logger = logging.getLogger(__name__)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String(255)),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
    sqlalchemy.Column("hashed_password", sqlalchemy.Text()),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean),
)


editions = sqlalchemy.Table(
    "editions",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
)

authors = sqlalchemy.Table(
    "authors",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
)

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column[model.Edition](
        "edition_id", sqlalchemy.ForeignKey("editions.id")
    ),
)

map_book_to_author = sqlalchemy.Table(
    "map_book_to_author",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column[model.Author]("author_id", sqlalchemy.ForeignKey("authors.id")),
    sqlalchemy.Column[model.Book]("book_id", sqlalchemy.ForeignKey("books.id")),
)


def start_mappers() -> None:
    logger.info("Starting mappers")
    mapper_registry = registry()

    _user_mapper = mapper_registry.map_imperatively(
        class_=model.User,
        local_table=users,
    )
    _book_mapper = mapper_registry.map_imperatively(
        model.Book,
        local_table=books,
    )

    _author_mapper = mapper_registry.map_imperatively(
        class_=model.Author,
        local_table=authors,
        properties={
            "books": relationship(
                _book_mapper,
                secondary=map_book_to_author,
                collection_class=list,
            )
        },
    )
    _edition_mapper = mapper_registry.map_imperatively(
        class_=model.Edition,
        local_table=editions,
        properties={
            "books": relationship(_book_mapper),
        },
    )

.PHONY: make-migrations migrate format lint

make-migrations:
	alembic revision --autogenerate -m $(m)

migrate:
	alembic upgrade head

format:
	ruff format

lint: 
	ruff check --fix

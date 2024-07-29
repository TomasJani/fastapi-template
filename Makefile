.PHONY: make-migrations migrate prestart start-worker

make-migrations:
	alembic revision --autogenerate

migrate:
	alembic upgrade head

.PHONY: up down setup test-api test-web

up:
	docker compose up -d --build db api web

down:
	docker compose down -v

setup:
	docker compose run --rm api uv run python manage.py migrate && \
	docker compose run --rm api uv run python manage.py seed_activity

test-api:
	docker compose run --rm api uv run pytest

test-web:
	docker compose run --rm web npm test

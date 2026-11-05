FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.31 /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

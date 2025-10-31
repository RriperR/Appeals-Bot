FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY entrypoint.sh entrypoint.sh

COPY . .

RUN chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app

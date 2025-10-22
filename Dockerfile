FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY entrypoint.sh entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

ENV PYTHONPATH=/app

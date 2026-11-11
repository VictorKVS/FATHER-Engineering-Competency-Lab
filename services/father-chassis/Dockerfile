FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config

RUN pip install --no-cache-dir ".[production]" \
    && addgroup --system father \
    && adduser --system --ingroup father --home /app father \
    && mkdir -p /app/data \
    && chown -R father:father /app

USER father

ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["uvicorn", "father.api:app", "--host", "0.0.0.0", "--port", "8080"]

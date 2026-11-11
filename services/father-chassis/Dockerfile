FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir ".[production]"
ENV PYTHONPATH=/app/src
EXPOSE 8080
CMD ["uvicorn", "father.api:app", "--host", "0.0.0.0", "--port", "8080"]

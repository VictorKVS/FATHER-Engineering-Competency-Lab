FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/fua

WORKDIR /app

RUN groupadd --gid 10001 fua \
    && useradd --uid 10001 --gid 10001 --create-home --home-dir /home/fua --shell /usr/sbin/nologin fua

COPY pyproject.toml ./
COPY father_fua ./father_fua

RUN python -m pip install --no-cache-dir --no-compile . \
    && chown -R 10001:10001 /app /home/fua

USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).read()" || exit 1

CMD ["python","-m","uvicorn","father_fua.api:app","--host","0.0.0.0","--port","8080","--no-access-log"]

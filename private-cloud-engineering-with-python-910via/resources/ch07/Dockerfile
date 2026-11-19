# syntax=docker/dockerfile:1

# Build:  docker build -t pce-ch07-good:1 --build-arg APP_VERSION=1.0.0 .
# Run:    docker run -d --name pce-ch07-good -p 18000:8000 pce-ch07-good:1
#
# Pin the base images. A tag can move; for a fully repeatable build add the
# digest as well, for example python:3.13-slim-bookworm@sha256:<digest>.

# ---- stage 1: build the virtual environment (has pip and compilers) ----
FROM python:3.13-bookworm AS build
WORKDIR /src
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
# Dependencies first: this layer stays cached until requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Source last: editing service.py only rebuilds from here.
COPY app/ ./app/

# ---- stage 2: the runtime image (slim, no build tools, not root) ----
FROM python:3.13-slim-bookworm AS runtime
# ARG exists only while building; the ENV below copies it so the app can read it.
ARG APP_VERSION=dev
LABEL org.opencontainers.image.version=$APP_VERSION
RUN groupadd -r app && useradd --no-log-init -r -g app app
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --from=build /src/app/ ./
# ENV is kept in the image and can be overridden with docker run -e.
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_VERSION=$APP_VERSION
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
# Exec form: python is PID 1 and receives SIGTERM from docker stop.
ENTRYPOINT ["python", "/app/service.py"]

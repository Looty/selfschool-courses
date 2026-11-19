FROM python:3.13-slim-bookworm
WORKDIR /app
COPY api.py worker.py probe.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/api.py"]

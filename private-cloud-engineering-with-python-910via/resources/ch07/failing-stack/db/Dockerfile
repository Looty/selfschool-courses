FROM python:3.13-slim-bookworm
WORKDIR /app
COPY db.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 7000
ENTRYPOINT python /app/db.py; echo "db: process exited"

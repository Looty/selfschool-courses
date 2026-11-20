FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app_fastapi.py tasks.py ./

RUN useradd --system --no-create-home vmapi
USER vmapi

EXPOSE 8000
# The same image runs the worker; compose.yaml overrides the command for it.
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "--access-logfile=-", "app:create_app()"]

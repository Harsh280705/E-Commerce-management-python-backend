FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better layer caching).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code: backend/app + backend/celery_app.py land at /app/*.
COPY app ./app
COPY celery_app.py ./celery_app.py

EXPOSE 8000

# Overridden by docker-compose for the Celery worker service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

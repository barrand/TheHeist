FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app/ backend/app/
COPY backend/run.py backend/
COPY backend/scripts/ backend/scripts/
COPY shared_data/ shared_data/

RUN mkdir -p backend/experiences backend/generated_images

# Create a minimal .env at the project root (secrets come via Cloud Run env vars)
RUN echo "GEMINI_API_KEY=from-env" > .env

ENV PORT=8000
EXPOSE 8000

WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

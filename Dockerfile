# React frontend
    FROM node:20-slim AS frontend
    WORKDIR /frontend
    COPY frontend/package*.json ./
    RUN npm install
    COPY frontend/ ./
    RUN npm run build          # outputs static files to /frontend/dist
    
    # Python backend
    FROM python:3.12-slim
    WORKDIR /app
    
    # system deps for psycopg2
    RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
    
    COPY backend/requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY backend/ ./backend/
    COPY data/papers ./data/papers
    # copy the built frontend from stage 1 into a folder FastAPI will serve
    COPY --from=frontend /frontend/dist ./frontend_dist
    
    WORKDIR /app/backend
    ENV PYTHONPATH=/app/backend
    
    # Render provides $PORT
    CMD ["sh", "-c", "python scripts/create_schema.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
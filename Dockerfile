
# Stage 1: Build React frontend
FROM node:20-slim AS frontend-build

WORKDIR /frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend and combined application
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

COPY --from=frontend-build /frontend/dist ./frontend/dist

# Keep the original full dataset in the image.
COPY DATASET.csv ./DATASET.csv

ENV PYTHONPATH=/app/backend
ENV DATABASE_URL=sqlite:////tmp/astroexpert.db

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

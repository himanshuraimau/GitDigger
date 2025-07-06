# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Create necessary directories for uploads and database
RUN mkdir -p uploaded_files data

# Set Python path
ENV PYTHONPATH=/app

# Copy source code (do this after dependencies to optimize caching)
COPY src/ ./src/
COPY .env.example .env

# Expose port
EXPOSE 8000

# Initialize database and start server
CMD ["sh", "-c", "rm -f /app/gitdigger.db /app/data/gitdigger.db && uv run python -c \"import sys; sys.path.append('/app'); from src.models.database import create_tables; create_tables(); print('Database initialized successfully')\" && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]

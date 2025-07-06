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

# Copy source code
COPY src/ ./src/
COPY .env.example .env

# Create necessary directories for uploads and database
RUN mkdir -p uploaded_files data

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Initialize database and start server
CMD uv run python -c "import sys; sys.path.append('/app'); from src.models.database import create_tables; create_tables(); print('Database initialized successfully')" && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# GitDigger

A simple API service to upload PDF documents, extract company information using LLM, and get GitHub organization data.

## Features
- Upload PDF and process it
- Extract company names using LLM
- Get GitHub organization members
- Data saved in SQLite

## Quick Start

### Prerequisites
- Python 3.8+ and [uv](https://docs.astral.sh/uv/) (for local dev)
- Docker (for containerized run)

### Local Development

```bash
# Clone the repository
git clone https://github.com/himanshuraimau/GitDigger.git
cd GitDigger

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
uv run python -c "from src.models.database import create_tables; create_tables()"

# Start the server
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker (Recommended for Production)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run manually
docker build -t gitdigger .
docker run -p 8000:8000 --env-file .env gitdigger
```

The API will be available at http://localhost:8000
Docs: http://localhost:8000/docs

## Environment Variables
- `GEMINI_API_KEY` - Your Google Gemini API key
- `GITHUB_ACCESS_TOKEN` - Your GitHub access token

## API Endpoints
- `POST /api/documents/upload` - Upload a PDF
- `GET /api/documents/status/{job_id}` - Check job status

## Dependency Management
- Add package: `uv add <package-name>`
- Add dev package: `uv add --dev <package-name>`
- Sync: `uv sync`

## Project Structure
```
src/
├── api/        # FastAPI routes and app
├── models/     # Database models
├── services/   # PDF, LLM, GitHub logic
├── config/     # Config files
└── utils/      # Utilities
```

MIT
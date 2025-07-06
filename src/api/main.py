from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import documents
import datetime


app = FastAPI(
    title="GitDigger API",
    description="PDF to GitHub company data extraction service",
    version="0.1.0"
)


cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()} # type: ignore

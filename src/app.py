import os
import sys
import uvicorn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import app
from src.models.database import create_tables
from src.config.config import UPLOAD_DIR

def init_app():
    create_tables()
    print("Database tables initialized")
    
    return app

if __name__ == "__main__":
    app = init_app()
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)

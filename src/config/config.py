import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database
DB_PATH = os.path.join(BASE_DIR, "gitdigger.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Upload directory
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# GitHub API
GITHUB_API_URL = "https://api.github.com"
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "")

# Simulate long-running process with delays
SIMULATION_DELAY = 30  # seconds

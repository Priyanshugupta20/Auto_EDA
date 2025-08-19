import os
from pathlib import Path

# Base directories
CURRENT_DIR = Path(__file__).parent.resolve()      # utils/
SRC_DIR = CURRENT_DIR.parent                       # src/
BACKEND_DIR = SRC_DIR.parent                       # backend/
FRONTEND_DIR = BACKEND_DIR.parent / 'frontend'

# Folder paths
UPLOAD_FOLDER = BACKEND_DIR / 'upload'
OUTPUT_FOLDER = BACKEND_DIR / 'outputs'

# Allowed dataset file types
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

# Server settings
APP_TITLE = "Automated Data Cleaning API"
APP_DESCRIPTION = "Backend service for uploading, cleaning, and analyzing datasets."
APP_VERSION = "1.0.0"
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

# CORS settings (for frontend integration)
ALLOWED_ORIGINS = ["*"]  # Change to ["http://localhost:3000"] or your domain in production

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
import os

# Base directory for backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload & cleaned file folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned")

# Allowed dataset file types
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}

# Server settings
APP_TITLE = "Automated Data Cleaning API"
APP_DESCRIPTION = "Backend service for uploading, cleaning, and analyzing datasets."
APP_VERSION = "1.0.0"

# CORS settings (for frontend integration)
ALLOWED_ORIGINS = ["*"]  # Change to ["http://localhost:3000"] or your domain in production

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

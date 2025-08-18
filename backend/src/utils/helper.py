from pathlib import Path
from utils.config import ALLOWED_EXTENSIONS
import os
import logging

def setup_logging(log_file_path='backend/outputs/pipeline.log'):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, mode='w'),
            logging.StreamHandler()
        ]
    )


def allowed_file(filename):
    suffix = Path(filename).suffix.lower()
    return suffix and suffix in ALLOWED_EXTENSIONS

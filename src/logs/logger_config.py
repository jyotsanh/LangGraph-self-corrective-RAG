import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Logging Configuration
LOG_FILE = os.path.join(log_dir, "app.log")

# Create a rotating file handler (max size 5MB, keeps 3 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.INFO)

# Define log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
file_handler.setFormatter(formatter)

# Get logger instance
logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Optional: Also log to console in development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info("Logging is now configured.")

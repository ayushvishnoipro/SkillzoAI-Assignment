"""
Logging utilities for the application
"""
import logging
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)

# Create app logger
app_logger = logging.getLogger("resume_analysis")
app_logger.setLevel(logging.INFO)

# Set debug level from environment variable if present
if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes"):
    app_logger.setLevel(logging.DEBUG)
    app_logger.debug("Debug logging enabled")

# Reduce log verbosity for watchfiles
logging.getLogger("watchfiles").setLevel(logging.WARNING)

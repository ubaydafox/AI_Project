import logging
import logging.handlers
import os
from pathlib import Path

# Base directory of the project (directory containing this file)
BASE_DIR: Path = Path(__file__).resolve().parent

# Directory where JSON data files reside
DATA_DIR: Path = BASE_DIR / "data"

# Default batch used when a user hasn't registered
DEFAULT_BATCH: str = "CSE-58B"

# Day name mappings (English -> Bengali)
DAY_MAPPING_EN_TO_BN: dict[str, str] = {
    "Sunday": "রবিবার",
    "Monday": "সোমবার",
    "Tuesday": "মঙ্গলবার",
    "Wednesday": "বুধবার",
    "Thursday": "বৃহস্পতিবার",
    "Friday": "শুক্রবার",
    "Saturday": "শনিবার",
}

# Ordered day lists for weekly calculations
DAY_ORDER_EN: list[str] = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DAY_ORDER_BN: list[str] = ["শনিবার", "রবিবার", "সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার"]

# Logging configuration
IS_VERCEL = "VERCEL" in os.environ
logging.getLogger().setLevel(logging.INFO)

if not IS_VERCEL:
    # Rotating file handler (max 5 MB per file, keep 3 backups) - Only for local development
    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE: Path = LOG_DIR / "bot.log"
    
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
else:
    # On Vercel, logging to stdout is sufficient
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)

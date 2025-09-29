# src/config.py

import os
from dotenv import load_dotenv

# Load variables from a local .env into environment variables (only if .env present)
load_dotenv()

# Read env variables into Python constants used by the app
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
REGION_CODE = os.getenv("REGION_CODE", "PH")                # default to PH


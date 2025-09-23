#!/bin/bash
# Find the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to the project root (one level up from script folder)
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source venv/Scripts/activate

# Run the ETL script and save logs
py src/etl_runner.py >> logs/etl.log 2>&1

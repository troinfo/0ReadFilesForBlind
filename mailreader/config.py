# config.py
import platform
import os
import sys

# Determine if running as executable or script
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_path = os.path.dirname(sys.executable)
else:
    # Running as script
    app_path = os.path.dirname(os.path.abspath(__file__))

# Detect platform
if platform.system() == "Windows":
    POPPLER_PATH = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'Library', 'bin')
else:
    POPPLER_PATH = "/usr/bin"

# Define log file path
LOG_FILE = os.path.join(app_path, "logs", "application.log")

# Define default output path
DEFAULT_OUTPUT_PATH = os.path.join(app_path, "output")

# Create the default output directory if it doesn't exist
if not os.path.exists(DEFAULT_OUTPUT_PATH):
    os.makedirs(DEFAULT_OUTPUT_PATH)

# Default summary length
DEFAULT_SUMMARY_LENGTH = {"max_length": 100, "min_length": 50}
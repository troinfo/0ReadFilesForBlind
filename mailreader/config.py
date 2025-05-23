import platform
import os

# Detect platform
if platform.system() == "Windows":
    POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"
else:
    POPPLER_PATH = "/usr/bin"

# Verify Poppler path exists
if not os.path.exists(POPPLER_PATH):
    raise FileNotFoundError(f"Poppler not found at {POPPLER_PATH}. Please install it.")

# Define log file path
LOG_FILE = "application.log"

# Define default output path
DEFAULT_OUTPUT_PATH = os.path.join(os.getcwd(), "output")

# Create the default output directory if it doesn't exist
if not os.path.exists(DEFAULT_OUTPUT_PATH):
    os.makedirs(DEFAULT_OUTPUT_PATH)

# Default summary length
DEFAULT_SUMMARY_LENGTH = {"max_length": 100, "min_length": 50}

# setup_dependencies.py

import os
import subprocess

def install_dependencies():
    """
    Installs required Python packages.
    """
    packages = [
        "pdfplumber",
        "transformers",
        "torch",
        "tk",
    ]

    for package in packages:
        subprocess.check_call(["pip", "install", package])

    # Verify Poppler installation
    poppler_path = "/usr/bin/poppler"
    if not os.path.exists(poppler_path):
        raise FileNotFoundError(f"Poppler is not installed or not found at {poppler_path}.")
    print("All dependencies are installed.")

if __name__ == "__main__":
    install_dependencies()

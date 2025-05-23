# dependency_installers.py - All installation functions isolated
import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tempfile
import importlib
import logging

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin():
    """Check if the script is running with administrative privileges"""
    try:
        return os.getuid() == 0  # For Unix systems
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # For Windows

def check_package_installed(package_name):
    """Check if a Python package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_python_package_safe(package, progress_text=None):
    """Extra-safe Python package installation to prevent process crashes"""
    try:
        if progress_text:
            progress_text.set(f"Installing {package}...")
        
        logger.info(f"Starting SAFE installation of {package}")
        
        # For soundfile specifically, try alternative installation methods
        if package == "soundfile":
            logger.info("Using special handling for soundfile")
            
            # Method 1: Try installing libsndfile first (soundfile dependency)
            try:
                logger.info("Attempting to install libsndfile dependency...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "--upgrade", "cffi"
                ], capture_output=True, text=True, timeout=120)
            except Exception as e:
                logger.warning(f"cffi installation failed: {e}")
            
            # Method 2: Try installing soundfile with no-cache
            install_commands = [
                [sys.executable, "-m", "pip", "install", "--no-cache-dir", "soundfile"],
                [sys.executable, "-m", "pip", "install", "--force-reinstall", "soundfile"],
                [sys.executable, "-m", "pip", "install", "--no-deps", "soundfile"],
                [sys.executable, "-m", "pip", "install", "soundfile"]
            ]
        else:
            # Standard installation for other packages
            install_commands = [
                [sys.executable, "-m", "pip", "install", "--upgrade", package],
                [sys.executable, "-m", "pip", "install", package]
            ]
        
        # Try each installation method
        for i, cmd in enumerate(install_commands):
            try:
                logger.info(f"Trying installation method {i+1} for {package}: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=180,  # 3 minute timeout
                    cwd=os.getcwd(),  # Ensure we're in the right directory
                    env=os.environ.copy()  # Use current environment
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully installed {package} using method {i+1}")
                    
                    # Verify the installation worked
                    try:
                        if package == "soundfile":
                            import soundfile
                        elif package == "numpy":
                            import numpy
                        logger.info(f"Verified {package} can be imported")
                        return True
                    except ImportError as e:
                        logger.warning(f"Package {package} installed but cannot be imported: {e}")
                        continue  # Try next method
                        
                else:
                    logger.warning(f"Method {i+1} failed with return code {result.returncode}")
                    logger.warning(f"Error output: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Method {i+1} for {package} timed out")
                continue
            except Exception as e:
                logger.error(f"Method {i+1} for {package} failed with exception: {e}")
                continue
        
        # If all methods failed
        logger.error(f"All installation methods failed for {package}")
        return False
        
    except Exception as e:
        logger.error(f"Critical error during {package} installation: {e}")
        return False

def install_python_package(package, progress_text=None):
    """Install a Python package using pip with detailed logging"""
    try:
        if progress_text:
            progress_text.set(f"Installing {package}...")
        
        logger.info(f"Starting installation of {package}")
        
        # Run pip install with detailed output
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", package
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            logger.info(f"Successfully installed {package}")
            return True
        else:
            logger.error(f"Failed to install {package}. Return code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            if progress_text:
                progress_text.set(f"Error installing {package}: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Installation of {package} timed out")
        if progress_text:
            progress_text.set(f"Installation of {package} timed out")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing {package}: {e}")
        if progress_text:
            progress_text.set(f"Error installing {package}: {str(e)[:100]}")
        return False
    """Install a Python package using pip with detailed logging"""
    try:
        if progress_text:
            progress_text.set(f"Installing {package}...")
        
        logger.info(f"Starting installation of {package}")
        
        # Run pip install with detailed output
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", package
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            logger.info(f"Successfully installed {package}")
            return True
        else:
            logger.error(f"Failed to install {package}. Return code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            if progress_text:
                progress_text.set(f"Error installing {package}: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Installation of {package} timed out")
        if progress_text:
            progress_text.set(f"Installation of {package} timed out")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing {package}: {e}")
        if progress_text:
            progress_text.set(f"Error installing {package}: {str(e)[:100]}")
        return False

def install_basic_packages(packages, progress_text=None, progress_bar=None, root_window=None):
    """Install basic required packages"""
    logger.info("Starting basic package installation")
    failed_packages = []
    
    for i, package in enumerate(packages):
        try:
            if progress_text:
                progress_text.set(f"Checking {package}...")
            if root_window:
                root_window.update()
            
            if not check_package_installed(package):
                logger.info(f"Package {package} not found, installing...")
                if not install_python_package(package, progress_text):
                    failed_packages.append(package)
                    logger.warning(f"Failed to install {package}, continuing with others")
            else:
                logger.info(f"Package {package} already installed")
            
            # Update progress bar if provided
            if progress_bar and root_window:
                progress_bar["value"] = ((i + 1) / len(packages)) * 50  # Use 50% of total progress
                root_window.update()
                
        except Exception as e:
            logger.error(f"Error processing package {package}: {e}")
            failed_packages.append(package)
    
    if failed_packages:
        logger.warning(f"Failed to install packages: {failed_packages}")
    
    return len(failed_packages) == 0, failed_packages

def install_kokoro_safe(progress_text=None):
    """Safely install Kokoro TTS with extensive error handling"""
    logger.info("Starting Kokoro TTS installation")
    
    try:
        if progress_text:
            progress_text.set("Installing Kokoro TTS dependencies...")
        
        # Step 1: Install basic dependencies first with extra safety
        basic_deps = ["numpy", "soundfile"]  # Changed order - numpy first
        for dep in basic_deps:
            logger.info(f"Installing Kokoro dependency: {dep}")
            if progress_text:
                progress_text.set(f"Installing {dep}...")
            
            # Use the safer installation method
            success = install_python_package_safe(dep, progress_text)
        
        # Step 2: Try to install phonemizer (this often fails on Windows)
        logger.info("Installing phonemizer...")
        if progress_text:
            progress_text.set("Installing phonemizer (speech processing)...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "phonemizer"
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                logger.warning(f"Phonemizer installation failed: {result.stderr}")
                if progress_text:
                    progress_text.set("Warning: Phonemizer installation failed, Kokoro may not work")
                # Continue anyway, sometimes kokoro works without it
        except Exception as e:
            logger.warning(f"Phonemizer installation error: {e}")
        
        # Step 3: Install Kokoro itself
        logger.info("Installing Kokoro TTS...")
        if progress_text:
            progress_text.set("Installing Kokoro TTS (this may take a moment)...")
        
        try:
            # Try different installation methods
            install_commands = [
                [sys.executable, "-m", "pip", "install", "kokoro>=0.9.2"],
                [sys.executable, "-m", "pip", "install", "kokoro"],
                [sys.executable, "-m", "pip", "install", "--no-deps", "kokoro"]
            ]
            
            success = False
            for cmd in install_commands:
                try:
                    logger.info(f"Trying installation command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        logger.info("Kokoro TTS installed successfully")
                        success = True
                        break
                    else:
                        logger.warning(f"Command failed: {result.stderr}")
                except Exception as cmd_error:
                    logger.warning(f"Command failed with exception: {cmd_error}")
                    continue
                    
            if not success:
                logger.error("All Kokoro installation methods failed")
                return False, "All installation methods failed"
            
        except Exception as e:
            logger.error(f"Error during Kokoro installation: {e}")
            return False, str(e)
        
        # Step 4: Test the installation
        logger.info("Testing Kokoro installation...")
        try:
            import kokoro
            logger.info("Kokoro TTS installed and importable")
            if progress_text:
                progress_text.set("Kokoro TTS installed successfully!")
            return True, "Success"
        except ImportError as e:
            logger.error(f"Kokoro installed but not importable: {e}")
            return False, f"Installation succeeded but import failed: {e}"
    
    except Exception as e:
        logger.error(f"Unexpected error during Kokoro installation: {e}")
        return False, f"Unexpected error: {e}"
        
def install_kokoro_completely_safe(progress_text=None):
    """Install Kokoro using completely isolated process to prevent crashes"""
    logger.info("Starting ISOLATED Kokoro TTS installation")
    
    try:
        if progress_text:
            progress_text.set("Installing Kokoro TTS in isolated process...")
        
        # Import the isolated installer
        from isolated_kokoro_installer import install_kokoro_isolated
        
        logger.info("Running Kokoro installation in separate process...")
        if progress_text:
            progress_text.set("Running Kokoro installation (this may take several minutes)...")
        
        # Run the isolated installation
        results = install_kokoro_isolated()
        
        # Check results
        if "error" in results:
            logger.error(f"Isolated installation failed: {results['error']}")
            return False, results["error"]
        
        # Check if import test passed
        import_result = results.get("import_test", {})
        if import_result.get("success"):
            logger.info("Kokoro installation and import test successful")
            if progress_text:
                progress_text.set("Kokoro TTS installed successfully!")
            return True, "Success"
        else:
            error_msg = import_result.get("error", "Import test failed")
            logger.error(f"Kokoro installation completed but import failed: {error_msg}")
            return False, f"Installation completed but import failed: {error_msg}"
            
    except ImportError:
        logger.error("Could not import isolated_kokoro_installer module")
        return False, "Isolated installer module not found"
    except Exception as e:
        logger.error(f"Unexpected error during isolated Kokoro installation: {e}")
        return False, f"Unexpected error: {e}"

def install_xtts_safe(progress_text=None):
    """Safely install XTTS with extensive error handling"""
    logger.info("Starting XTTS installation")
    
    try:
        if progress_text:
            progress_text.set("Installing XTTS-v2 (this may take several minutes)...")
        
        # Install TTS package
        logger.info("Installing TTS package...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "TTS"
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            logger.info("TTS package installed successfully")
            # Test the installation
            try:
                from TTS.api import TTS
                logger.info("XTTS installed and importable")
                if progress_text:
                    progress_text.set("XTTS-v2 installed successfully!")
                return True, "Success"
            except ImportError as e:
                logger.error(f"TTS installed but not importable: {e}")
                return False, f"Installation succeeded but import failed: {e}"
        else:
            logger.error(f"TTS installation failed: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error("XTTS installation timed out")
        return False, "Installation timed out"
    except Exception as e:
        logger.error(f"Unexpected error during XTTS installation: {e}")
        return False, str(e)

def install_poppler_windows(progress_text=None):
    """Install Poppler on Windows"""
    logger.info("Starting Poppler installation")
    
    try:
        if progress_text:
            progress_text.set("Downloading Poppler...")
        
        # URL for the poppler for Windows build
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip"
        poppler_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler')
        
        # Create directory if it doesn't exist
        os.makedirs(poppler_path, exist_ok=True)
        
        # Download the Poppler zip file
        temp_zip = os.path.join(tempfile.gettempdir(), "poppler.zip")
        urllib.request.urlretrieve(poppler_url, temp_zip)
        
        if progress_text:
            progress_text.set("Extracting Poppler...")
        
        # Extract the zip file
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(poppler_path)
        
        # Clean up the zip file
        os.remove(temp_zip)
        
        # Add to PATH for the current process
        bin_path = os.path.join(poppler_path, 'Library', 'bin')
        if bin_path not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + bin_path
        
        if progress_text:
            progress_text.set("Poppler installed successfully!")
        
        logger.info("Poppler installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing Poppler: {e}")
        if progress_text:
            progress_text.set(f"Error installing Poppler: {e}")
        return False

def install_tesseract_windows(progress_text=None):
    """Install Tesseract OCR on Windows"""
    logger.info("Starting Tesseract installation")
    
    try:
        if progress_text:
            progress_text.set("Downloading Tesseract OCR...")
        
        # URL for Tesseract installer
        tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
        
        # Download the Tesseract installer
        temp_installer = os.path.join(tempfile.gettempdir(), "tesseract_installer.exe")
        urllib.request.urlretrieve(tesseract_url, temp_installer)
        
        if progress_text:
            progress_text.set("Running Tesseract installer...\nPlease follow the installation prompts.")
        
        # Run the installer
        subprocess.run([temp_installer], check=True)
        
        # Clean up the installer
        os.remove(temp_installer)
        
        if progress_text:
            progress_text.set("Tesseract OCR installed successfully!")
        
        logger.info("Tesseract installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing Tesseract: {e}")
        if progress_text:
            progress_text.set(f"Error installing Tesseract OCR: {e}")
        return False

def is_ai_model_downloaded():
    """Check if the AI model is already downloaded"""
    try:
        # Get the models directory
        if 'TRANSFORMERS_CACHE' in os.environ:
            models_dir = os.environ['TRANSFORMERS_CACHE']
        else:
            models_dir = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'transformers')
        
        # Check if the BART model files exist
        bart_model_files = [
            os.path.join(models_dir, 'models--facebook--bart-large-cnn'),
            os.path.join(os.path.expanduser('~'), '.cache', 'torch', 'transformers', 'facebook', 'bart-large-cnn')
        ]
        
        for path in bart_model_files:
            if os.path.exists(path):
                return True
                
        return False
    except Exception:
        return False

def download_ai_model(progress_text=None):
    """Pre-download the AI model for summarization"""
    logger.info("Starting AI model download")
    
    # Check if model is already downloaded
    if is_ai_model_downloaded():
        if progress_text:
            progress_text.set("AI model is already downloaded.")
        logger.info("AI model already downloaded")
        return True
    
    try:
        if progress_text:
            progress_text.set("Downloading AI model for summarization (this may take a while)...")
        
        # Import transformers and download model
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
        
        if progress_text:
            progress_text.set("AI model downloaded successfully!")
        
        logger.info("AI model downloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error downloading AI model: {e}")
        if progress_text:
            progress_text.set(f"Warning: Could not pre-download AI model: {e}")
        return False
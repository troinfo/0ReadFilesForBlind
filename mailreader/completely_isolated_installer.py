# completely_isolated_installer.py - Clean version without duplicates
import subprocess
import sys
import os
import json
import tempfile
import time

def create_installation_script():
    """Create a completely isolated installation script"""
    install_script = '''
import subprocess
import sys
import os
import json
import time

def install_package_safely(package):
    """Install a single package with detailed reporting"""
    print(f"Starting installation of {package}...")
    
    try:
        # Use very conservative installation approach
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", package
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print(f"Successfully installed {package}")
            
            # Test import if possible
            try:
                if package == "numpy":
                    import numpy
                elif package == "soundfile":
                    import soundfile
                elif package == "pygame":
                    import pygame
                elif package == "pdfplumber":
                    import pdfplumber
                elif package == "torch":
                    import torch
                print(f"Successfully imported {package}")
                return {"success": True, "message": f"Installed and verified {package}"}
            except ImportError as e:
                print(f"Installed {package} but import failed: {e}")
                return {"success": False, "error": f"Import failed: {e}"}
                
        else:
            print(f"Installation failed for {package}: {result.stderr}")
            return {"success": False, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        print(f"Installation of {package} timed out")
        return {"success": False, "error": "Installation timed out"}
    except Exception as e:
        print(f"Unexpected error installing {package}: {e}")
        return {"success": False, "error": str(e)}

def main():
    print("Starting isolated package installation...")
    
    # Get package list from command line or use default
    if len(sys.argv) > 1:
        packages = sys.argv[1].split(",")
    else:
        packages = [
            "pdfplumber", "pdf2image", "pytesseract", "pyttsx3",
            "transformers", "torch", "torchvision", "torchaudio", "pygame"
        ]
    
    # Get results file path from command line (if provided)
    if len(sys.argv) > 2:
        results_file = sys.argv[2]
    else:
        results_file = "installation_results.json"
    
    print(f"Installing packages: {packages}")
    print(f"Results will be written to: {results_file}")
    
    results = {}
    
    for package in packages:
        print(f"\\n=== Installing {package} ===")
        result = install_package_safely(package)
        results[package] = result
        
        if not result["success"]:
            print(f"Failed to install {package}, stopping installation")
            break
        
        # Small delay between packages
        time.sleep(1)
    
    # Write results to the specified file path
    try:
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {results_file}")
        
        # Verify the file was created
        if os.path.exists(results_file):
            print(f"Results file verified at {results_file}")
        else:
            print(f"ERROR: Results file was not created at {results_file}")
            
    except Exception as e:
        print(f"ERROR writing results to {results_file}: {e}")
    
    print("\\nInstallation process complete")

if __name__ == "__main__":
    main()
'''
    return install_script

def install_packages_isolated(packages, progress_text=None):
    """Install packages in a completely separate process - PyInstaller compatible version"""
    print(f"Starting isolated installation of packages: {packages}")
    
    # Create the installation script
    script_content = create_installation_script()
    temp_script = os.path.join(tempfile.gettempdir(), "isolated_installer.py")
    
    # Use absolute path for results file in the MAIN process directory
    main_process_dir = os.getcwd()
    results_file = os.path.join(main_process_dir, "installation_results.json")
    
    try:
        # Write the script
        with open(temp_script, "w") as f:
            f.write(script_content)
        
        # Prepare package list
        package_list = ",".join(packages)
        
        if progress_text:
            progress_text.set(f"Installing packages in isolated process...")
        
        print(f"Running isolated installer with packages: {package_list}")
        print(f"Results will be written to: {results_file}")
        
        # CRITICAL: Use the actual Python executable, not sys.executable when frozen
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable - use embedded Python
            python_exe = os.path.join(sys._MEIPASS, 'python.exe')
            if not os.path.exists(python_exe):
                # Fallback: try to find Python in the system
                python_exe = 'python'
        else:
            # Running as script - use current Python
            python_exe = sys.executable
        
        print(f"Using Python executable: {python_exe}")
        
        # Run the installation in a separate process
        process = subprocess.Popen([
            python_exe, temp_script, package_list, results_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
           cwd=main_process_dir,
           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)  # Create new console on Windows
        
        # Wait for completion with timeout
        stdout, stderr = process.communicate(timeout=1800)  # 30 minute timeout
        
        print(f"Installation process completed with return code: {process.returncode}")
        print(f"Output: {stdout}")
        
        if stderr:
            print(f"Errors: {stderr}")
        
        # Read results from the specified location
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                results = json.load(f)
            
            # Clean up
            os.remove(results_file)
            
            return results
        else:
            return {"error": f"Results file not created at {results_file}"}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Installation timed out"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Clean up temp files
        if os.path.exists(temp_script):
            os.remove(temp_script)

def install_kokoro_isolated():
    """Install Kokoro TTS packages in isolated process"""
    kokoro_packages = ["numpy", "soundfile", "phonemizer", "kokoro>=0.9.2"]
    return install_packages_isolated(kokoro_packages)

if __name__ == "__main__":
    # Test the isolated installer
    test_packages = ["numpy", "pygame"]
    results = install_packages_isolated(test_packages)
    print("Final results:")
    print(json.dumps(results, indent=2))
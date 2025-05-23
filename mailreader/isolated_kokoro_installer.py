# isolated_kokoro_installer.py - Run Kokoro installation in completely separate process
import subprocess
import sys
import os
import json
import tempfile

def install_kokoro_isolated():
    """Install Kokoro in a completely separate Python process"""
    
    # Create a temporary script for isolated installation
    install_script = '''
import subprocess
import sys
import os
import json

def install_package(package):
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", package
        ], capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    print("Starting isolated Kokoro installation...")
    
    # Install dependencies
    packages = ["numpy", "cffi", "soundfile", "phonemizer", "kokoro>=0.9.2"]
    results = {}
    
    for package in packages:
        print(f"Installing {package}...")
        result = install_package(package)
        results[package] = result
        
        if not result["success"]:
            print(f"Failed to install {package}: {result.get('stderr', result.get('error', 'Unknown error'))}")
            break
        else:
            print(f"Successfully installed {package}")
    
    # Test import
    try:
        import kokoro
        results["import_test"] = {"success": True}
        print("Kokoro import test successful")
    except ImportError as e:
        results["import_test"] = {"success": False, "error": str(e)}
        print(f"Kokoro import failed: {e}")
    
    # Write results to file
    with open("kokoro_install_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Installation process complete")

if __name__ == "__main__":
    main()
'''
    
    # Write the script to a temporary file
    temp_script = os.path.join(tempfile.gettempdir(), "kokoro_installer.py")
    with open(temp_script, "w") as f:
        f.write(install_script)
    
    try:
        # Run the installation in a separate process
        print("Starting isolated Kokoro installation process...")
        
        # Use subprocess.Popen for better control
        process = subprocess.Popen([
            sys.executable, temp_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for completion with timeout
        stdout, stderr = process.communicate(timeout=600)  # 10 minute timeout
        
        print(f"Installation process completed with return code: {process.returncode}")
        print(f"Output: {stdout}")
        
        if stderr:
            print(f"Errors: {stderr}")
        
        # Read results
        results_file = "kokoro_install_results.json"
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                results = json.load(f)
            
            # Clean up
            os.remove(results_file)
            os.remove(temp_script)
            
            return results
        else:
            return {"error": "Results file not created"}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Installation timed out"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Clean up temp files
        if os.path.exists(temp_script):
            os.remove(temp_script)

if __name__ == "__main__":
    results = install_kokoro_isolated()
    print("Final results:")
    print(json.dumps(results, indent=2))
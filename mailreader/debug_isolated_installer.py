# debug_isolated_installer.py - Diagnostic version to find the issue
import subprocess
import sys
import os
import json
import tempfile
import time

def test_basic_subprocess():
    """Test if we can run a basic subprocess at all"""
    print("Testing basic subprocess functionality...")
    
    try:
        # Test very basic subprocess
        result = subprocess.run([sys.executable, "-c", "print('Hello from subprocess')"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✓ Basic subprocess works: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ Basic subprocess failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Basic subprocess error: {e}")
        return False

def test_package_check():
    """Test if we can check for packages in a subprocess"""
    print("Testing package checking in subprocess...")
    
    test_script = '''
import sys
try:
    import pdfplumber
    print("pdfplumber: INSTALLED")
except ImportError:
    print("pdfplumber: NOT INSTALLED")

try:
    import pygame
    print("pygame: INSTALLED") 
except ImportError:
    print("pygame: NOT INSTALLED")

print("Package check complete")
'''
    
    try:
        temp_script = os.path.join(tempfile.gettempdir(), "package_check.py")
        with open(temp_script, "w") as f:
            f.write(test_script)
        
        result = subprocess.run([sys.executable, temp_script], 
                              capture_output=True, text=True, timeout=60)
        
        print(f"Package check result (return code {result.returncode}):")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        os.remove(temp_script)
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Package check error: {e}")
        return False

def test_file_writing():
    """Test if subprocess can write files"""
    print("Testing file writing in subprocess...")
    
    test_script = '''
import json
import os

try:
    test_data = {"test": "success", "message": "File writing works"}
    
    with open("test_results.json", "w") as f:
        json.dump(test_data, f)
    
    print("File written successfully")
    
    # Verify file exists
    if os.path.exists("test_results.json"):
        print("File exists and can be read")
        with open("test_results.json", "r") as f:
            data = json.load(f)
        print(f"File content: {data}")
    else:
        print("ERROR: File was not created")
        
except Exception as e:
    print(f"ERROR writing file: {e}")
'''
    
    try:
        temp_script = os.path.join(tempfile.gettempdir(), "file_test.py")
        with open(temp_script, "w") as f:
            f.write(test_script)
        
        # Run from the main directory to ensure file is created in the right place
        result = subprocess.run([sys.executable, temp_script], 
                              capture_output=True, text=True, timeout=60,
                              cwd=os.getcwd())
        
        print(f"File writing test result (return code {result.returncode}):")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        # Check if the test file was created
        test_file = "test_results.json"
        if os.path.exists(test_file):
            print("✓ Test file was created successfully")
            os.remove(test_file)
        else:
            print("✗ Test file was NOT created")
        
        os.remove(temp_script)
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ File writing test error: {e}")
        return False

def test_pip_in_subprocess():
    """Test if pip works in subprocess"""
    print("Testing pip in subprocess...")
    
    test_script = '''
import subprocess
import sys

try:
    # Test pip list command
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print("pip list works")
        # Show first few lines
        lines = result.stdout.split('\\n')[:5]
        for line in lines:
            if line.strip():
                print(f"  {line}")
    else:
        print(f"pip list failed: {result.stderr}")
        
except Exception as e:
    print(f"pip test error: {e}")
'''
    
    try:
        temp_script = os.path.join(tempfile.gettempdir(), "pip_test.py")
        with open(temp_script, "w") as f:
            f.write(test_script)
        
        result = subprocess.run([sys.executable, temp_script], 
                              capture_output=True, text=True, timeout=120)
        
        print(f"Pip test result (return code {result.returncode}):")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        os.remove(temp_script)
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Pip test error: {e}")
        return False

def run_diagnostics():
    """Run all diagnostic tests"""
    print("=" * 50)
    print("ISOLATED INSTALLER DIAGNOSTICS")
    print("=" * 50)
    
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Temp directory: {tempfile.gettempdir()}")
    print()
    
    tests = [
        ("Basic Subprocess", test_basic_subprocess),
        ("Package Checking", test_package_check),
        ("File Writing", test_file_writing),
        ("Pip in Subprocess", test_pip_in_subprocess)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results[test_name] = False
        print()
    
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\nThe isolated installer won't work until these issues are resolved.")
        print("Check the error messages above for clues.")
    
    return all_passed

if __name__ == "__main__":
    run_diagnostics()
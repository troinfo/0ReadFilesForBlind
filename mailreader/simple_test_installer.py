# simple_test_installer.py - Minimal test version to isolate the issue
import subprocess
import sys
import os
import json
import tempfile

def create_simple_installer_script():
    """Create a very simple installer script for testing"""
    script = '''
import json
import sys
import os

def main():
    print("Simple installer started")
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    
    # Just create a simple success result
    results = {
        "test_package": {
            "success": True,
            "message": "Test installation successful"
        }
    }
    
    print("Writing results file...")
    try:
        with open("simple_install_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Results file written successfully")
        
        # Verify file exists
        if os.path.exists("simple_install_results.json"):
            print("Results file verified to exist")
        else:
            print("ERROR: Results file does not exist after writing")
            
    except Exception as e:
        print(f"ERROR writing results file: {e}")
    
    print("Simple installer completed")

if __name__ == "__main__":
    main()
'''
    return script

def test_simple_isolated_install():
    """Test a simplified version of the isolated installer"""
    print("Testing simplified isolated installer...")
    
    # Create the simple script
    script_content = create_simple_installer_script()
    temp_script = os.path.join(tempfile.gettempdir(), "simple_installer.py")
    
    try:
        # Write the script
        with open(temp_script, "w") as f:
            f.write(script_content)
        
        print(f"Created script at: {temp_script}")
        print("Running isolated installer...")
        
        # Run the installation in a separate process
        process = subprocess.Popen([
            sys.executable, temp_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for completion with timeout
        stdout, stderr = process.communicate(timeout=60)
        
        print(f"Process completed with return code: {process.returncode}")
        print("--- STDOUT ---")
        print(stdout)
        
        if stderr:
            print("--- STDERR ---")
            print(stderr)
        
        # Check for results file
        results_file = "simple_install_results.json"
        if os.path.exists(results_file):
            print(f"✓ Results file created successfully!")
            with open(results_file, "r") as f:
                results = json.load(f)
            print(f"Results content: {json.dumps(results, indent=2)}")
            
            # Clean up
            os.remove(results_file)
            return True
        else:
            print("✗ Results file was NOT created")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("✗ Process timed out")
        return False
    except Exception as e:
        print(f"✗ Error running simple installer: {e}")
        return False
    finally:
        # Clean up temp script
        if os.path.exists(temp_script):
            os.remove(temp_script)

def test_real_installer_script():
    """Test the exact script from completely_isolated_installer"""
    print("\nTesting the real installer script...")
    
    # Import and test the real function
    try:
        from completely_isolated_installer import install_packages_isolated
        
        print("Testing with a simple package list...")
        test_packages = ["pdfplumber"]  # Just one package that we know is installed
        
        results = install_packages_isolated(test_packages)
        
        print(f"Real installer results: {json.dumps(results, indent=2)}")
        
        if "error" in results:
            print(f"✗ Real installer failed: {results['error']}")
            return False
        else:
            print("✓ Real installer succeeded")
            return True
            
    except Exception as e:
        print(f"✗ Error testing real installer: {e}")
        return False

def main():
    print("=" * 60)
    print("SIMPLE INSTALLER TEST")
    print("=" * 60)
    
    # Test 1: Simple version
    simple_success = test_simple_isolated_install()
    
    # Test 2: Real version  
    real_success = test_real_installer_script()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Simple installer: {'✓ PASS' if simple_success else '✗ FAIL'}")
    print(f"Real installer: {'✓ PASS' if real_success else '✗ FAIL'}")
    
    if simple_success and not real_success:
        print("\nThe simple installer works but the real one doesn't.")
        print("This means there's a bug in the complex installer code.")
    elif not simple_success:
        print("\nEven the simple installer doesn't work.")
        print("There might be an environment or permissions issue.")
    else:
        print("\nBoth installers work! The issue might be elsewhere.")

if __name__ == "__main__":
    main()
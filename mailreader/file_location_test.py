# file_location_test.py - Find exactly where result files are being created
import os
import sys
import subprocess
import tempfile
import glob

def find_installation_results_files():
    """Search for installation_results.json files everywhere"""
    print("Searching for installation_results.json files...")
    
    search_locations = [
        os.getcwd(),  # Current directory
        tempfile.gettempdir(),  # Temp directory
        os.path.dirname(sys.executable),  # Python executable directory
        os.path.expanduser("~"),  # User home directory
    ]
    
    all_found_files = []
    
    for location in search_locations:
        try:
            pattern = os.path.join(location, "*installation_results.json*")
            found_files = glob.glob(pattern)
            if found_files:
                print(f"Found in {location}:")
                for file in found_files:
                    print(f"  - {file}")
                    # Check file age
                    import time
                    mtime = os.path.getmtime(file)
                    age = time.time() - mtime
                    print(f"    Age: {age:.1f} seconds")
                    all_found_files.extend(found_files)
        except Exception as e:
            print(f"Error searching {location}: {e}")
    
    return all_found_files

def test_file_creation_locations():
    """Test where our subprocess actually creates files"""
    print("\nTesting where subprocess creates files...")
    
    test_script = '''
import os
import json
import sys

print(f"Subprocess working directory: {os.getcwd()}")
print(f"Subprocess __file__ would be: {__file__ if '__file__' in globals() else 'Not available'}")

# Create test files in multiple locations
locations_to_test = [
    ("current_dir", "test_current.json"),
    ("absolute", os.path.abspath("test_absolute.json")),
]

for name, filepath in locations_to_test:
    try:
        with open(filepath, "w") as f:
            json.dump({"test": name, "path": filepath}, f)
        
        if os.path.exists(filepath):
            print(f"✓ Successfully created {name} at: {os.path.abspath(filepath)}")
        else:
            print(f"✗ Failed to create {name} at: {filepath}")
            
    except Exception as e:
        print(f"✗ Error creating {name}: {e}")
'''
    
    # Write and run the test script
    temp_script = os.path.join(tempfile.gettempdir(), "file_location_test.py")
    
    try:
        with open(temp_script, "w") as f:
            f.write(test_script)
        
        print(f"Running test script from: {temp_script}")
        
        # Run the script
        result = subprocess.run([sys.executable, temp_script], 
                              capture_output=True, text=True, timeout=30,
                              cwd=os.getcwd())  # Use current directory as working directory
        
        print("Subprocess output:")
        print(result.stdout)
        if result.stderr:
            print("Subprocess errors:")
            print(result.stderr)
        
        # Check for the test files
        test_files = ["test_current.json", "test_absolute.json"]
        for test_file in test_files:
            abs_path = os.path.abspath(test_file)
            if os.path.exists(abs_path):
                print(f"✓ Found test file: {abs_path}")
                os.remove(abs_path)
            else:
                print(f"✗ Test file NOT found: {abs_path}")
        
        os.remove(temp_script)
        
    except Exception as e:
        print(f"Error running file location test: {e}")

def run_installer_and_track_files():
    """Run the installer and immediately check for result files"""
    print("\nRunning installer and tracking files...")
    
    # Get list of JSON files before
    before_files = set(glob.glob("*.json"))
    print(f"JSON files before: {before_files}")
    
    # Import and run installer
    try:
        from completely_isolated_installer import install_packages_isolated
        
        print("Running installer...")
        results = install_packages_isolated(["pdfplumber"], None)
        
        # Get list of JSON files after
        after_files = set(glob.glob("*.json"))
        print(f"JSON files after: {after_files}")
        
        new_files = after_files - before_files
        if new_files:
            print(f"✓ New files created: {new_files}")
            for file in new_files:
                print(f"  Content of {file}:")
                try:
                    import json
                    with open(file, 'r') as f:
                        content = json.load(f)
                    print(f"    {content}")
                except Exception as e:
                    print(f"    Error reading: {e}")
        else:
            print("✗ No new JSON files were created")
        
        print(f"Installer returned: {results}")
        
    except Exception as e:
        print(f"Error running installer: {e}")

def main():
    print("=" * 60)
    print("FILE LOCATION DIAGNOSTIC")
    print("=" * 60)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Temp directory: {tempfile.gettempdir()}")
    
    # Test 1: Find existing files
    find_installation_results_files()
    
    # Test 2: Test where subprocesses create files
    test_file_creation_locations()
    
    # Test 3: Run installer and track file creation
    run_installer_and_track_files()

if __name__ == "__main__":
    main()
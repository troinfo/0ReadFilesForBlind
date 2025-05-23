# setup_diagnostic.py - Troubleshooting script
import os
import sys
import traceback

def check_files():
    """Check if all required files exist"""
    required_files = [
        'dependency_setup.py',
        'dependency_installers.py', 
        'setup_gui.py',
        'isolated_kokoro_installer.py'
    ]
    
    print("=== File Check ===")
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} MISSING")
            missing_files.append(file)
    
    return missing_files

def test_imports():
    """Test importing each module"""
    print("\n=== Import Test ===")
    
    modules = [
        ('dependency_installers', 'from dependency_installers import is_admin'),
        ('setup_gui', 'from setup_gui import create_setup_gui'),
        ('isolated_kokoro_installer', 'from isolated_kokoro_installer import install_kokoro_isolated')
    ]
    
    import_errors = []
    for module_name, import_statement in modules:
        try:
            exec(import_statement)
            print(f"✓ {module_name} imports successfully")
        except Exception as e:
            print(f"✗ {module_name} import failed: {e}")
            import_errors.append((module_name, str(e)))
    
    return import_errors

def test_basic_functionality():
    """Test basic tkinter functionality"""
    print("\n=== Basic Functionality Test ===")
    
    try:
        import tkinter as tk
        print("✓ tkinter imports successfully")
        
        # Test creating a basic window
        root = tk.Tk()
        root.withdraw()  # Hide it
        print("✓ Can create tkinter window")
        root.destroy()
        
    except Exception as e:
        print(f"✗ tkinter test failed: {e}")
        return False
    
    return True

def run_minimal_setup():
    """Try to run a minimal version of the setup"""
    print("\n=== Minimal Setup Test ===")
    
    try:
        # Try to import and run just the GUI creation
        from setup_gui import create_setup_gui
        print("✓ setup_gui imported successfully")
        
        # Don't actually run the GUI, just test creation
        print("✓ About to test GUI creation...")
        setup_window, complete_var = create_setup_gui()
        print("✓ GUI created successfully")
        
        # Destroy without showing
        setup_window.destroy()
        print("✓ GUI destroyed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Minimal setup failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("Mailreader Setup Diagnostic Tool")
    print("=" * 40)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Run diagnostics
    missing_files = check_files()
    import_errors = test_imports()
    tkinter_ok = test_basic_functionality()
    
    if not missing_files and not import_errors and tkinter_ok:
        minimal_setup_ok = run_minimal_setup()
        
        if minimal_setup_ok:
            print("\n=== DIAGNOSIS ===")
            print("✓ All basic checks passed!")
            print("The issue might be in the main application calling the setup.")
            print("Try running: python dependency_setup.py")
        else:
            print("\n=== DIAGNOSIS ===")
            print("✗ Minimal setup test failed - check the error above")
    else:
        print("\n=== DIAGNOSIS ===")
        if missing_files:
            print(f"✗ Missing files: {missing_files}")
        if import_errors:
            print(f"✗ Import errors: {import_errors}")
        if not tkinter_ok:
            print("✗ tkinter not working properly")

if __name__ == "__main__":
    main()
# path_diagnostics.py - Identify missing paths
import os
import sys
import traceback
import importlib.util

def check_file_exists(filepath):
    """Check if a file exists"""
    exists = os.path.isfile(filepath)
    print(f"{'✓' if exists else '✗'} File {'exists' if exists else 'missing'}: {filepath}")
    return exists

def check_directory_exists(dirpath):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    print(f"{'✓' if exists else '✗'} Directory {'exists' if exists else 'missing'}: {dirpath}")
    return exists

def check_module_imports():
    """Try to import each required module"""
    modules = [
        "ui", "pdf_processor", "summarizer", "tts_handler", "config",
        "tkinter", "pygame", "pdfplumber", "transformers"
    ]
    
    print("\n=== Module Import Tests ===")
    for module_name in modules:
        try:
            # First check if the .py file exists (for our own modules)
            if module_name in ["ui", "pdf_processor", "summarizer", "tts_handler", "config"]:
                check_file_exists(f"{module_name}.py")
            
            # Try to import it
            if importlib.util.find_spec(module_name):
                print(f"✓ Module can be imported: {module_name}")
            else:
                print(f"✗ Module cannot be found: {module_name}")
        except Exception as e:
            print(f"✗ Error checking module {module_name}: {e}")

def find_missing_referenced_files():
    """Check if files referenced in code exist"""
    
    # Files that might be referenced in code
    key_files = [
        ("Log file", os.path.join("logs", "application.log")),
        ("Config directory", "config"),
        ("Config file", os.path.join("config", "app_config.json")),
        ("Output directory", "output"),
        ("Models directory", "models"),
        ("Icon file", "app_icon.ico"),
        ("Manifest file", "mailreader.manifest")
    ]
    
    print("\n=== Referenced Files Check ===")
    for name, path in key_files:
        if os.path.exists(path):
            print(f"✓ {name} exists: {path}")
        else:
            print(f"✗ {name} missing: {path}")

def check_directory_permissions():
    """Check if we have write permissions in key directories"""
    
    directories = [
        ".", "logs", "output", "models", "config", 
        os.path.join("output", "temp")
    ]
    
    print("\n=== Directory Permissions Check ===")
    for directory in directories:
        try:
            if not os.path.exists(directory):
                print(f"✗ Cannot check permissions - directory doesn't exist: {directory}")
                continue
                
            # Try to create a test file
            test_file = os.path.join(directory, "permission_test.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ Have write permission in: {directory}")
        except Exception as e:
            print(f"✗ No write permission in {directory}: {e}")

def check_ui_imports():
    """Check if the UI module's imports work"""
    
    print("\n=== UI Module Import Check ===")
    ui_imports = [
        ("tkinter", "import tkinter as tk"),
        ("filedialog", "from tkinter import filedialog"),
        ("messagebox", "from tkinter import messagebox"),
        ("ttk", "from tkinter import ttk"),
        ("threading", "import threading"),
        ("pdf_processor", "from pdf_processor import extract_text_from_pdf"),
        ("tts_handler", "import tts_handler"),
        ("summarizer", "from summarizer import summarize_text")
    ]
    
    for name, import_stmt in ui_imports:
        try:
            exec(import_stmt)
            print(f"✓ Import succeeded: {import_stmt}")
        except Exception as e:
            print(f"✗ Import failed: {import_stmt}")
            print(f"  Error: {e}")

def check_temp_directory():
    """Check if we can access and write to temp directory"""
    
    import tempfile
    
    print("\n=== Temp Directory Check ===")
    try:
        temp_dir = tempfile.gettempdir()
        print(f"System temp directory: {temp_dir}")
        
        # Check if it exists
        if os.path.exists(temp_dir):
            print(f"✓ Temp directory exists: {temp_dir}")
        else:
            print(f"✗ Temp directory doesn't exist: {temp_dir}")
            return
        
        # Check if we can write to it
        test_file = os.path.join(temp_dir, "mailreader_test.tmp")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ Can write to temp directory")
        except Exception as e:
            print(f"✗ Cannot write to temp directory: {e}")
    except Exception as e:
        print(f"✗ Error checking temp directory: {e}")
    
    # Also check custom temp directories
    custom_temp_paths = [
        os.path.join("output", "temp"),
        "temp"
    ]
    
    for path in custom_temp_paths:
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(f"✓ Created custom temp directory: {path}")
            except Exception as e:
                print(f"✗ Cannot create custom temp directory {path}: {e}")
                continue
        
        # Test writing to it
        test_file = os.path.join(path, "mailreader_test.tmp")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ Can write to custom temp directory: {path}")
        except Exception as e:
            print(f"✗ Cannot write to custom temp directory {path}: {e}")

def main():
    """Run all diagnostics"""
    print("=" * 60)
    print("MAILREADER PATH DIAGNOSTICS")
    print("=" * 60)
    
    # Print system info
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    
    try:
        # Check the directory structure
        print("\n=== Directory Structure Check ===")
        check_directory_exists("logs")
        check_directory_exists("output")
        check_directory_exists("models")
        check_directory_exists("config")
        
        # Check for core files
        print("\n=== Core Files Check ===")
        check_file_exists("main.py")
        check_file_exists("ui.py")
        check_file_exists("pdf_processor.py")
        check_file_exists("tts_handler.py")
        check_file_exists("summarizer.py")
        check_file_exists("config.py")
        
        # Run other checks
        check_module_imports()
        find_missing_referenced_files()
        check_directory_permissions()
        check_temp_directory()
        check_ui_imports()
        
    except Exception as e:
        print(f"\nDiagnostics failed with error: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
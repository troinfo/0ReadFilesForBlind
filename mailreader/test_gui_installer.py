# test_gui_installer.py - Test the GUI integration specifically
import os
import sys

def test_gui_installer():
    """Test the installer as it would be called from the GUI"""
    print("Testing GUI installer integration...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    try:
        # Import the modules like the GUI does
        from completely_isolated_installer import install_packages_isolated
        from minimal_setup_gui import run_minimal_setup_thread
        
        print("✓ Successfully imported modules")
        
        # Test with the same basic packages the GUI uses
        basic_packages = [
            "pdfplumber", "pdf2image", "pytesseract", "pyttsx3",
            "transformers", "torch", "torchvision", "torchaudio", "pygame"
        ]
        
        print(f"Testing installation of: {basic_packages}")
        
        # Create a mock progress_text object
        class MockProgressText:
            def __init__(self):
                self.text = ""
            def set(self, text):
                self.text = text
                print(f"Progress: {text}")
        
        progress_text = MockProgressText()
        
        # Run the installer
        print("Starting isolated installation...")
        results = install_packages_isolated(basic_packages, progress_text)
        
        print(f"Installation completed")
        print(f"Results type: {type(results)}")
        print(f"Results: {results}")
        
        # Check if it's an error
        if "error" in results:
            print(f"✗ Installation failed: {results['error']}")
            return False
        
        # Check individual package results
        print("\nIndividual package results:")
        success_count = 0
        for package, result in results.items():
            success = result.get("success", False)
            if success:
                success_count += 1
                print(f"  ✓ {package}: {result.get('message', 'Success')}")
            else:
                print(f"  ✗ {package}: {result.get('error', 'Unknown error')}")
        
        print(f"\nSummary: {success_count}/{len(results)} packages successful")
        return success_count > 0
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_file_permissions():
    """Check if we can create files in the current directory"""
    print("\nTesting file creation permissions...")
    
    test_files = [
        "test_file.txt",
        "installation_results.json",
        "test_results.json"
    ]
    
    for filename in test_files:
        try:
            with open(filename, "w") as f:
                f.write("test")
            
            if os.path.exists(filename):
                print(f"✓ Can create {filename}")
                os.remove(filename)
            else:
                print(f"✗ Created {filename} but it doesn't exist")
                
        except Exception as e:
            print(f"✗ Cannot create {filename}: {e}")

def main():
    print("=" * 60)
    print("GUI INSTALLER INTEGRATION TEST")
    print("=" * 60)
    
    # Test file permissions first
    check_file_permissions()
    
    # Test the GUI installer
    success = test_gui_installer()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    
    if success:
        print("✓ GUI installer integration works!")
        print("The issue might be in the GUI thread handling or timing.")
    else:
        print("✗ GUI installer integration failed")
        print("This explains why the setup GUI isn't working.")

if __name__ == "__main__":
    main()
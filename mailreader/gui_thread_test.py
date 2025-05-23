# gui_thread_test.py - Test the installer in an actual GUI thread context
import tkinter as tk
from tkinter import ttk
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI Thread Test")
        self.root.geometry("500x300")
        
        # Variables
        self.progress_text = tk.StringVar(value="Ready to test...")
        self.status_var = tk.StringVar(value="pending")
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Title
        tk.Label(self.root, text="GUI Thread Installer Test", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Progress
        self.progress_bar = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress_bar.pack(pady=10)
        
        self.progress_label = tk.Label(self.root, textvariable=self.progress_text, wraplength=450)
        self.progress_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.test_button = tk.Button(button_frame, text="Test Installer", command=self.start_test)
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = tk.Button(button_frame, text="Close", command=self.root.destroy)
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.results_text = tk.Text(self.root, height=8, width=60)
        self.results_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
    def log_result(self, message):
        """Add a message to the results area"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def start_test(self):
        """Start the test in a separate thread"""
        self.test_button.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        
        # Start the test thread
        test_thread = threading.Thread(target=self.run_test_thread, daemon=True)
        test_thread.start()
        
    def run_test_thread(self):
        """Run the installer test in a separate thread (like the real GUI does)"""
        try:
            self.log_result("Starting GUI thread test...")
            self.progress_text.set("Testing installer in GUI thread...")
            self.progress_bar["value"] = 10
            self.root.update()
            
            # Import the installer
            from completely_isolated_installer import install_packages_isolated
            self.log_result("✓ Successfully imported installer")
            
            # Test with a small subset of packages
            test_packages = ["pdfplumber", "pygame"]  # Just 2 packages for quick test
            
            self.log_result(f"Testing packages: {test_packages}")
            self.progress_text.set("Running isolated installer...")
            self.progress_bar["value"] = 30
            self.root.update()
            
            # Create a mock progress function that updates the GUI
            def gui_progress_update(message):
                self.progress_text.set(message)
                self.log_result(f"Progress: {message}")
                self.root.update()
            
            # Mock progress object
            class MockProgress:
                def set(self, text):
                    gui_progress_update(text)
            
            mock_progress = MockProgress()
            
            # Run the installer
            self.log_result("Calling install_packages_isolated...")
            results = install_packages_isolated(test_packages, mock_progress)
            
            self.progress_bar["value"] = 80
            self.root.update()
            
            # Analyze results
            self.log_result(f"Results received: {type(results)}")
            
            if results is None:
                self.log_result("✗ Results is None!")
                self.progress_text.set("Failed: No results returned")
            elif "error" in results:
                self.log_result(f"✗ Error in results: {results['error']}")
                self.progress_text.set(f"Failed: {results['error']}")
            elif not results:
                self.log_result("✗ Results is empty!")
                self.progress_text.set("Failed: Empty results")
            else:
                self.log_result("✓ Results look good:")
                success_count = 0
                for package, result in results.items():
                    success = result.get("success", False)
                    if success:
                        success_count += 1
                        self.log_result(f"  ✓ {package}: Success")
                    else:
                        self.log_result(f"  ✗ {package}: {result.get('error', 'Failed')}")
                
                self.progress_text.set(f"Completed: {success_count}/{len(results)} packages successful")
            
            self.progress_bar["value"] = 100
            self.root.update()
            
        except Exception as e:
            self.log_result(f"✗ Exception in test thread: {e}")
            import traceback
            self.log_result(f"Full traceback:\n{traceback.format_exc()}")
            self.progress_text.set(f"Failed with exception: {e}")
        
        finally:
            # Re-enable the test button
            self.test_button.config(state=tk.NORMAL)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    print("Starting GUI Thread Test...")
    print("This will test the installer in the same context as the real setup GUI.")
    
    gui = TestGUI()
    gui.run()

if __name__ == "__main__":
    main()
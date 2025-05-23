# minimal_setup_gui.py - Simplified setup that avoids crashes
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform
import logging
import os

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_minimal_setup_thread(progress_text, progress_bar, complete_var, status_var, root_window, 
                             download_ai_var, install_kokoro_var, install_xtts_var):
    """Run a minimal setup process that avoids crashes"""
    
    try:
        logger.info("Minimal setup thread started")
        status_var.set("running")
        
        # Step 1: Check what's already installed
        progress_text.set("Checking existing packages...")
        progress_bar["value"] = 10
        root_window.update()
        
        # Import the isolated installer
        from completely_isolated_installer import install_packages_isolated, install_kokoro_isolated
        
        # Step 2: Install basic packages if needed
        basic_packages = [
            "pdfplumber", "pdf2image", "pytesseract", "pyttsx3",
            "transformers", "torch", "torchvision", "torchaudio", "pygame"
        ]
        
        progress_text.set("Installing basic packages in isolated process...")
        progress_bar["value"] = 20
        root_window.update()
        
        logger.info("Starting isolated installation of basic packages")
        
        try:
            # Force UI update before starting
            progress_text.set("Starting package installation in isolated process...")
            root_window.update()
            
            # Add a small delay to ensure UI is updated
            import time
            time.sleep(0.5)
            
            # Call the installer with explicit error handling
            basic_results = install_packages_isolated(basic_packages, progress_text)
            
            # Force UI update after installation
            root_window.update()
            
            logger.info(f"Basic installation completed, results type: {type(basic_results)}")
            logger.info(f"Basic installation results: {basic_results}")
            
            # Check if results is None or empty
            if basic_results is None:
                logger.error("Basic installation returned None")
                progress_text.set("Installation failed: No results returned")
                status_var.set("failed")
                return
            
            if "error" in basic_results:
                logger.error(f"Basic package installation failed: {basic_results['error']}")
                progress_text.set(f"Basic installation failed: {basic_results['error']}")
                status_var.set("failed")
                return
            
            # Check if results is empty
            if not basic_results:
                logger.error("Basic installation returned empty results")
                progress_text.set("Installation failed: Empty results")
                status_var.set("failed")
                return
            
            # Check results
            failed_packages = []
            success_count = 0
            for package, result in basic_results.items():
                if result.get("success", False):
                    success_count += 1
                    logger.info(f"Package {package} installed successfully")
                else:
                    failed_packages.append(package)
                    logger.warning(f"Package {package} failed: {result}")
            
            if failed_packages:
                logger.warning(f"Some packages failed: {failed_packages}")
                progress_text.set(f"Warning: Failed packages: {', '.join(failed_packages[:3])}")
            else:
                progress_text.set("Basic packages installed successfully!")
                logger.info(f"All {success_count} basic packages installed successfully")
                
        except Exception as e:
            logger.error(f"Exception during basic package installation: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            progress_text.set(f"Installation error: {str(e)}")
            status_var.set("failed")
            return
        
        progress_bar["value"] = 50
        root_window.update()
        
        # Step 3: Install Kokoro if requested
        if install_kokoro_var.get():
            progress_text.set("Installing Kokoro TTS in isolated process...")
            progress_bar["value"] = 60
            root_window.update()
            
            logger.info("Starting isolated Kokoro installation")
            kokoro_results = install_kokoro_isolated()
            
            if "error" in kokoro_results:
                logger.error(f"Kokoro installation failed: {kokoro_results['error']}")
                progress_text.set(f"Kokoro installation failed but continuing...")
            else:
                # Check if all Kokoro packages installed
                kokoro_success = all(result.get("success", False) for result in kokoro_results.values())
                if kokoro_success:
                    progress_text.set("Kokoro TTS installed successfully!")
                else:
                    progress_text.set("Kokoro TTS installation had issues but continuing...")
        
        progress_bar["value"] = 80
        root_window.update()
        
        # Step 4: Skip system installations for now to avoid more crashes
        progress_text.set("Skipping system installations (Poppler/Tesseract) to avoid crashes...")
        
        # Step 5: Skip AI model to keep it simple
        progress_text.set("Skipping AI model download (can be done later)...")
        
        progress_bar["value"] = 100
        root_window.update()
        
        # Complete
        progress_text.set("Setup completed! Application should work with basic functionality.")
        status_var.set("completed")
        complete_var.set(True)
        
        # Enable continue button
        root_window.after(100, lambda: enable_continue_button(root_window))
        logger.info("Minimal setup completed successfully")
        
    except Exception as e:
        logger.error(f"Minimal setup thread crashed: {e}")
        progress_text.set(f"Setup failed: {e}")
        status_var.set("failed")
        root_window.update()

def enable_continue_button(root_window):
    """Enable the continue button"""
    try:
        for widget in root_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for button in widget.winfo_children():
                    if isinstance(button, tk.Button) and button.cget("text") == "Continue":
                        button.config(state=tk.NORMAL)
                        logger.info("Continue button enabled")
                        break
    except Exception as e:
        logger.error(f"Error enabling continue button: {e}")

def create_minimal_setup_gui():
    """Create a minimal setup GUI that avoids crashes"""
    
    # Create the setup window
    setup_window = tk.Tk()
    setup_window.title("Mailreader - Minimal Safe Setup")
    setup_window.geometry("550x400")
    
    # Center window
    setup_window.update_idletasks()
    width = setup_window.winfo_width()
    height = setup_window.winfo_height()
    x = (setup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (setup_window.winfo_screenheight() // 2) - (height // 2)
    setup_window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Variables
    complete_var = tk.BooleanVar(value=False)
    progress_text = tk.StringVar(value="Ready to start minimal setup...")
    status_var = tk.StringVar(value="pending")
    download_ai_var = tk.BooleanVar(value=False)  # Disabled for safety
    install_kokoro_var = tk.BooleanVar(value=False)  # User choice
    install_xtts_var = tk.BooleanVar(value=False)  # Disabled for safety
    
    # Title and description
    tk.Label(setup_window, text="Mailreader - Minimal Safe Setup", font=("Arial", 16, "bold")).pack(pady=10)
    
    tk.Label(setup_window, text="This minimal setup avoids crashes by using isolated processes.\n"
                               "All installations run separately to prevent application restarts.",
             wraplength=500).pack(pady=5)
    
    # Warning about enhanced features
    warning_frame = tk.LabelFrame(setup_window, text="Safe Installation Mode", fg="blue")
    warning_frame.pack(fill=tk.X, padx=20, pady=5)
    
    tk.Label(warning_frame, 
             text="This setup runs all package installations in separate processes to prevent crashes.\n"
                  "Some advanced features (Poppler, Tesseract, AI model) are skipped for stability.\n"
                  "The application will work with basic PDF reading and summarization.",
             wraplength=500, 
             justify=tk.LEFT, 
             font=("Arial", 9)).pack(padx=10, pady=5)
    
    # Enhanced TTS options frame
    tts_frame = tk.LabelFrame(setup_window, text="Voice Options")
    tts_frame.pack(fill=tk.X, padx=20, pady=5)
    
    # Kokoro TTS checkbox
    kokoro_checkbox = tk.Checkbutton(tts_frame, text="Install Kokoro TTS (High quality voice - isolated installation)", 
                                    variable=install_kokoro_var)
    kokoro_checkbox.pack(anchor=tk.W, padx=10, pady=2)
    
    # Progress bar and text
    progress_frame = tk.Frame(setup_window)
    progress_frame.pack(fill=tk.X, padx=20, pady=10)
    
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=510, mode="determinate")
    progress_bar.pack(fill=tk.X)
    
    progress_label = tk.Label(progress_frame, textvariable=progress_text, wraplength=500, justify="left")
    progress_label.pack(fill=tk.X, pady=5)
    
    # Buttons
    button_frame = tk.Frame(setup_window)
    button_frame.pack(side=tk.BOTTOM, pady=20)
    
    def start_minimal_setup():
        logger.info("Starting minimal setup process")
        start_button.config(state=tk.DISABLED)
        skip_button.config(state=tk.DISABLED)
        
        # Start setup in a separate thread
        setup_thread = threading.Thread(
            target=run_minimal_setup_thread, 
            args=(progress_text, progress_bar, complete_var, status_var, setup_window, 
                  download_ai_var, install_kokoro_var, install_xtts_var)
        )
        setup_thread.daemon = True
        setup_thread.start()
        
        # Check status periodically
        check_status()
    
    def check_status():
        status = status_var.get()
        
        if status == "completed":
            continue_button.config(state=tk.NORMAL)
            setup_window.update()
        elif status == "failed":
            start_button.config(text="Retry", state=tk.NORMAL)
            skip_button.config(state=tk.NORMAL)
            setup_window.update()
        elif status == "running":
            setup_window.after(100, check_status)
    
    def skip_setup():
        result = messagebox.askyesno("Skip Setup", 
                                    "Skip installation? The application may not work properly without dependencies.")
        if result:
            complete_var.set(False)
            setup_window.destroy()
    
    def continue_app():
        complete_var.set(True)
        setup_window.destroy()
    
    start_button = tk.Button(button_frame, text="Start Safe Setup", command=start_minimal_setup, width=15)
    start_button.pack(side=tk.LEFT, padx=5)
    
    skip_button = tk.Button(button_frame, text="Skip", command=skip_setup, width=12)
    skip_button.pack(side=tk.LEFT, padx=5)
    
    continue_button = tk.Button(button_frame, text="Continue", command=continue_app, width=12, state=tk.DISABLED)
    continue_button.pack(side=tk.LEFT, padx=5)
    
    return setup_window, complete_var

def run_setup():
    """Main setup function using minimal approach"""
    try:
        logger.info("Starting minimal Mailreader setup process")
        
        # Create and run the minimal setup GUI
        setup_window, complete_var = create_minimal_setup_gui()
        setup_window.mainloop()
        
        result = complete_var.get()
        logger.info(f"Minimal setup completed with result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Minimal setup failed: {e}")
        return False

if __name__ == "__main__":
    result = run_setup()
    print(f"Minimal setup completed: {result}")
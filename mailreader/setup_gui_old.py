# setup_gui.py - GUI interface separated from installation logic
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform
import logging

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enable_continue_button(root_window):
    """Enable the continue button - used as a separate function to ensure it runs in the main thread"""
    try:
        # Find the continue button
        for widget in root_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for button in widget.winfo_children():
                    if isinstance(button, tk.Button) and button.cget("text") == "Continue":
                        button.config(state=tk.NORMAL)
                        logger.info("Continue button enabled")
                        break
    except Exception as e:
        logger.error(f"Error enabling continue button: {e}")

def run_setup_thread(progress_text, progress_bar, complete_var, status_var, root_window, 
                     download_ai_var, install_kokoro_var, install_xtts_var):
    """Run the setup process in a separate thread"""
    from dependency_installers import (
        install_basic_packages, install_kokoro_safe, install_xtts_safe,
        install_poppler_windows, install_tesseract_windows, download_ai_model, is_admin
    )
    
    try:
        logger.info("Setup thread started")
        # Update status
        status_var.set("running")
        
        # List of required packages
        basic_packages = [
            "pdfplumber",
            "pdf2image", 
            "pytesseract",
            "pyttsx3",
            "transformers",
            "torch",
            "torchvision",
            "torchaudio",
            "pygame"
        ]
        
        current_step = 0
        total_steps = 5  # Simplified step counting
        
        # Step 1: Install basic packages
        logger.info("Installing basic packages")
        progress_text.set("Installing basic packages...")
        progress_bar["value"] = 10
        root_window.update()
        
        success, failed_packages = install_basic_packages(
            basic_packages, progress_text, progress_bar, root_window
        )
        
        if failed_packages:
            logger.warning(f"Some basic packages failed: {failed_packages}")
            progress_text.set(f"Warning: Failed to install: {', '.join(failed_packages[:3])}")
            root_window.update()
        
        current_step += 1
        progress_bar["value"] = 30
        root_window.update()
        
        # Step 2: Install enhanced TTS packages if selected
        if install_kokoro_var.get():
            logger.info("Installing Kokoro TTS")
            progress_text.set("Installing Kokoro TTS (experimental)...")
            root_window.update()
            
            try:
                success, error_msg = install_kokoro_safe(progress_text)
                if not success:
                    logger.error(f"Kokoro installation failed: {error_msg}")
                    progress_text.set(f"Kokoro installation failed: {error_msg[:50]}...")
                    root_window.update()
                    # Continue with setup instead of failing
            except Exception as e:
                logger.error(f"Kokoro installation crashed: {e}")
                progress_text.set(f"Kokoro installation failed with error")
                root_window.update()
        
        if install_xtts_var.get():
            logger.info("Installing XTTS")
            progress_text.set("Installing XTTS-v2 (experimental)...")
            root_window.update()
            
            try:
                success, error_msg = install_xtts_safe(progress_text)
                if not success:
                    logger.error(f"XTTS installation failed: {error_msg}")
                    progress_text.set(f"XTTS installation failed: {error_msg[:50]}...")
                    root_window.update()
            except Exception as e:
                logger.error(f"XTTS installation crashed: {e}")
                progress_text.set(f"XTTS installation failed with error")
                root_window.update()
        
        current_step += 1
        progress_bar["value"] = 50
        root_window.update()
        
        # Step 3: Platform-specific installations
        if platform.system() == "Windows":
            # Install Poppler
            progress_text.set("Checking Poppler...")
            root_window.update()
            
            import os
            poppler_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'Library', 'bin')
            
            if not os.path.exists(poppler_path):
                logger.info("Installing Poppler")
                if not install_poppler_windows(progress_text):
                    progress_text.set("Warning: Failed to install Poppler. Some features may not work.")
                    root_window.update()
            
            # Install Tesseract
            progress_text.set("Checking Tesseract OCR...")
            root_window.update()
            tesseract_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Tesseract-OCR')
            
            if not os.path.exists(tesseract_path):
                # Ask user if they want to install Tesseract
                install_tesseract = messagebox.askyesno("Tesseract OCR", 
                                     "Tesseract OCR is needed for processing image-based PDFs.\n\n"
                                     "Do you want to install it now?")
                root_window.update()
                
                if install_tesseract:
                    logger.info("Installing Tesseract")
                    if not install_tesseract_windows(progress_text):
                        progress_text.set("Warning: Failed to install Tesseract. OCR features may not work.")
                        root_window.update()
        else:
            # For non-Windows platforms
            progress_text.set("For Linux/macOS, please ensure you have Poppler and Tesseract installed via your package manager.")
            root_window.update()
        
        current_step += 1
        progress_bar["value"] = 80
        root_window.update()
        
        # Step 4: Download AI model if selected
        if download_ai_var.get():
            logger.info("Downloading AI model")
            download_ai_model(progress_text)
        else:
            progress_text.set("Skipping AI model download (will download on first use)")
        
        root_window.update()
        
        # Step 5: Complete
        progress_bar["value"] = 100
        root_window.update()
        
        # Setup completed successfully
        progress_text.set("Setup completed successfully! Click 'Continue' to start the application.")
        status_var.set("completed")
        complete_var.set(True)
        
        # Explicitly update the continue button state
        root_window.after(100, lambda: enable_continue_button(root_window))
        logger.info("Setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup thread crashed: {e}")
        progress_text.set(f"Error during setup: {e}")
        status_var.set("failed")
        root_window.update()

def create_setup_gui():
    """Create and return the setup GUI"""
    from dependency_installers import is_admin, is_ai_model_downloaded
    
    # Create the setup window
    setup_window = tk.Tk()
    setup_window.title("Mailreader Setup - Modular")
    setup_window.geometry("550x500")
    
    # Center window
    setup_window.update_idletasks()
    width = setup_window.winfo_width()
    height = setup_window.winfo_height()
    x = (setup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (setup_window.winfo_screenheight() // 2) - (height // 2)
    setup_window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Variables
    complete_var = tk.BooleanVar(value=False)
    progress_text = tk.StringVar(value="Ready to start setup...")
    status_var = tk.StringVar(value="pending")  # pending, running, completed, failed
    download_ai_var = tk.BooleanVar(value=False)
    install_kokoro_var = tk.BooleanVar(value=False)  # Keep false by default
    install_xtts_var = tk.BooleanVar(value=False)
    
    # Admin check
    if platform.system() == "Windows" and not is_admin():
        tk.messagebox.showwarning("Admin Required", 
                                "This setup may require administrator privileges for some features.\n"
                                "Consider closing and running the application as administrator.")
    
    # Title and description
    tk.Label(setup_window, text="Mailreader - Modular Setup", font=("Arial", 16, "bold")).pack(pady=10)
    
    tk.Label(setup_window, text="This will install dependencies for the Mailreader application with optional enhanced voices.",
             wraplength=500).pack(pady=5)
    
    # AI Model options frame
    ai_frame = tk.LabelFrame(setup_window, text="AI Options")
    ai_frame.pack(fill=tk.X, padx=20, pady=5)
    
    # Check if AI model is already downloaded
    ai_model_downloaded = is_ai_model_downloaded()
    ai_checkbox_text = "Download AI model for summarization"
    if ai_model_downloaded:
        ai_checkbox_text += " (already downloaded)"
    
    # AI model download checkbox
    ai_checkbox = tk.Checkbutton(ai_frame, text=ai_checkbox_text, 
                                variable=download_ai_var, 
                                state=tk.DISABLED if ai_model_downloaded else tk.NORMAL)
    ai_checkbox.pack(anchor=tk.W, padx=10, pady=2)
    
    # Enhanced TTS options frame
    tts_frame = tk.LabelFrame(setup_window, text="Enhanced Voice Options (Experimental)")
    tts_frame.pack(fill=tk.X, padx=20, pady=5)
    
    # Kokoro TTS checkbox
    kokoro_checkbox = tk.Checkbutton(tts_frame, text="Install Kokoro TTS (High quality voice - may fail)", 
                                    variable=install_kokoro_var)
    kokoro_checkbox.pack(anchor=tk.W, padx=10, pady=2)
    
    # XTTS checkbox
    xtts_checkbox = tk.Checkbutton(tts_frame, text="Install XTTS-v2 (Voice cloning, large download - may fail)", 
                                  variable=install_xtts_var)
    xtts_checkbox.pack(anchor=tk.W, padx=10, pady=2)
    
    # Add warning about enhanced voices
    tk.Label(tts_frame, 
             text="WARNING: Enhanced voices are experimental and may cause installation issues.\n"
                  "Leave unchecked for reliable installation with default system voice.\n"
                  "You can try enhanced voices after confirming the app works with default voice.",
             wraplength=500, 
             justify=tk.LEFT, 
             font=("Arial", 8),
             fg="red").pack(padx=10, pady=5)
    
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
    
    def start_setup():
        logger.info("Starting setup process")
        start_button.config(state=tk.DISABLED)
        skip_button.config(state=tk.DISABLED)
        
        # Start setup in a separate thread
        setup_thread = threading.Thread(
            target=run_setup_thread, 
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
            # Check again in 100ms
            setup_window.after(100, check_status)
    
    def skip_setup():
        result = messagebox.askyesno("Skip Setup", 
                                    "Skipping setup may cause the application to not function correctly "
                                    "if dependencies are missing.\n\nAre you sure you want to skip?")
        if result:
            complete_var.set(False)
            setup_window.destroy()
    
    def continue_app():
        complete_var.set(True)
        setup_window.destroy()
    
    start_button = tk.Button(button_frame, text="Start Setup", command=start_setup, width=12)
    start_button.pack(side=tk.LEFT, padx=5)
    
    skip_button = tk.Button(button_frame, text="Skip", command=skip_setup, width=12)
    skip_button.pack(side=tk.LEFT, padx=5)
    
    continue_button = tk.Button(button_frame, text="Continue", command=continue_app, width=12, state=tk.DISABLED)
    continue_button.pack(side=tk.LEFT, padx=5)
    
    return setup_window, complete_var
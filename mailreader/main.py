# main.py - With transformers blocking
import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox
import traceback
import json

# Preemptively block transformers module to prevent PyInstaller from looking for it
# This is a critical step to prevent the transformers import error
sys.modules['transformers'] = None

def setup_paths():
    """Set up paths for packaged executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = os.path.dirname(sys.executable)
        # Set current directory to the executable directory
        os.chdir(application_path)
        # Add executable directory to path
        if application_path not in sys.path:
            sys.path.insert(0, application_path)
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Create necessary directories
    os.makedirs(os.path.join(application_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(application_path, "output"), exist_ok=True)
    os.makedirs(os.path.join(application_path, "models"), exist_ok=True)
    os.makedirs(os.path.join(application_path, "config"), exist_ok=True)
    
    # Create a custom temp directory
    app_temp_dir = os.path.join(application_path, "output", "temp")
    os.makedirs(app_temp_dir, exist_ok=True)
    
    # Ensure config file exists
    config_file = os.path.join(application_path, "config", "app_config.json")
    if not os.path.exists(config_file):
        # Create a default config file
        default_config = {
            "first_run": False,
            "setup_complete": True,
            "tts_engine": "pyttsx3",
            "app_version": "1.0.0",
            "output_directory": "output",
            "temp_directory": "output/temp"
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    # Set environment variables for temp directory
    os.environ["TMPDIR"] = app_temp_dir
    os.environ["TEMP"] = app_temp_dir
    os.environ["TMP"] = app_temp_dir
    
    # Set model cache environment variable
    os.environ["TRANSFORMERS_CACHE"] = os.path.join(application_path, "models")
    
    return application_path

def setup_logging(app_path):
    """Set up logging configuration"""
    log_dir = os.path.join(app_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "application.log")
    
    # Create log file if it doesn't exist
    if not os.path.exists(log_path):
        try:
            with open(log_path, 'w') as f:
                f.write("# Mailreader application log\n")
        except:
            pass  # Proceed even if we can't create the log file
    
    try:
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add a console handler to also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
    except:
        # Fallback to console logging if file logging fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"An error occurred: {exc_value}")
    print("Please check the log file for more details.")

def check_first_run(app_path):
    """Check if this is the first run of the application"""
    config_file = os.path.join(app_path, "config", "app_config.json")
    
    if not os.path.exists(config_file):
        return True
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('first_run', True)
    except:
        return True

def mark_setup_complete(app_path):
    """Mark that setup has been completed"""
    config_file = os.path.join(app_path, "config", "app_config.json")
    
    # Create or update config file
    config = {'first_run': False, 'setup_complete': True}
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
                config.update(existing_config)
        
        config['first_run'] = False
        config['setup_complete'] = True
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logging.error(f"Error updating config file: {e}")

def main():
    """Main application entry point"""
    try:
        print("Starting Mailreader application...")
        
        # Set up sys.path and directories
        app_path = setup_paths()
        print(f"Application path: {app_path}")
        
        # Set up logging
        setup_logging(app_path)
        logging.info("Application starting")
        
        # Set up global exception handler
        sys.excepthook = handle_exception
        
        # Check if this is the first run
        if check_first_run(app_path):
            logging.info("First run detected, launching setup")
            
            # Import setup module
            try:
                from dependency_setup import run_setup
                
                # Run setup with GUI
                setup_completed = run_setup()
                
                if not setup_completed:
                    logging.error("Setup failed or was cancelled")
                    messagebox.showerror("Setup Failed", 
                                        "Setup was not completed. The application may not function correctly.\n"
                                        "Please run the application again to retry setup.")
                    return
                
                # Mark setup as complete
                mark_setup_complete(app_path)
                logging.info("Setup completed successfully")
            except Exception as setup_error:
                logging.error(f"Error during setup: {setup_error}")
                messagebox.showerror("Setup Error", 
                                    f"Error during setup: {setup_error}\n\n"
                                    "The application will try to continue, but some features may not work.")
        
        # Print information about loaded modules
        print(f"Python path: {sys.path}")
        
        # Import UI module with safe handling
        print("Importing UI module...")
        try:
            from ui import app
            print("UI module imported successfully")
        except ImportError as e:
            print(f"Error importing UI module: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error importing UI: {e}")
            traceback.print_exc()
            raise
        
        # Start the UI
        print("Starting UI...")
        app.mainloop()
        
    except Exception as e:
        error_message = f"Error starting application: {e}"
        logging.error(error_message, exc_info=True)
        traceback.print_exc()
        
        # Show error message
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"{error_message}\n\nTraceback: {traceback.format_exc()}\n\nPlease check the log file for details.")
            root.destroy()
        except Exception as dialog_error:
            print(f"Error showing dialog: {dialog_error}")
            print(f"Original error: {error_message}")

if __name__ == "__main__":
    main()
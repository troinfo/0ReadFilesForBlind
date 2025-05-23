# uninstall.py
import os
import sys
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import json

def get_app_path():
    """Get the application path"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_path = os.path.dirname(os.path.abspath(__file__))
    return app_path

def reset_first_run_flag():
    """Reset the first run flag in the config"""
    app_path = get_app_path()
    config_dir = os.path.join(app_path, "config")
    config_file = os.path.join(config_dir, "app_config.json")
    
    if os.path.exists(config_file):
        try:
            # Update the config file
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config['first_run'] = True
            config['setup_complete'] = False
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            return True
        except Exception as e:
            print(f"Error updating config file: {e}")
            return False
    else:
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Create a new config file
        config = {'first_run': True, 'setup_complete': False}
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        return True

def clean_directories():
    """Clean up output and logs directories"""
    app_path = get_app_path()
    dirs_to_clean = [
        os.path.join(app_path, "logs"),
        os.path.join(app_path, "output"),
        os.path.join(app_path, "models")
    ]
    
    cleaned = []
    
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            try:
                # Remove all files in the directory but keep the directory
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                cleaned.append(directory)
            except Exception as e:
                print(f"Error cleaning directory {directory}: {e}")
    
    return cleaned

def run_uninstall_gui():
    """Run the uninstall process with a GUI"""
    root = tk.Tk()
    root.title("Mailreader Uninstall/Reset")
    root.geometry("500x350")
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Variables
    status_text = tk.StringVar(value="Ready to reset the application.")
    
    # Title and description
    tk.Label(root, text="Mailreader - Reset/Uninstall", font=("Arial", 16, "bold")).pack(pady=10)
    
    tk.Label(root, text="This will reset the application to its initial state. You'll need to run setup again the next time you start the application.",
             wraplength=450).pack(pady=5)
    
    # Options frame
    options_frame = tk.LabelFrame(root, text="Reset Options")
    options_frame.pack(fill=tk.X, padx=20, pady=10)
    
    reset_first_run_var = tk.BooleanVar(value=True)
    reset_first_run_check = tk.Checkbutton(options_frame, text="Reset first-run flag (forces setup to run again)", variable=reset_first_run_var)
    reset_first_run_check.pack(anchor=tk.W, padx=10, pady=5)
    
    clean_dirs_var = tk.BooleanVar(value=True)
    clean_dirs_check = tk.Checkbutton(options_frame, text="Clean logs, output, and model directories", variable=clean_dirs_var)
    clean_dirs_check.pack(anchor=tk.W, padx=10, pady=5)
    
    # Status frame
    status_frame = tk.Frame(root)
    status_frame.pack(fill=tk.X, padx=20, pady=10)
    
    status_label = tk.Label(status_frame, textvariable=status_text, wraplength=450)
    status_label.pack(fill=tk.X, pady=5)
    
    # Button frame
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=20)
    
    def perform_reset():
        """Perform the reset operation"""
        reset_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.DISABLED)
        
        status_text.set("Resetting application...")
        root.update()
        
        if reset_first_run_var.get():
            if reset_first_run_flag():
                status_text.set(status_text.get() + "\nFirst-run flag reset successfully.")
            else:
                status_text.set(status_text.get() + "\nError resetting first-run flag.")
        
        if clean_dirs_var.get():
            cleaned = clean_directories()
            if cleaned:
                status_text.set(status_text.get() + f"\nCleaned directories: {', '.join([os.path.basename(d) for d in cleaned])}")
            else:
                status_text.set(status_text.get() + "\nNo directories were cleaned.")
        
        status_text.set(status_text.get() + "\n\nReset complete! You can now close this window.")
        reset_button.config(text="Close", command=root.destroy, state=tk.NORMAL)
    
    reset_button = tk.Button(button_frame, text="Reset Application", command=perform_reset, width=15)
    reset_button.pack(side=tk.LEFT, padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=root.destroy, width=15)
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    run_uninstall_gui()
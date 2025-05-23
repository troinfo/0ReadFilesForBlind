# ui.py - With safer imports for all modules
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import logging
import os
import sys

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Safe import function
def safe_import(module_name):
    """Safely import a module and return None if it fails"""
    try:
        return __import__(module_name)
    except ImportError as e:
        logging.error(f"Error importing {module_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error importing {module_name}: {e}")
        return None

# Safely import our modules
pdf_processor = safe_import("pdf_processor")
tts_handler = safe_import("tts_handler")
summarizer = safe_import("summarizer")

# Check if modules are available
pdf_processor_available = pdf_processor is not None
tts_handler_available = tts_handler is not None
summarizer_available = summarizer is not None

# Global variables to store states
current_text = ""
summarized_text = ""
current_file_path = ""

# Function to extract text from PDF safely
def extract_text_safely(pdf_path):
    """Extract text from PDF with error handling"""
    if not pdf_processor_available:
        return "(PDF processing is not available)"
    
    try:
        return pdf_processor.extract_text_from_pdf(pdf_path)
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return f"(Error extracting text: {str(e)})"

# Function to browse and process the PDF file
def browse_and_process_file():
    global current_text, summarized_text, current_file_path
    
    if not pdf_processor_available:
        messagebox.showerror("Module Missing", 
                           "PDF processor module is not available. The application cannot process PDF files.")
        return
    
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    
    current_file_path = file_path
    process_file_button.config(state=tk.NORMAL)
    
    try:
        # Show processing status
        status_label.config(text="Processing PDF file...")
        
        # Extract text in a separate thread to avoid freezing UI
        def process_in_thread():
            global current_text
            try:
                extracted_text = extract_text_safely(file_path)
                current_text = extracted_text
                summarized_text = ""  # Reset summary
                
                # Update UI in the main thread
                app.after(0, lambda: status_label.config(text=f"File loaded: {os.path.basename(file_path)}"))
            except Exception as e:
                app.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
                app.after(0, lambda: status_label.config(text="Error loading file"))
        
        threading.Thread(target=process_in_thread).start()
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.config(text="Error loading file")

# Function to process the current PDF based on user selection
def process_current_file():
    global current_text, summarized_text
    
    if not current_text:
        messagebox.showwarning("Warning", "Please load a PDF file first.")
        return
    
    # Clear the text area
    output_text.delete(1.0, tk.END)
    
    # Get selected action
    action = action_var.get()
    
    if action == "read_all":
        # Display and read full text
        output_text.insert(tk.END, current_text)
        
        if tts_handler_available:
            tts_handler.set_current_text(current_text)
            threading.Thread(target=tts_handler.read_aloud).start()
            status_label.config(text=f"Reading full text using {tts_handler.get_current_engine()}...")
        else:
            status_label.config(text="Text-to-speech not available")
        
    elif action == "summarize":
        # Generate and display summary
        if not summarizer_available:
            messagebox.showwarning("Feature Unavailable", 
                                 "The summarization feature is currently unavailable.")
            return
        
        try:
            if not summarized_text:  # Only summarize if not already done
                status_label.config(text="Generating summary...")
                
                # Do summarization in a thread to avoid freezing UI
                def summarize_in_thread():
                    global summarized_text
                    try:
                        summarized_text = summarizer.summarize_text(current_text)
                        
                        # Update UI in the main thread
                        app.after(0, lambda: output_text.insert(tk.END, summarized_text))
                        app.after(0, lambda: status_label.config(text="Summary generated"))
                    except Exception as e:
                        app.after(0, lambda: messagebox.showerror("Error", f"Error during summarization: {e}"))
                        app.after(0, lambda: status_label.config(text="Error generating summary"))
                
                threading.Thread(target=summarize_in_thread).start()
            else:
                # If we already have a summary, just display it
                output_text.insert(tk.END, summarized_text)
                status_label.config(text="Summary displayed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during summarization: {e}")
            return
            
    elif action == "summarize_and_read":
        # Generate, display and read summary
        if not summarizer_available:
            messagebox.showwarning("Feature Unavailable", 
                                 "The summarization feature is currently unavailable.")
            return
            
        if not tts_handler_available:
            messagebox.showwarning("Feature Unavailable",
                                 "The text-to-speech feature is currently unavailable.")
            return
            
        try:
            if not summarized_text:  # Only summarize if not already done
                status_label.config(text="Generating summary...")
                
                # Do summarization and reading in a thread
                def summarize_and_read_thread():
                    global summarized_text
                    try:
                        summarized_text = summarizer.summarize_text(current_text)
                        
                        # Update UI and start reading in the main thread
                        app.after(0, lambda: output_text.insert(tk.END, summarized_text))
                        app.after(0, lambda: tts_handler.set_current_text(summarized_text))
                        app.after(0, lambda: threading.Thread(target=tts_handler.read_aloud).start())
                        app.after(0, lambda: status_label.config(
                            text=f"Reading summary using {tts_handler.get_current_engine()}..."))
                    except Exception as e:
                        app.after(0, lambda: messagebox.showerror("Error", f"Error during summarization: {e}"))
                        app.after(0, lambda: status_label.config(text="Error generating summary"))
                
                threading.Thread(target=summarize_and_read_thread).start()
            else:
                # If we already have a summary, just display and read it
                output_text.insert(tk.END, summarized_text)
                tts_handler.set_current_text(summarized_text)
                threading.Thread(target=tts_handler.read_aloud).start()
                status_label.config(text=f"Reading summary using {tts_handler.get_current_engine()}...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during summarization: {e}")

# Function to change TTS engine
def change_tts_engine():
    if not tts_handler_available:
        messagebox.showwarning("Feature Unavailable",
                             "The text-to-speech feature is currently unavailable.")
        return
        
    selected_engine = voice_var.get()
    if tts_handler.set_tts_engine(selected_engine):
        status_label.config(text=f"Voice changed to: {tts_handler.AVAILABLE_ENGINES.get(selected_engine, selected_engine)}")
    else:
        messagebox.showerror("Error", f"Could not switch to {selected_engine}. Make sure required packages are installed.")

# Function to pause reading
def pause_reading():
    if tts_handler_available:
        tts_handler.pause_reading()
        status_label.config(text="Reading paused. Press 'F' to resume.")

# Function to resume reading
def resume_reading():
    if tts_handler_available:
        tts_handler.resume_reading()
        status_label.config(text="Reading resumed...")

# Function to stop reading
def stop_reading():
    if tts_handler_available:
        tts_handler.stop_reading()
        status_label.config(text="Reading stopped.")

# Create the UI
app = tk.Tk()
app.title("PDF Mail Reader - Enhanced")

# Create a frame for the top controls
top_frame = tk.Frame(app)
top_frame.pack(fill=tk.X, padx=10, pady=5)

# Add a button to browse for PDF files
browse_button = tk.Button(top_frame, text="Browse PDF", command=browse_and_process_file)
browse_button.pack(side=tk.LEFT, padx=5)

# Voice selection frame
voice_frame = tk.LabelFrame(app, text="Voice Selection")
voice_frame.pack(fill=tk.X, padx=10, pady=5)

# Get available engines and create radio buttons
available_engines = {"pyttsx3": "Default System Voice"}
if tts_handler_available:
    try:
        available_engines = tts_handler.get_available_engines()
    except Exception as e:
        logging.error(f"Error getting TTS engines: {e}")

voice_var = tk.StringVar(value="pyttsx3")

for engine_id, engine_name in available_engines.items():
    radio = tk.Radiobutton(voice_frame, text=engine_name, variable=voice_var, 
                          value=engine_id, command=change_tts_engine)
    radio.pack(anchor=tk.W, padx=5)

# Add note about high-quality voices
note_text = "Note: High-quality voices require additional packages to be installed during setup."
tk.Label(voice_frame, text=note_text, font=("Arial", 8), fg="gray").pack(padx=5, pady=2)

# Add radio buttons for action selection
action_var = tk.StringVar(value="read_all")
action_frame = tk.LabelFrame(app, text="Select Action")
action_frame.pack(fill=tk.X, padx=10, pady=5)

read_all_radio = tk.Radiobutton(action_frame, text="Read All Text", variable=action_var, value="read_all")
read_all_radio.pack(anchor=tk.W, padx=5)

# Add warning if summarizer is not available
if not summarizer_available:
    summarize_radio = tk.Radiobutton(action_frame, text="Summarize Only (Unavailable)", variable=action_var, value="summarize", state=tk.DISABLED)
    summarize_radio.pack(anchor=tk.W, padx=5)
    
    summarize_read_radio = tk.Radiobutton(action_frame, text="Summarize and Read (Unavailable)", variable=action_var, value="summarize_and_read", state=tk.DISABLED)
    summarize_read_radio.pack(anchor=tk.W, padx=5)
    
    # Add warning about summarization
    tk.Label(action_frame, text="Summarization features are temporarily unavailable", 
             font=("Arial", 8), fg="red").pack(padx=5, pady=2)
else:
    summarize_radio = tk.Radiobutton(action_frame, text="Summarize Only", variable=action_var, value="summarize")
    summarize_radio.pack(anchor=tk.W, padx=5)
    
    summarize_read_radio = tk.Radiobutton(action_frame, text="Summarize and Read", variable=action_var, value="summarize_and_read")
    summarize_read_radio.pack(anchor=tk.W, padx=5)

# Add a button to process the current file
process_file_button = tk.Button(action_frame, text="Process File", command=process_current_file, state=tk.DISABLED)
process_file_button.pack(pady=5)

# Create a frame for the playback controls
control_frame = tk.Frame(app)
control_frame.pack(fill=tk.X, padx=10, pady=5)

# Add Pause, Resume, and Stop buttons
pause_button = tk.Button(control_frame, text="Pause (J)", command=pause_reading)
pause_button.pack(side=tk.LEFT, padx=5)

resume_button = tk.Button(control_frame, text="Resume (F)", command=resume_reading)
resume_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(control_frame, text="Stop", command=stop_reading)
stop_button.pack(side=tk.LEFT, padx=5)

# Add a status label
status_label = tk.Label(app, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Add a text widget to display the extracted text
text_frame = tk.Frame(app)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

output_text = tk.Text(text_frame, height=20, width=60, wrap="word")
scrollbar = tk.Scrollbar(text_frame)

output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_text.yview)

# Bind keyboard shortcuts
def on_key_press(event):
    if event.keysym.lower() == 'j':  # Check if 'J' key is pressed
        pause_reading()
        return "break"  # Prevent default behavior
    elif event.keysym.lower() == 'f':  # Check if 'F' key is pressed
        resume_reading()
        return "break"  # Prevent default behavior

app.bind("<KeyPress>", on_key_press)

# Configure the app window
app.geometry("700x600")  # Made larger to accommodate new controls
app.focus_set()  # Set focus to the app window

# Show missing module warnings at startup if needed
if not pdf_processor_available:
    messagebox.showwarning("Module Missing", 
                         "PDF processor module is not available or has limited functionality.\n"
                         "Some PDF processing features may not work correctly.")

if not tts_handler_available:
    messagebox.showwarning("Module Missing",
                         "Text-to-speech module is not available.\n"
                         "Reading features will not work.")

if not summarizer_available:
    messagebox.showwarning("Module Missing",
                         "Summarizer module is not available.\n"
                         "Summarization features will not work.")
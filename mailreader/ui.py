# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pdf_processor import extract_text_from_pdf
import tts_handler

# Function to browse and process the PDF file
def browse_and_process_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    try:
        text = extract_text_from_pdf(file_path)
        tts_handler.set_current_text(text)

        # Display extracted text
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, text)

        # Prompt user to read aloud
        if messagebox.askyesno("Read Aloud", "Would you like to hear the text read aloud?"):
            threading.Thread(target=tts_handler.read_aloud, args=(0,)).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to pause reading using the 'J' key
def pause_reading():
    tts_handler.pause_reading()
    messagebox.showinfo("Paused", "Your audio has been paused. Press 'F' to resume.")

# Create the UI
app = tk.Tk()
app.title("PDF Mail Reader")

# Add a button to process PDF files
browse_button = tk.Button(app, text="Browse PDF", command=browse_and_process_file)
browse_button.pack(pady=10)

# Add a Pause button (formerly Stop button)
pause_button = tk.Button(app, text="Pause Reading", command=pause_reading)
pause_button.pack(pady=10)

# Add a text widget to display the extracted text
output_text = tk.Text(app, height=20, width=60, wrap="word")
output_text.pack(pady=10)

# Bind the 'J' key to pause reading and the 'F' key to resume reading
def on_key_press(event):
    if event.keysym.lower() == 'j':  # Check if 'J' key is pressed
        pause_reading()
        return "break"  # Prevent default behavior
    elif event.keysym.lower() == 'f':  # Check if 'F' key is pressed
        tts_handler.resume_reading()
        return "break"  # Prevent default behavior

app.bind("<KeyPress>", on_key_press)

# Configure the app window
app.geometry("500x400")
app.focus_set()  # Set focus to the app window
app.mainloop()

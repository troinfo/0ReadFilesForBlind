import pyttsx3
import threading
import logging

# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Logging setup
from config import LOG_FILE
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Variables to track TTS state
current_text = ""
audio_playing_thread = None
reading_paused = False

def set_current_text(text):
    global current_text
    current_text = text

# Update read_aloud to accept optional arguments
def read_aloud(event=None):
    global current_text, audio_playing_thread, reading_paused
    reading_paused = False

    # Function to handle reading aloud in a separate thread
    def play_text():
        if current_text.strip():
            try:
                tts_engine.say(current_text)
                tts_engine.runAndWait()
            except Exception as e:
                logging.error(f"Error during TTS: {e}")
                print(f"An error occurred during TTS: {e}")

    # Start reading aloud in a new thread to keep the UI responsive
    audio_playing_thread = threading.Thread(target=play_text)
    audio_playing_thread.start()

def pause_reading():
    tts_engine.stop()
    global reading_paused
    reading_paused = True
    logging.info("Playback paused.")

def resume_reading():
    global reading_paused
    if reading_paused and current_text:
        logging.info("Resuming playback.")
        read_aloud()

def stop_reading():
    tts_engine.stop()
    logging.info("Playback stopped.")

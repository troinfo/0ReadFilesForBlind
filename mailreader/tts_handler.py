# tts_handler.py - Fixed version with improved temp folder handling
import pyttsx3
import pygame
import os
import tempfile
import threading
import logging
import time
import re
import shutil

# Initialize pygame mixer
pygame.mixer.init()

# Initialize the traditional TTS engine as fallback
pyttsx3_engine = pyttsx3.init()

# Logging setup
from config import LOG_FILE, DEFAULT_OUTPUT_PATH
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Variables to track TTS state
current_text = ""
is_playing = False
is_paused = False
is_converting = False
current_chunk = 0
text_chunks = []
stop_requested = False
current_engine = "pyttsx3"  # Default engine

# Setup custom temp directory if needed
def setup_temp_directory():
    """Set up and verify the temporary directory for audio files"""
    try:
        # First try the system temp directory
        system_temp = tempfile.gettempdir()
        if os.path.exists(system_temp) and os.access(system_temp, os.W_OK):
            temp_dir = system_temp
            logging.info(f"Using system temp directory: {temp_dir}")
        else:
            # Fallback to our app's output directory for temp files
            app_temp_dir = os.path.join(DEFAULT_OUTPUT_PATH, "temp")
            os.makedirs(app_temp_dir, exist_ok=True)
            temp_dir = app_temp_dir
            logging.info(f"Created custom temp directory: {temp_dir}")
        
        # Create a test file to verify we can write
        test_file = os.path.join(temp_dir, "mailreader_test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logging.info("Temp directory write test successful")
        
        return os.path.join(temp_dir, "mailreader_temp")
    except Exception as e:
        # Last resort: use the current directory
        logging.error(f"Error setting up temp directory: {e}, falling back to current directory")
        fallback_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(fallback_dir, exist_ok=True)
        return os.path.join(fallback_dir, "mailreader_temp")

# Set up the temp directory path
temp_audio_file_prefix = setup_temp_directory()
logging.info(f"Using temp audio file prefix: {temp_audio_file_prefix}")

# Available TTS engines
AVAILABLE_ENGINES = {
    "pyttsx3": "Default System Voice",
    "kokoro": "Kokoro TTS (High Quality)",
    "xtts": "XTTS-v2 (Voice Cloning)"
}

def get_available_engines():
    """Get list of available TTS engines based on installed packages"""
    available = {"pyttsx3": "Default System Voice"}
    
    try:
        import kokoro
        available["kokoro"] = "Kokoro TTS (High Quality)"
    except ImportError:
        pass
    
    try:
        from TTS.api import TTS
        available["xtts"] = "XTTS-v2 (Voice Cloning)"
    except ImportError:
        pass
    
    return available

def set_tts_engine(engine_name):
    """Set the TTS engine to use"""
    global current_engine
    available = get_available_engines()
    
    if engine_name in available:
        current_engine = engine_name
        logging.info(f"TTS engine set to: {engine_name}")
        return True
    else:
        logging.warning(f"TTS engine {engine_name} not available")
        return False

def get_current_engine():
    """Get the currently selected TTS engine"""
    return current_engine

def set_current_text(text):
    """Set the current text to be read aloud and chunk it into manageable pieces"""
    global current_text, text_chunks, current_chunk
    current_text = text
    current_chunk = 0
    
    # Split text into manageable chunks (adjust size based on engine)
    chunk_size = 800 if current_engine == "kokoro" else 1000
    text_chunks = chunk_text(text, chunk_size)
    
    logging.info(f"Text set with {len(text)} characters, divided into {len(text_chunks)} chunks for {current_engine}")

def chunk_text(text, chunk_size=1000):
    """Split text into manageable chunks for better TTS handling"""
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        end_pos = min(current_pos + chunk_size, len(text))
        
        if end_pos < len(text):
            sentence_end = max(
                text.rfind('. ', current_pos, end_pos),
                text.rfind('! ', current_pos, end_pos),
                text.rfind('? ', current_pos, end_pos),
                text.rfind('.\n', current_pos, end_pos),
                text.rfind('!\n', current_pos, end_pos),
                text.rfind('?\n', current_pos, end_pos)
            )
            
            if sentence_end != -1:
                end_pos = sentence_end + 2
            else:
                space_pos = text.rfind(' ', current_pos, end_pos)
                if space_pos != -1:
                    end_pos = space_pos + 1
        
        chunks.append(text[current_pos:end_pos].strip())
        current_pos = end_pos
    
    return chunks

def convert_text_to_speech_pyttsx3(text, output_file):
    """Convert text to speech using pyttsx3"""
    global is_converting
    
    try:
        is_converting = True
        logging.info(f"Converting text chunk ({len(text)} chars) to speech using pyttsx3...")
        
        # Ensure the directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        pyttsx3_engine.save_to_file(text, output_file)
        pyttsx3_engine.runAndWait()
        
        # Verify the file was created
        if not os.path.exists(output_file):
            logging.error(f"pyttsx3 failed to create output file: {output_file}")
            return False
            
        logging.info(f"Text converted and saved to {output_file}")
        is_converting = False
        return True
    except Exception as e:
        logging.error(f"Error converting text to speech with pyttsx3: {e}")
        is_converting = False
        return False

def convert_text_to_speech_kokoro(text, output_file):
    """Convert text to speech using Kokoro TTS"""
    global is_converting
    
    try:
        is_converting = True
        logging.info(f"Converting text chunk ({len(text)} chars) to speech using Kokoro...")
        
        # Ensure the directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Import Kokoro
        from kokoro import KPipeline
        import soundfile as sf
        
        # Initialize Kokoro pipeline with default voice
        pipeline = KPipeline(lang_code='a')  # 'a' for American English
        
        # Generate audio
        audio_data = pipeline(text)
        
        # Save to file
        sf.write(output_file, audio_data, 24000)
        
        # Verify the file was created
        if not os.path.exists(output_file):
            logging.error(f"Kokoro failed to create output file: {output_file}")
            return False
            
        logging.info(f"Text converted and saved to {output_file}")
        is_converting = False
        return True
    except Exception as e:
        logging.error(f"Error converting text to speech with Kokoro: {e}")
        is_converting = False
        return False

def convert_text_to_speech_xtts(text, output_file):
    """Convert text to speech using XTTS-v2"""
    global is_converting
    
    try:
        is_converting = True
        logging.info(f"Converting text chunk ({len(text)} chars) to speech using XTTS...")
        
        # Ensure the directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Import TTS
        from TTS.api import TTS
        
        # Initialize XTTS model (this might take time on first run)
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        
        # Generate speech using default English voice
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker="Ana Florence",  # Built-in speaker
            language="en"
        )
        
        # Verify the file was created
        if not os.path.exists(output_file):
            logging.error(f"XTTS failed to create output file: {output_file}")
            return False
            
        logging.info(f"Text converted and saved to {output_file}")
        is_converting = False
        return True
    except Exception as e:
        logging.error(f"Error converting text to speech with XTTS: {e}")
        is_converting = False
        return False

def convert_text_to_speech(text, output_file):
    """Convert text to speech using the selected engine"""
    if current_engine == "kokoro":
        return convert_text_to_speech_kokoro(text, output_file)
    elif current_engine == "xtts":
        return convert_text_to_speech_xtts(text, output_file)
    else:
        return convert_text_to_speech_pyttsx3(text, output_file)

def read_aloud(event=None):
    """Read the current text aloud from the beginning"""
    global current_chunk, is_playing, is_paused, stop_requested
    
    if not text_chunks:
        logging.warning("No text to read")
        return
    
    # If already playing, stop first
    if is_playing:
        stop_reading()
        time.sleep(0.2)
    
    # Reset state
    current_chunk = 0
    is_paused = False
    is_playing = True
    stop_requested = False
    
    # Start playback in a separate thread
    threading.Thread(target=play_all_chunks, daemon=True).start()

def play_all_chunks():
    """Play all text chunks in sequence"""
    global current_chunk, is_playing, is_paused, stop_requested
    
    while current_chunk < len(text_chunks) and not stop_requested:
        if not is_paused:
            chunk_file = f"{temp_audio_file_prefix}_{current_chunk}.wav"
            
            # Convert current chunk to speech
            if convert_text_to_speech(text_chunks[current_chunk], chunk_file):
                try:
                    # Load and play the audio file
                    pygame.mixer.music.load(chunk_file)
                    pygame.mixer.music.play()
                    
                    logging.info(f"Playing chunk {current_chunk+1}/{len(text_chunks)} using {current_engine}")
                    
                    # Wait for playback to finish or be paused
                    while pygame.mixer.music.get_busy() and not stop_requested:
                        time.sleep(0.1)
                        
                        if is_paused:
                            time.sleep(0.1)
                            continue
                    
                    # Clean up the temporary file
                    try:
                        os.remove(chunk_file)
                    except Exception as e:
                        logging.error(f"Error removing temporary file: {e}")
                    
                    # Move to the next chunk if not stopped
                    if not stop_requested and not is_paused:
                        current_chunk += 1
                    
                except Exception as e:
                    logging.error(f"Error playing audio chunk: {e}")
                    current_chunk += 1
            else:
                current_chunk += 1
        else:
            time.sleep(0.1)
    
    # Mark as not playing when done with all chunks
    if not is_paused:
        is_playing = False
        logging.info("Playback finished")

def pause_reading():
    """Pause the current reading"""
    global is_paused
    
    if is_playing and not is_paused:
        try:
            pygame.mixer.music.pause()
            is_paused = True
            logging.info(f"Playback paused at chunk {current_chunk+1}/{len(text_chunks)}")
        except Exception as e:
            logging.error(f"Error pausing playback: {e}")

def resume_reading():
    """Resume reading from where it was paused"""
    global is_paused
    
    if is_playing and is_paused:
        try:
            pygame.mixer.music.unpause()
            is_paused = False
            logging.info(f"Playback resumed at chunk {current_chunk+1}/{len(text_chunks)}")
        except Exception as e:
            logging.error(f"Error resuming playback: {e}")

def stop_reading():
    """Stop reading completely"""
    global is_playing, is_paused, stop_requested
    
    stop_requested = True
    
    if is_playing:
        try:
            pygame.mixer.music.stop()
            is_playing = False
            is_paused = False
            logging.info("Playback stopped")
        except Exception as e:
            logging.error(f"Error stopping playback: {e}")
    
    cleanup_temp_files()

def cleanup_temp_files():
    """Clean up temporary audio files"""
    try:
        # Get the directory from the temp_audio_file_prefix
        temp_dir = os.path.dirname(temp_audio_file_prefix)
        prefix_name = os.path.basename(temp_audio_file_prefix)
        
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                if filename.startswith(prefix_name) and filename.endswith(".wav"):
                    try:
                        os.remove(os.path.join(temp_dir, filename))
                    except Exception as e:
                        logging.error(f"Error removing temp file {filename}: {e}")
        else:
            logging.warning(f"Temp directory does not exist: {temp_dir}")
    except Exception as e:
        logging.error(f"Error cleaning up temporary files: {e}")

def cleanup():
    """Clean up resources when the application exits"""
    stop_reading()
    cleanup_temp_files()
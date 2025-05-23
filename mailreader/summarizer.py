# summarizer.py - Works with either real or mock transformers
import logging
import os
import sys
import traceback

# Set up basic logging to console first
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Global variables
DEFAULT_SUMMARY_LENGTH = {"max_length": 100, "min_length": 50}
summarizer_pipeline = None

# Try to import config only when needed
def get_config():
    """Get configuration values safely"""
    try:
        from config import DEFAULT_SUMMARY_LENGTH as config_summary_length
        from config import LOG_FILE
        
        # Setup file logging if we have a valid log file
        if LOG_FILE and os.path.isdir(os.path.dirname(LOG_FILE)):
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(file_handler)
            
        return config_summary_length, LOG_FILE
    except Exception as e:
        logging.warning(f"Error importing config: {e}, using defaults")
        return DEFAULT_SUMMARY_LENGTH, None

# Initialize text-to-speech engine
def init_tts():
    """Initialize text-to-speech - separated to prevent import errors"""
    try:
        import pyttsx3
        return pyttsx3.init()
    except ImportError:
        logging.warning("pyttsx3 not available for TTS")
        return None
    except Exception as e:
        logging.error(f"Error initializing TTS: {e}")
        return None

def simple_summarize(text, max_length=100):
    """A simple fallback summarizer that doesn't use transformers"""
    logging.info("Using simple fallback summarizer")
    
    # Clean the text
    text = " ".join(text.split())
    
    # Get the first few sentences as a simple summary
    sentences = text.split('. ')
    
    # Limit to first 3-5 sentences or to max_length characters
    summary_sentences = []
    current_length = 0
    
    for sentence in sentences[:10]:  # Look at first 10 sentences
        if current_length + len(sentence) <= max_length:
            summary_sentences.append(sentence)
            current_length += len(sentence) + 2  # +2 for period and space
        else:
            break
    
    if not summary_sentences:
        # If no sentences fit, just truncate the text
        return text[:max_length] + "..."
    
    # Join the summary sentences
    summary = '. '.join(summary_sentences)
    if not summary.endswith('.'):
        summary += '.'
    
    return summary + " (Simple summary mode)"

def initialize_summarizer():
    """Initialize summarization pipeline - works with either real or mock transformers"""
    global summarizer_pipeline
    
    if summarizer_pipeline is not None:
        return summarizer_pipeline
        
    try:
        logging.info("Initializing summarization pipeline")
        
        # Try to import transformers (either real or mock)
        import transformers
        
        # Try to create the pipeline
        summarizer_pipeline = transformers.pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        
        logging.info("Summarization pipeline initialized successfully")
        return summarizer_pipeline
    except ImportError as e:
        logging.warning(f"Transformers not available: {e}")
        return None
    except Exception as e:
        logging.error(f"Error initializing summarizer: {e}")
        traceback.print_exc()
        return None

def summarize_text(text, max_length=None, min_length=None):
    """
    Summarizes the input text, using transformers if available or fallback if not.
    """
    if not text or not text.strip():
        raise ValueError("Input text is empty or invalid.")
    
    # Get config settings
    config_summary_length, _ = get_config()
    
    # Use default values if not provided
    max_length = max_length or config_summary_length["max_length"]
    min_length = min_length or config_summary_length["min_length"]
    
    # Clean and prepare the text
    processed_text = " ".join(text.split())
    
    # Try to initialize and use the transformers pipeline
    pipeline = initialize_summarizer()
    
    if pipeline:
        try:
            logging.info("Using transformers pipeline for summarization")
            summary = pipeline(processed_text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]["summary_text"]
        except Exception as e:
            logging.error(f"Error using transformers pipeline: {e}")
            logging.info("Falling back to simple summarizer")
    else:
        logging.info("No transformers pipeline available, using simple summarizer")
    
    # Fall back to simple summarization
    return simple_summarize(processed_text, max_length=max_length)

def read_aloud(text):
    """Reads text aloud using TTS."""
    tts_engine = init_tts()
    if not tts_engine:
        logging.error("TTS engine not available")
        return
        
    try:
        logging.info("Reading text aloud")
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        logging.error(f"Error during TTS: {e}")
        traceback.print_exc()

# Initialize logging but don't try to load transformers at module import time
logging.info("Summarizer module loaded with safe imports")
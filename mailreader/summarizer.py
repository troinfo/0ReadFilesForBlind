from transformers import pipeline
from config import DEFAULT_SUMMARY_LENGTH, LOG_FILE
import logging
import pyttsx3

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Initialize summarization model
summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", device=0)

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

def preprocess_text(text):
    """
    Preprocesses the input text to clean and truncate it for summarization.

    Args:
        text (str): Input text to preprocess.

    Returns:
        str: Preprocessed text.
    """
    # Remove extra spaces and control characters
    text = " ".join(text.split())
    
    # Truncate text to fit model input limits (e.g., 1024 tokens for most models)
    max_length = 1024  # Adjust based on the model's maximum input size
    return text[:max_length]

def split_text(text, chunk_size=512):
    """
    Splits text into manageable chunks for summarization.

    Args:
        text (str): Input text to split.
        chunk_size (int): Maximum size of each chunk.

    Returns:
        list: List of text chunks.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_text(text, max_length=None, min_length=None):
    """
    Summarizes the input text.

    Args:
        text (str): The text to summarize.
        max_length (int): Maximum length of the summary (optional).
        min_length (int): Minimum length of the summary (optional).

    Returns:
        str: The summarized text.
    """
    if not text.strip():
        raise ValueError("Input text is empty or invalid.")
    
    try:
        max_length = max_length or DEFAULT_SUMMARY_LENGTH["max_length"]
        min_length = min_length or DEFAULT_SUMMARY_LENGTH["min_length"]

        logging.info("Summarizing text.")
        text = preprocess_text(text)

        if len(text) > 1024:  # If text exceeds model input limit
            summaries = []
            for chunk in split_text(text):
                summary = summarizer_pipeline(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                summaries.append(summary[0]["summary_text"])
            return " ".join(summaries)
        else:
            summary = summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]["summary_text"]
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        raise

def read_aloud(text):
    """
    Reads text aloud using TTS.

    Args:
        text (str): Text to read aloud.
    """
    try:
        logging.info("Reading text aloud.")
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        logging.error(f"Error during TTS: {e}")
        raise

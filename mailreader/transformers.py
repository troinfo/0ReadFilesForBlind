# transformers.py - Mock module to satisfy PyInstaller
"""
Mock transformers module that provides empty implementations of key functionalities.
This allows the application to run without the real transformers library.
"""
import logging

logging.info("Using mock transformers module")

class Pipeline:
    """Mock Pipeline class"""
    def __init__(self, task=None, model=None, **kwargs):
        self.task = task
        self.model = model
        logging.info(f"Created mock Pipeline for task: {task}, model: {model}")
    
    def __call__(self, text, max_length=100, min_length=30, **kwargs):
        """Mock summarization that returns a simple extract"""
        logging.info("Using mock Pipeline for summarization")
        
        # Simple extractive summary (first few sentences)
        if isinstance(text, str):
            sentences = text.split('. ')
            summary = '. '.join(sentences[:3]) + '.'
            return [{"summary_text": summary + " (Mock summary)"}]
        
        # Handle list input
        results = []
        for t in text:
            sentences = t.split('. ')
            summary = '. '.join(sentences[:3]) + '.'
            results.append({"summary_text": summary + " (Mock summary)"})
        return results

def pipeline(task=None, model=None, **kwargs):
    """Mock pipeline factory function"""
    logging.info(f"Creating mock pipeline for {task} using {model}")
    return Pipeline(task=task, model=model, **kwargs)

# Mock key modules that might be imported
class AutoModelForSeq2SeqLM:
    """Mock model class"""
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        logging.info(f"Mock: Loading model {model_name}")
        return cls()

class AutoTokenizer:
    """Mock tokenizer class"""
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        logging.info(f"Mock: Loading tokenizer {model_name}")
        return cls()

# Create mock models module to satisfy imports like "from transformers import models"
class models:
    """Mock models module"""
    class bart:
        """Mock bart module"""
        class modeling_bart:
            """Mock modeling_bart module"""
            class BartForConditionalGeneration:
                """Mock BartForConditionalGeneration class"""
                @classmethod
                def from_pretrained(cls, model_name, **kwargs):
                    return cls()
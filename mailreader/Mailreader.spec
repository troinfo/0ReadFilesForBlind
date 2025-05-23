# Updated mailreader.spec File for PyInstaller
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Initialize base collections
datas = []
binaries = []
hiddenimports = []

# ================== Mock Transformers Module ==================
# Create a mock transformers.py file if it doesn't exist
# This allows the app to run without the real transformers library
mock_transformers_content = """
# transformers.py - Mock module to satisfy PyInstaller
import logging
logging.info("Using mock transformers module")

class Pipeline:
    def __init__(self, task=None, model=None, **kwargs):
        self.task = task
        self.model = model
    
    def __call__(self, text, max_length=100, min_length=30, **kwargs):
        # Simple extractive summary (first few sentences)
        if isinstance(text, str):
            sentences = text.split('. ')
            summary = '. '.join(sentences[:3]) + '.'
            return [{"summary_text": summary + " (Mock summary)"}]
        results = []
        for t in text:
            sentences = t.split('. ')
            summary = '. '.join(sentences[:3]) + '.'
            results.append({"summary_text": summary + " (Mock summary)"})
        return results

def pipeline(task=None, model=None, **kwargs):
    return Pipeline(task=task, model=model, **kwargs)

# Mock modules that might be imported
class AutoModelForSeq2SeqLM:
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        return cls()

class AutoTokenizer:
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        return cls()

class models:
    class bart:
        class modeling_bart:
            class BartForConditionalGeneration:
                @classmethod
                def from_pretrained(cls, model_name, **kwargs):
                    return cls()
"""

# Write the mock transformers file
with open('transformers.py', 'w') as f:
    f.write(mock_transformers_content)
print("Created mock transformers.py file")

# ================== Package Configuration ==================
# Add only core transformers dependencies, avoiding the heavy models
hiddenimports += [
    'tokenizers',
    'numpy',
    'torch.nn',
    'torch.nn.functional'
]

# Add PDF processing dependencies with submodules
hiddenimports += [
    'pdfplumber',
    'pdfminer.six',
    'pdfminer.pdfdocument',
    'pdfminer.pdfparser', 
    'pdfminer.pdftypes',
    'pdf2image',
    'PIL'
]

# Try to include pytesseract but don't fail if it's not available
try:
    import pytesseract
    hiddenimports.append('pytesseract')
    print("pytesseract module found and included")
except ImportError:
    print("pytesseract module not found - OCR capabilities will be disabled")

# Add audio/voice dependencies
hiddenimports += [
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'win32com.client',
    'comtypes'
]

# Add pygame with submodules
hiddenimports += [
    'pygame',
    'pygame.base',
    'pygame.constants',
    'pygame.mixer',
    'pygame.mixer_music',
    'pygame.font',
    'pygame.time'
]

# Add core Python modules
hiddenimports += [
    'tkinter',
    'threading',
    'json',
    'logging',
    'concurrent.futures'
]

# ================== Data Files Configuration ==================
# Use collect_all for key modules
for module in ['pdfplumber', 'PIL', 'pyttsx3', 'pygame']:
    try:
        module_datas, module_binaries, module_hiddenimports = collect_all(module)
        datas.extend(module_datas)
        binaries.extend(module_binaries)
        hiddenimports.extend(module_hiddenimports)
        print(f"Collected resources for {module}")
    except Exception as e:
        print(f"Error collecting {module}: {e}")

# Add application files
app_files = [
    ('config.py', '.'),
    ('ui.py', '.'),
    ('pdf_processor.py', '.'),
    ('summarizer.py', '.'),
    ('tts_handler.py', '.'),
    ('dependency_setup.py', '.'),
    ('transformers.py', '.')  # Include our mock transformers module
]
datas += app_files
print("Added application files to bundle")

# ================== Directory Structure ==================
# Create runtime directories directly in the bundle
runtime_dirs = [
    ('logs', 'logs'),
    ('output', 'output'),
    ('models', 'models'),
    ('config', 'config')
]

# Add runtime directories as datas
for src, dest in runtime_dirs:
    os.makedirs(src, exist_ok=True)
    datas.append((src, dest))

# Ensure config file exists
config_dir = 'config'
config_file = os.path.join(config_dir, 'app_config.json')
if not os.path.exists(config_file):
    os.makedirs(config_dir, exist_ok=True)
    with open(config_file, 'w') as f:
        f.write('{"first_run": false, "setup_complete": true, "tts_engine": "pyttsx3"}')
    print(f"Created default config file: {config_file}")

# Create temp directory
temp_dir = os.path.join('output', 'temp')
os.makedirs(temp_dir, exist_ok=True)
print(f"Created temp directory: {temp_dir}")

# ================== Executable Configuration ==================
icon_file = 'app_icon.ico' if os.path.exists('app_icon.ico') else None
manifest = 'mailreader.manifest'

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Mailreader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True for debugging - change back to False later
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    manifest=manifest,
)
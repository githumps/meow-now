"""
Configuration settings for Meow-Now application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Flask Configuration
FLASK_APP = os.getenv("FLASK_APP", "app.py")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# AGI Server Configuration
AGI_HOST = os.getenv("AGI_HOST", "0.0.0.0")
AGI_PORT = int(os.getenv("AGI_PORT", 4573))

# Asterisk Configuration
ASTERISK_HOST = os.getenv("ASTERISK_HOST", "localhost")
ASTERISK_AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", 5038))
ASTERISK_AMI_USERNAME = os.getenv("ASTERISK_AMI_USERNAME", "admin")
ASTERISK_AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "")

# Audio Configuration
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 8000))
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "wav")
MAX_RECORDING_DURATION = int(os.getenv("MAX_RECORDING_DURATION", 60))
CAT_MONOLOGUE_DURATION = int(os.getenv("CAT_MONOLOGUE_DURATION", 15))

# Audio paths
PROMPTS_DIR = AUDIO_DIR / "prompts"
CATS_DIR = AUDIO_DIR / "cats"
RECORDINGS_DIR = AUDIO_DIR / "recordings"
GENERATED_DIR = AUDIO_DIR / "generated"

# Ensure directories exist
for directory in [PROMPTS_DIR, CATS_DIR, RECORDINGS_DIR, GENERATED_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# TTS Engine Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "piper")
PIPER_MODEL_PATH = Path(os.getenv("PIPER_MODEL_PATH", str(MODELS_DIR / "piper/en_US-lessac-medium.onnx")))
COQUI_MODEL_PATH = Path(os.getenv("COQUI_MODEL_PATH", str(MODELS_DIR / "coqui/")))

# Voice Analysis Settings
PITCH_DETECTION_METHOD = os.getenv("PITCH_DETECTION_METHOD", "praat")
MIN_PITCH = int(os.getenv("MIN_PITCH", 75))
MAX_PITCH = int(os.getenv("MAX_PITCH", 600))

# Meow Generation Settings
MEOW_BASE_PITCH = int(os.getenv("MEOW_BASE_PITCH", 300))
MEOW_PITCH_VARIANCE = float(os.getenv("MEOW_PITCH_VARIANCE", 0.3))
MEOW_DURATION_MIN = float(os.getenv("MEOW_DURATION_MIN", 0.3))
MEOW_DURATION_MAX = float(os.getenv("MEOW_DURATION_MAX", 1.2))

# Cat Personalities Configuration
CAT_PERSONALITIES = {
    "grumpy": os.getenv("ENABLE_GRUMPY_CAT", "True").lower() == "true",
    "wise": os.getenv("ENABLE_WISE_CAT", "True").lower() == "true",
    "anxious": os.getenv("ENABLE_ANXIOUS_CAT", "True").lower() == "true",
    "diva": os.getenv("ENABLE_DIVA_CAT", "True").lower() == "true",
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / os.getenv("LOG_FILE", "meow-now.log").split("/")[-1]

# SIP Configuration (for reference)
SIP_TRUNK_HOST = os.getenv("SIP_TRUNK_HOST", "")
SIP_TRUNK_USERNAME = os.getenv("SIP_TRUNK_USERNAME", "")
SIP_TRUNK_PASSWORD = os.getenv("SIP_TRUNK_PASSWORD", "")
DID_NUMBER = os.getenv("DID_NUMBER", "")

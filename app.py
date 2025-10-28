"""
Main Flask Application for Meow-Now
Provides web interface and health check endpoints
"""
from flask import Flask, jsonify, render_template_string
import logging
import threading
import sys

from config import settings
from agi_server import AGIServer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY

# AGI Server instance
agi_server = None


@app.route('/')
def index():
    """Simple status page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meow-Now Status</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #ff6b6b; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .running { background-color: #51cf66; color: white; }
            .info { background-color: #339af0; color: white; }
            pre { background-color: #f1f3f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🐱 Meow-Now Voice System</h1>

        <div class="status running">
            <strong>Status:</strong> Running
        </div>

        <div class="status info">
            <strong>AGI Server:</strong> {{ agi_host }}:{{ agi_port }}
        </div>

        <h2>Configuration</h2>
        <pre>{{ config }}</pre>

        <h2>About</h2>
        <p>
            Meow-Now is a voice-based automated call tree system that turns your phone number
            into a cat-themed interactive experience.
        </p>

        <h3>Menu Options:</h3>
        <ul>
            <li><strong>Option 1:</strong> Meow Mockery - Voice-to-meow converter (60 seconds max)</li>
            <li><strong>Option 2:</strong> Talkative Cats - Multiple cat personalities (15 seconds each)</li>
        </ul>

        <h2>Endpoints</h2>
        <ul>
            <li><code>GET /</code> - This status page</li>
            <li><code>GET /health</code> - Health check endpoint</li>
            <li><code>GET /config</code> - Configuration details (JSON)</li>
        </ul>
    </body>
    </html>
    """
    config_info = f"""Sample Rate: {settings.SAMPLE_RATE} Hz
Audio Format: {settings.AUDIO_FORMAT}
TTS Engine: {settings.TTS_ENGINE}
Max Recording: {settings.MAX_RECORDING_DURATION}s
Cat Monologue: {settings.CAT_MONOLOGUE_DURATION}s
Enabled Personalities: {', '.join([k for k, v in settings.CAT_PERSONALITIES.items() if v])}"""

    return render_template_string(
        html,
        agi_host=settings.AGI_HOST,
        agi_port=settings.AGI_PORT,
        config=config_info
    )


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    status = {
        'status': 'healthy',
        'agi_server': {
            'host': settings.AGI_HOST,
            'port': settings.AGI_PORT,
            'running': agi_server is not None and agi_server.running
        },
        'configuration': {
            'tts_engine': settings.TTS_ENGINE,
            'sample_rate': settings.SAMPLE_RATE,
            'ollama_url': os.getenv('OLLAMA_URL', 'Not configured')
        }
    }
    return jsonify(status)


@app.route('/config')
def config():
    """Configuration endpoint"""
    config_data = {
        'agi': {
            'host': settings.AGI_HOST,
            'port': settings.AGI_PORT
        },
        'audio': {
            'sample_rate': settings.SAMPLE_RATE,
            'format': settings.AUDIO_FORMAT,
            'max_recording': settings.MAX_RECORDING_DURATION,
            'cat_monologue': settings.CAT_MONOLOGUE_DURATION
        },
        'tts': {
            'engine': settings.TTS_ENGINE
        },
        'personalities': {
            name: enabled for name, enabled in settings.CAT_PERSONALITIES.items()
        }
    }
    return jsonify(config_data)


def start_agi_server():
    """Start AGI server in background thread"""
    global agi_server
    logger.info("Starting AGI server...")
    agi_server = AGIServer()
    agi_server.start()


if __name__ == '__main__':
    import os

    # Start AGI server in background thread
    agi_thread = threading.Thread(target=start_agi_server, daemon=True)
    agi_thread.start()

    logger.info("Starting Flask web server...")

    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=settings.FLASK_DEBUG
    )

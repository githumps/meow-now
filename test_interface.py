#!/usr/bin/env python3
"""
Web-based Test Interface for Meow-Now
Allows testing the call flow using laptop microphone without phone infrastructure
"""
from flask import Flask, render_template_string, request, jsonify, send_file
import logging
import tempfile
import os
from pathlib import Path
import sys
import time
import subprocess
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.voice_analyzer import VoiceAnalyzer
from services.meow_generator import MeowSynthesizer
from services.cat_personalities import TalkativeCatHandler, CAT_REGISTRY
from services.meow_soundboard import MeowSoundboard
from services.real_meow_generator import RealMeowGenerator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize services
voice_analyzer = VoiceAnalyzer()
meow_synthesizer = MeowSynthesizer()
meow_soundboard = MeowSoundboard(sample_rate=settings.SAMPLE_RATE)
real_meow_generator = RealMeowGenerator(sample_rate=settings.SAMPLE_RATE)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Meow-Now Test Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #764ba2;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .phone-container {
            background: #2c3e50;
            border-radius: 30px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .screen {
            background: #34495e;
            border-radius: 10px;
            padding: 20px;
            min-height: 200px;
            color: #ecf0f1;
            font-family: monospace;
            font-size: 14px;
        }
        .button {
            background: #3498db;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        }
        .button:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.6);
        }
        .button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .button-danger {
            background: #e74c3c;
        }
        .button-danger:hover {
            background: #c0392b;
        }
        .button-success {
            background: #2ecc71;
        }
        .button-success:hover {
            background: #27ae60;
        }
        .keypad {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 20px 0;
        }
        .key {
            background: #3498db;
            color: white;
            border: none;
            padding: 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 24px;
            font-weight: bold;
            transition: all 0.2s;
        }
        .key:hover {
            background: #2980b9;
            transform: scale(1.05);
        }
        .key:active {
            transform: scale(0.95);
        }
        .status {
            padding: 15px;
            margin: 15px 0;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }
        .status-idle {
            background: #ecf0f1;
            color: #7f8c8d;
        }
        .status-ringing {
            background: #f39c12;
            color: white;
            animation: pulse 1s infinite;
        }
        .status-connected {
            background: #2ecc71;
            color: white;
        }
        .status-recording {
            background: #e74c3c;
            color: white;
            animation: pulse 1s infinite;
        }
        .status-processing {
            background: #9b59b6;
            color: white;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .recording-indicator {
            display: none;
            width: 20px;
            height: 20px;
            background: #e74c3c;
            border-radius: 50%;
            animation: blink 1s infinite;
            margin: 0 auto;
        }
        .recording-indicator.active {
            display: block;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .log-entry {
            padding: 5px;
            margin: 5px 0;
            border-left: 3px solid #3498db;
            padding-left: 10px;
        }
        .timer {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #e74c3c;
            margin: 10px 0;
        }
        audio {
            width: 100%;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 Meow-Now Test Interface</h1>
        <div class="subtitle">Test the call flow using your laptop microphone</div>

        <div class="phone-container">
            <div id="status" class="status status-idle">
                IDLE - Ready to test
            </div>

            <div class="recording-indicator" id="recordingIndicator"></div>

            <div class="screen" id="screen">
                <div class="log-entry">📞 Welcome to Meow-Now Test Interface</div>
                <div class="log-entry">Click "Start Call" to begin testing</div>
            </div>

            <div id="timer" class="timer" style="display:none;"></div>

            <div id="audioPlayback" style="display:none; margin: 20px 0;">
                <audio id="audioPlayer" controls></audio>
            </div>

            <div class="controls">
                <button id="startCall" class="button button-success" onclick="startCall()">
                    📞 Start Call
                </button>
                <button id="endCall" class="button button-danger" onclick="endCall()" disabled>
                    ❌ End Call
                </button>
            </div>

            <div id="keypad" style="display:none;">
                <div class="keypad">
                    <button class="key" onclick="pressKey('1')">1</button>
                    <button class="key" onclick="pressKey('2')">2</button>
                    <button class="key" onclick="pressKey('3')">3</button>
                    <button class="key" onclick="pressKey('4')">4</button>
                    <button class="key" onclick="pressKey('5')">5</button>
                    <button class="key" onclick="pressKey('6')">6</button>
                    <button class="key" onclick="pressKey('7')">7</button>
                    <button class="key" onclick="pressKey('8')">8</button>
                    <button class="key" onclick="pressKey('9')">9</button>
                    <button class="key" onclick="pressKey('*')">*</button>
                    <button class="key" onclick="pressKey('0')">0</button>
                    <button class="key" onclick="pressKey('#')">#</button>
                </div>
            </div>

            <div id="recordingControls" style="display:none; text-align: center; margin: 20px 0;">
                <button id="startRecording" class="button button-danger" onclick="startRecording()">
                    🎤 Start Talking
                </button>
                <button id="stopRecording" class="button" onclick="stopRecording()" disabled>
                    ⏹️ Stop (or press #)
                </button>
            </div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let callState = 'idle';
        let recordingStartTime;
        let timerInterval;
        let audioStream;

        function log(message, type = 'info') {
            const screen = document.getElementById('screen');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            screen.appendChild(entry);
            screen.scrollTop = screen.scrollHeight;
            console.log(message);
        }

        function setStatus(status, message) {
            const statusDiv = document.getElementById('status');
            statusDiv.className = 'status status-' + status;
            statusDiv.textContent = message;
            callState = status;
        }

        async function startCall() {
            log('📞 Initiating call...');
            setStatus('ringing', '📞 RINGING...');

            // Request microphone permission
            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                log('✅ Microphone access granted');
            } catch (err) {
                log('❌ Microphone access denied: ' + err.message);
                alert('Please allow microphone access to test the system');
                setStatus('idle', 'IDLE - Microphone denied');
                return;
            }

            setTimeout(() => {
                setStatus('connected', '✅ CONNECTED');
                log('✅ Call connected');
                playWelcome();
            }, 1000);

            document.getElementById('startCall').disabled = true;
            document.getElementById('endCall').disabled = false;
        }

        function endCall() {
            log('📞 Call ended');
            setStatus('idle', 'IDLE - Call ended');

            // Stop any ongoing recording
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }

            // Stop audio stream
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }

            // Hide controls
            document.getElementById('keypad').style.display = 'none';
            document.getElementById('recordingControls').style.display = 'none';
            document.getElementById('recordingIndicator').classList.remove('active');
            document.getElementById('timer').style.display = 'none';

            if (timerInterval) {
                clearInterval(timerInterval);
            }

            document.getElementById('startCall').disabled = false;
            document.getElementById('endCall').disabled = true;
        }

        function playWelcome() {
            log('🎵 "Welcome to Meow-Now! Press 1 for meow mockery, or press 2 for talkative cats."');

            // Simulate audio playback delay
            setTimeout(() => {
                document.getElementById('keypad').style.display = 'block';
                log('⌨️ Waiting for key press...');
            }, 3000);
        }

        function pressKey(key) {
            log('⌨️ Key pressed: ' + key);

            if (key === '1') {
                log('✅ Option 1 selected: Meow Mockery');
                handleMeowMockery();
            } else if (key === '2') {
                log('✅ Option 2 selected: Talkative Cats');
                handleTalkativeCats();
            } else {
                log('❓ Invalid option. Press 1 or 2.');
            }
        }

        function handleMeowMockery() {
            document.getElementById('keypad').style.display = 'none';
            log('🎵 "Get ready to be mocked! Start talking after the beep. You have 60 seconds. Press # when finished."');

            setTimeout(() => {
                log('🔔 BEEP!');
                document.getElementById('recordingControls').style.display = 'block';
            }, 3000);
        }

        async function startRecording() {
            audioChunks = [];

            try {
                mediaRecorder = new MediaRecorder(audioStream);

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    log('⏹️ Recording stopped, processing...');
                    setStatus('processing', '⚙️ PROCESSING - Generating meows...');
                    document.getElementById('recordingIndicator').classList.remove('active');
                    document.getElementById('timer').style.display = 'none';

                    if (timerInterval) {
                        clearInterval(timerInterval);
                    }

                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                    // Send to server for processing
                    await processMeowMockery(audioBlob);
                };

                mediaRecorder.start();
                setStatus('recording', '🎤 RECORDING - Speak now!');
                log('🎤 Recording started... speak now!');

                document.getElementById('recordingIndicator').classList.add('active');
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;

                // Start timer
                recordingStartTime = Date.now();
                document.getElementById('timer').style.display = 'block';
                updateTimer();
                timerInterval = setInterval(updateTimer, 100);

                // Auto-stop after 60 seconds
                setTimeout(() => {
                    if (mediaRecorder && mediaRecorder.state === 'recording') {
                        log('⏱️ 60 seconds elapsed, stopping recording');
                        stopRecording();
                    }
                }, 60000);

            } catch (err) {
                log('❌ Error starting recording: ' + err.message);
            }
        }

        function updateTimer() {
            const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
            const remaining = 60 - elapsed;
            document.getElementById('timer').textContent = remaining + 's remaining';

            if (remaining <= 0) {
                stopRecording();
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                document.getElementById('startRecording').disabled = false;
                document.getElementById('stopRecording').disabled = true;
            }
        }

        async function processMeowMockery(audioBlob) {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            try {
                const response = await fetch('/api/test/meow-mockery', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    log('✅ Voice analysis complete');
                    log('   - Mean pitch: ' + result.analysis.mean_pitch.toFixed(1) + ' Hz');
                    log('   - Segments: ' + result.analysis.segments);
                    log('🐱 Generated meow mockery!');

                    // Play the meow audio
                    const audioPlayback = document.getElementById('audioPlayback');
                    const audioPlayer = document.getElementById('audioPlayer');
                    audioPlayback.style.display = 'block';
                    audioPlayer.src = '/api/test/audio/' + result.audio_file;
                    audioPlayer.play();

                    log('🎵 Playing meow mockery...');

                    audioPlayer.onended = () => {
                        setTimeout(() => {
                            log('👋 Thanks for letting us mock you! Goodbye!');
                            setTimeout(endCall, 2000);
                        }, 1000);
                    };
                } else {
                    log('❌ Error: ' + result.error);
                    setTimeout(endCall, 2000);
                }
            } catch (err) {
                log('❌ Error processing audio: ' + err.message);
                setTimeout(endCall, 2000);
            }
        }

        async function handleTalkativeCats() {
            document.getElementById('keypad').style.display = 'none';
            log('🎵 "Connecting you to one of our talkative cats..."');
            setStatus('processing', '⚙️ PROCESSING - Selecting cat...');

            try {
                const response = await fetch('/api/test/talkative-cats', {
                    method: 'POST'
                });

                const result = await response.json();

                if (result.success) {
                    log('✅ Selected: ' + result.cat_name + ' Cat');
                    log('💬 Generating monologue...');

                    setStatus('connected', '🐱 CAT SPEAKING...');

                    // Play the cat audio
                    const audioPlayback = document.getElementById('audioPlayback');
                    const audioPlayer = document.getElementById('audioPlayer');
                    audioPlayback.style.display = 'block';
                    audioPlayer.src = '/api/test/audio/' + result.audio_file;
                    audioPlayer.play();

                    log('🎵 Playing cat monologue...');
                    log('   "' + result.text.substring(0, 100) + '..."');

                    audioPlayer.onended = () => {
                        log('👋 Cat hung up!');
                        setTimeout(endCall, 1000);
                    };
                } else {
                    log('❌ Error: ' + result.error);
                    setTimeout(endCall, 2000);
                }
            } catch (err) {
                log('❌ Error: ' + err.message);
                setTimeout(endCall, 2000);
            }
        }

        // Allow pressing # to stop recording
        document.addEventListener('keydown', (e) => {
            if (e.key === '#' && callState === 'recording') {
                log('⌨️ # key pressed');
                stopRecording();
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main test interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/test/meow-mockery', methods=['POST'])
def test_meow_mockery():
    """Process meow mockery test"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            audio_file.save(tmp.name)
            webm_path = Path(tmp.name)

        logger.info(f"Saved WebM audio: {webm_path}")

        # Convert WebM to WAV using ffmpeg (if available)
        wav_path = webm_path.with_suffix('.wav')
        try:
            import subprocess
            subprocess.run([
                'ffmpeg', '-i', str(webm_path),
                '-ar', '8000',
                '-ac', '1',
                '-y',
                str(wav_path)
            ], check=True, capture_output=True)
            logger.info(f"Converted to WAV: {wav_path}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            # Try to use the webm directly if ffmpeg not available
            wav_path = webm_path

        # Analyze voice
        analysis = voice_analyzer.analyze_audio_file(wav_path)

        # Generate meows using REAL cat sounds
        meow_audio = real_meow_generator.generate_meow_sequence(analysis)

        # Save meow audio
        meow_file = settings.GENERATED_DIR / f"test_meow_{os.getpid()}.wav"
        import soundfile as sf
        sf.write(meow_file, meow_audio, settings.SAMPLE_RATE)

        logger.info(f"Generated meow file: {meow_file}")

        # Cleanup temporary files
        try:
            webm_path.unlink()
            if wav_path != webm_path:
                wav_path.unlink()
        except:
            pass

        return jsonify({
            'success': True,
            'analysis': {
                'mean_pitch': float(analysis['mean_pitch']),
                'pitch_range': [float(analysis['pitch_range'][0]), float(analysis['pitch_range'][1])],
                'segments': len(analysis['speech_segments']),
                'duration': float(analysis['duration'])
            },
            'audio_file': meow_file.name
        })

    except Exception as e:
        logger.error(f"Error processing meow mockery: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test/talkative-cats', methods=['POST'])
def test_talkative_cats():
    """Process talkative cats test"""
    try:
        import random

        # Select random enabled cat
        enabled_cats = [
            name for name, enabled in settings.CAT_PERSONALITIES.items()
            if enabled and name in CAT_REGISTRY
        ]

        if not enabled_cats:
            return jsonify({'success': False, 'error': 'No cat personalities enabled'}), 400

        cat_name = random.choice(enabled_cats)
        cat_class = CAT_REGISTRY[cat_name]
        cat = cat_class()

        logger.info(f"Selected cat: {cat.name}")

        # Generate monologue
        ollama_url = os.getenv('OLLAMA_URL', None)
        text = cat.generate_monologue(ollama_url)

        logger.info(f"Generated text: {text[:100]}...")

        # Generate TTS audio
        audio_file = settings.GENERATED_DIR / f"test_cat_{cat.name.lower()}_{os.getpid()}.wav"

        # Try to generate audio using Piper
        try:
            import subprocess

            if settings.PIPER_MODEL_PATH.exists():
                # Use Piper TTS
                cmd = [
                    "piper",
                    "--model", str(settings.PIPER_MODEL_PATH),
                    "--output_file", str(audio_file)
                ]

                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                stdout, stderr = process.communicate(input=text.encode())

                if process.returncode != 0:
                    raise Exception(f"Piper failed: {stderr.decode()}")

                logger.info(f"Generated audio with Piper: {audio_file}")
            else:
                # Fallback: create silent audio file
                logger.warning("Piper model not found, creating placeholder audio")
                import numpy as np
                import soundfile as sf

                # Create 15 seconds of silence
                duration = settings.CAT_MONOLOGUE_DURATION
                samples = np.zeros(int(duration * settings.SAMPLE_RATE))
                sf.write(audio_file, samples, settings.SAMPLE_RATE)

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            # Create silent placeholder
            import numpy as np
            import soundfile as sf
            samples = np.zeros(int(15 * settings.SAMPLE_RATE))
            sf.write(audio_file, samples, settings.SAMPLE_RATE)

        return jsonify({
            'success': True,
            'cat_name': cat.name,
            'text': text,
            'audio_file': audio_file.name
        })

    except Exception as e:
        logger.error(f"Error in talkative cats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        file_path = settings.GENERATED_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        return send_file(file_path, mimetype='audio/wav')
    except Exception as e:
        logger.error(f"Error serving audio: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# Debug Routes - Direct Feature Testing
# ============================================

@app.route('/debug')
def debug_panel():
    """Debug panel for direct feature testing"""
    debug_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Meow-Now Debug Panel</title>
    <style>
        body {
            font-family: 'Monaco', 'Courier New', monospace;
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        h1 {
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }
        h2 {
            color: #569cd6;
            margin-top: 30px;
        }
        .section {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }
        .button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .button:hover {
            background: #1177bb;
        }
        .button-success {
            background: #107c10;
        }
        .button-success:hover {
            background: #16a615;
        }
        input[type="file"],
        input[type="text"] {
            background: #3c3c3c;
            border: 1px solid #3e3e42;
            color: #d4d4d4;
            padding: 8px;
            border-radius: 3px;
            margin: 5px 0;
            font-family: inherit;
        }
        input[type="text"] {
            width: 300px;
        }
        .output {
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 3px;
            padding: 15px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        }
        .success { color: #4ec9b0; }
        .error { color: #f48771; }
        .info { color: #569cd6; }
        audio {
            width: 100%;
            margin: 10px 0;
        }
        .inline-form {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
    </style>
</head>
<body>
    <h1>🐱 Meow-Now Debug Panel</h1>
    <p style="color: #858585;">Direct access to all features for testing</p>
    <p><a href="/" style="color: #569cd6;">← Back to Test Interface</a></p>

    <div class="section">
        <h2>🎤 Meownalysis</h2>
        <p>Upload audio to analyze pitch and rhythm</p>
        <div class="inline-form">
            <input type="file" id="analysisFile" accept="audio/*">
            <button class="button button-success" onclick="analyzeVoice()">Analyze</button>
        </div>
        <div id="analysisOutput" class="output" style="display:none;"></div>
    </div>

    <div class="section">
        <h2>🐈 Meow Generation</h2>
        <p>Generate custom meows with specific parameters</p>
        <div class="inline-form">
            <label>Pitch (Hz): <input type="text" id="meowPitch" value="300" style="width:80px;"></label>
            <label>Duration (s): <input type="text" id="meowDuration" value="0.8" style="width:80px;"></label>
            <label>Variance: <input type="text" id="meowVariance" value="0.3" style="width:80px;"></label>
            <button class="button button-success" onclick="generateMeow()">Generate</button>
        </div>
        <div id="meowOutput" class="output" style="display:none;"></div>
        <div id="meowAudio" style="display:none;"></div>
    </div>

    <div class="section">
        <h2>😺 Cat Personalities</h2>
        <div class="inline-form">
            <select id="catSelect">
                <option value="grumpy">Grumpy Cat 😾</option>
                <option value="wise">Wise Cat 🧘</option>
                <option value="anxious">Anxious Cat 😰</option>
                <option value="diva">Diva Cat 💅</option>
            </select>
            <button class="button button-success" onclick="testCat()">Generate</button>
        </div>
        <div id="catOutput" class="output" style="display:none;"></div>
        <div id="catAudio" style="display:none;"></div>
    </div>

    <div class="section">
        <h2>🎵 Meow Soundboard - Find the Right Sound!</h2>
        <p>Test 8 different meow synthesis methods. Which one sounds most like a cat?</p>
        <div class="inline-form">
            <label>Pitch (Hz): <input type="text" id="soundboardPitch" value="400" style="width:80px;"></label>
            <label>Duration (s): <input type="text" id="soundboardDuration" value="0.8" style="width:80px;"></label>
            <button class="button button-success" onclick="generateSoundboard()">Generate All Methods</button>
        </div>
        <div id="soundboardOutput" class="output" style="display:none;"></div>
        <div id="soundboardAudio"></div>
    </div>

    <div class="section">
        <h2>ℹ️ System Info</h2>
        <button class="button" onclick="getSystemInfo()">Refresh</button>
        <div id="systemOutput" class="output"></div>
    </div>

    <script>
        async function analyzeVoice() {
            const file = document.getElementById('analysisFile').files[0];
            if (!file) { alert('Please select a file'); return; }

            const output = document.getElementById('analysisOutput');
            output.style.display = 'block';
            output.innerHTML = '<span class="info">Analyzing...</span>';

            const formData = new FormData();
            formData.append('audio', file);

            try {
                const res = await fetch('/api/debug/analyze', { method: 'POST', body: formData });
                const r = await res.json();

                if (r.success) {
                    output.innerHTML = `<span class="success">✓ Analysis Complete</span>

Mean Pitch: ${r.analysis.mean_pitch.toFixed(2)} Hz
Pitch Range: ${r.analysis.pitch_range[0].toFixed(2)} - ${r.analysis.pitch_range[1].toFixed(2)} Hz
Duration: ${r.analysis.duration.toFixed(2)}s
Segments: ${r.analysis.segments}
Speaking Rate: ${r.analysis.speaking_rate.toFixed(2)}/s`;
                } else {
                    output.innerHTML = `<span class="error">✗ ${r.error}</span>`;
                }
            } catch (e) {
                output.innerHTML = `<span class="error">✗ ${e.message}</span>`;
            }
        }

        async function generateMeow() {
            const output = document.getElementById('meowOutput');
            output.style.display = 'block';
            output.innerHTML = '<span class="info">Generating...</span>';

            try {
                const res = await fetch('/api/debug/generate-meow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pitch: parseFloat(document.getElementById('meowPitch').value),
                        duration: parseFloat(document.getElementById('meowDuration').value),
                        variance: parseFloat(document.getElementById('meowVariance').value)
                    })
                });
                const r = await res.json();

                if (r.success) {
                    output.innerHTML = `<span class="success">✓ Generated</span>
Duration: ${r.duration.toFixed(2)}s`;
                    document.getElementById('meowAudio').style.display = 'block';
                    document.getElementById('meowAudio').innerHTML =
                        `<audio controls autoplay src="/api/test/audio/${r.filename}"></audio>`;
                } else {
                    output.innerHTML = `<span class="error">✗ ${r.error}</span>`;
                }
            } catch (e) {
                output.innerHTML = `<span class="error">✗ ${e.message}</span>`;
            }
        }

        async function testCat() {
            const output = document.getElementById('catOutput');
            output.style.display = 'block';
            output.innerHTML = '<span class="info">Generating...</span>';

            try {
                const res = await fetch('/api/debug/test-cat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cat: document.getElementById('catSelect').value })
                });
                const r = await res.json();

                if (r.success) {
                    output.innerHTML = `<span class="success">✓ ${r.cat_name} Cat</span>

"${r.text}"

Method: ${r.method || 'N/A'}`;
                    document.getElementById('catAudio').style.display = 'block';
                    document.getElementById('catAudio').innerHTML =
                        `<audio controls autoplay src="/api/test/audio/${r.audio_file}</audio>`;
                } else {
                    output.innerHTML = `<span class="error">✗ ${r.error}</span>`;
                }
            } catch (e) {
                output.innerHTML = `<span class="error">✗ ${e.message}</span>`;
            }
        }

        async function getSystemInfo() {
            const output = document.getElementById('systemOutput');
            output.innerHTML = '<span class="info">Loading...</span>';

            try {
                const res = await fetch('/api/debug/system-info');
                const r = await res.json();

                output.innerHTML = `<span class="success">✓ System Info</span>

Praat: ${r.praat_available ? '✓' : '✗'}
Pitch Method: ${r.pitch_method}
TTS Engine: ${r.tts_engine}
Piper Model: ${r.piper_model_exists ? '✓' : '✗'}

Ollama URL: ${r.ollama_url || 'Not configured'}
Ollama Connected: ${r.ollama_connected ? '✓' : '✗'}

Generated Files: ${r.generated_files}
Sample Rate: ${r.sample_rate} Hz`;
            } catch (e) {
                output.innerHTML = `<span class="error">✗ ${e.message}</span>`;
            }
        }

        async function generateSoundboard() {
            const output = document.getElementById('soundboardOutput');
            const audioDiv = document.getElementById('soundboardAudio');
            output.style.display = 'block';
            output.innerHTML = '<span class="info">Generating all 8 meow methods...</span>';
            audioDiv.innerHTML = '';

            try {
                const res = await fetch('/api/debug/meow-soundboard', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pitch: parseFloat(document.getElementById('soundboardPitch').value),
                        duration: parseFloat(document.getElementById('soundboardDuration').value)
                    })
                });
                const r = await res.json();

                if (r.success) {
                    output.innerHTML = '<span class="success">✓ Generated all methods!</span>';

                    let audioHTML = '<div style="margin-top: 15px;">';
                    const methods = r.methods;

                    for (const [methodName, methodData] of Object.entries(methods)) {
                        if (methodData.success) {
                            const num = methodName.replace('method_', '');
                            audioHTML += `
                                <div style="margin: 15px 0; padding: 10px; background: #2d2d30; border-radius: 5px;">
                                    <strong style="color: #4ec9b0;">Method ${num}</strong>: ${methodData.description}
                                    <audio controls style="width: 100%; margin-top: 5px;" src="/api/test/audio/${methodData.filename}"></audio>
                                </div>
                            `;
                        }
                    }
                    audioHTML += '</div>';
                    audioDiv.innerHTML = audioHTML;
                } else {
                    output.innerHTML = `<span class="error">✗ ${r.error}</span>`;
                }
            } catch (e) {
                output.innerHTML = `<span class="error">✗ ${e.message}</span>`;
            }
        }

        window.addEventListener('load', getSystemInfo);
    </script>
</body>
</html>
    """
    return debug_html


@app.route('/api/debug/analyze', methods=['POST'])
def debug_analyze():
    """Debug endpoint for voice analysis"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file'}), 400

        audio_file = request.files['audio']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio_file.save(tmp.name)
            audio_path = Path(tmp.name)

        # Convert if needed
        if not audio_path.suffix == '.wav':
            wav_path = audio_path.with_suffix('.wav')
            try:
                subprocess.run(['ffmpeg', '-i', str(audio_path), '-ar', '8000', '-ac', '1', '-y', str(wav_path)],
                             check=True, capture_output=True)
                audio_path.unlink()
                audio_path = wav_path
            except:
                pass

        # Analyze
        analysis = voice_analyzer.analyze_audio_file(audio_path)

        # Cleanup
        audio_path.unlink()

        return jsonify({
            'success': True,
            'analysis': {
                'mean_pitch': float(analysis['mean_pitch']),
                'pitch_range': [float(analysis['pitch_range'][0]), float(analysis['pitch_range'][1])],
                'pitch_variance': float(analysis['pitch_variance']),
                'segments': len(analysis['speech_segments']),
                'duration': float(analysis['duration']),
                'speaking_rate': float(analysis['speaking_rate'])
            }
        })

    except Exception as e:
        logger.error(f"Debug analyze error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug/generate-meow', methods=['POST'])
def debug_generate_meow():
    """Debug endpoint for meow generation"""
    try:
        data = request.json
        pitch = data.get('pitch', 300)
        duration = data.get('duration', 0.8)
        variance = data.get('variance', 0.3)

        # Generate meow
        meow_audio = meow_synthesizer.generate_meow(pitch, duration, variance)

        # Save
        filename = f"debug_meow_{int(time.time())}.wav"
        filepath = settings.GENERATED_DIR / filename
        import soundfile as sf
        sf.write(filepath, meow_audio, settings.SAMPLE_RATE)

        return jsonify({
            'success': True,
            'filename': filename,
            'duration': len(meow_audio) / settings.SAMPLE_RATE
        })

    except Exception as e:
        logger.error(f"Debug meow generation error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug/test-cat', methods=['POST'])
def debug_test_cat():
    """Debug endpoint for cat personality testing"""
    try:
        data = request.json
        cat_name = data.get('cat', 'grumpy')

        if cat_name not in CAT_REGISTRY:
            return jsonify({'success': False, 'error': f'Unknown cat: {cat_name}'}), 400

        cat_class = CAT_REGISTRY[cat_name]
        cat = cat_class()

        # Generate text
        ollama_url = os.getenv('OLLAMA_URL', None)
        text = cat.generate_monologue(ollama_url)

        # Try TTS
        filename = f"debug_cat_{cat_name}_{int(time.time())}.wav"
        filepath = settings.GENERATED_DIR / filename

        try:
            if settings.PIPER_MODEL_PATH.exists():
                cmd = ["piper", "--model", str(settings.PIPER_MODEL_PATH), "--output_file", str(filepath)]
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate(input=text.encode())

                if process.returncode == 0:
                    return jsonify({
                        'success': True,
                        'cat_name': cat.name,
                        'text': text,
                        'audio_file': filename,
                        'method': 'Piper TTS'
                    })
        except Exception as e:
            logger.warning(f"TTS failed: {e}")

        # Fallback: create silent audio
        import numpy as np
        import soundfile as sf
        silence = np.zeros(int(15 * settings.SAMPLE_RATE))
        sf.write(filepath, silence, settings.SAMPLE_RATE)

        return jsonify({
            'success': True,
            'cat_name': cat.name,
            'text': text,
            'audio_file': filename,
            'method': 'Fallback (silent)'
        })

    except Exception as e:
        logger.error(f"Debug cat test error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/debug/system-info')
def debug_system_info():
    """Debug endpoint for system information"""
    try:
        # Check praat
        praat_available = False
        try:
            import parselmouth
            praat_available = True
        except:
            pass

        # Check ollama
        ollama_connected = False
        ollama_url = os.getenv('OLLAMA_URL', '')
        if ollama_url:
            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                ollama_connected = response.status_code == 200
            except:
                pass

        # Count files
        generated_files = len(list(settings.GENERATED_DIR.glob('*.wav')))

        return jsonify({
            'praat_available': praat_available,
            'pitch_method': 'praat' if praat_available else 'basic',
            'tts_engine': settings.TTS_ENGINE,
            'piper_model_exists': settings.PIPER_MODEL_PATH.exists(),
            'ollama_url': ollama_url,
            'ollama_connected': ollama_connected,
            'sample_rate': settings.SAMPLE_RATE,
            'generated_files': generated_files
        })

    except Exception as e:
        logger.error(f"System info error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug/meow-soundboard', methods=['POST'])
def debug_meow_soundboard():
    """Generate all meow synthesis methods for comparison"""
    try:
        data = request.json or {}
        pitch = data.get('pitch', 400)
        duration = data.get('duration', 0.8)

        # Generate all methods
        results = meow_soundboard.generate_all_methods(pitch, duration)

        # Save audio files
        import soundfile as sf
        import time

        response_data = {}
        for method_name, method_data in results.items():
            if method_data['success']:
                filename = f"soundboard_{method_name}_{int(time.time())}.wav"
                filepath = settings.GENERATED_DIR / filename
                sf.write(filepath, method_data['audio'], settings.SAMPLE_RATE)

                response_data[method_name] = {
                    'filename': filename,
                    'description': method_data['description'],
                    'success': True
                }
            else:
                response_data[method_name] = {
                    'description': method_data['description'],
                    'success': False
                }

        return jsonify({
            'success': True,
            'methods': response_data
        })

    except Exception as e:
        logger.error(f"Soundboard error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    import os

    logger.info("=" * 60)
    logger.info("Meow-Now Test Interface")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Starting web server on http://localhost:5001")
    logger.info("")
    logger.info("Open your browser and go to: http://localhost:5001")
    logger.info("")
    logger.info("This interface simulates the call flow using your laptop microphone.")
    logger.info("No Asterisk or NumberBarn required for testing!")
    logger.info("")
    logger.info("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )

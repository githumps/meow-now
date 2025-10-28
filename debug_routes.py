"""
Debug routes to append to test_interface.py
"""

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
        <h2>🎤 Voice Analysis</h2>
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
                        `<audio controls autoplay src="/api/test/audio/${r.audio_file}"></audio>`;
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

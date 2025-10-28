# Local Testing Guide

Test Meow-Now locally using your laptop microphone - **no phone number or Asterisk required!**

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the test interface
python test_interface.py

# 3. Open browser
# Go to: http://localhost:5001
```

## What You Get

A beautiful web interface that simulates the entire call flow:

- **Virtual Phone** - Click "Start Call" to simulate calling
- **IVR Menu** - On-screen keypad to press 1 or 2
- **Microphone Recording** - Use your laptop mic to test meow mockery
- **Real-time Processing** - See the actual voice analysis and meow generation
- **Audio Playback** - Hear the generated meows or cat personalities

## Testing Option 1: Meow Mockery

1. Click **"Start Call"**
2. Wait for welcome message (simulated)
3. Press **1** on the virtual keypad
4. Click **"Start Talking"**
5. **Speak into your laptop microphone**
   - Talk for a few seconds
   - Try different pitches (high, low, singing)
   - The system records for up to 60 seconds
6. Click **"Stop"** or press **#**
7. Watch the processing:
   - Voice analysis runs (pitch detection)
   - Meow synthesis generates matching meows
   - Audio plays back automatically
8. Hear yourself mocked by a cat! 🐱

## Testing Option 2: Talkative Cats

1. Click **"Start Call"**
2. Wait for welcome message
3. Press **2** on the virtual keypad
4. Wait for processing:
   - Random cat personality selected
   - LLM generates monologue (if Ollama configured)
   - TTS creates audio
5. Hear the cat's 15-second monologue
6. Call ends automatically

## Features

### Visual Call Flow
```
┌─────────────────────────────┐
│     Meow-Now Test UI        │
├─────────────────────────────┤
│                             │
│  Status: 📞 RINGING...      │
│                             │
│  ┌───────────────────────┐  │
│  │ Screen (Call Log)     │  │
│  │ • Call connected      │  │
│  │ • Playing welcome     │  │
│  │ • Press 1 or 2        │  │
│  └───────────────────────┘  │
│                             │
│  ⏺️ Recording Indicator     │
│  ⏱️ Timer: 45s remaining    │
│                             │
│  ┌─┬─┬─┐                   │
│  │1│2│3│ Virtual Keypad    │
│  ├─┼─┼─┤                   │
│  │4│5│6│                   │
│  ├─┼─┼─┤                   │
│  │7│8│9│                   │
│  ├─┼─┼─┤                   │
│  │*│0│#│                   │
│  └─┴─┴─┘                   │
│                             │
│  [🎤 Start Talking]         │
│  [⏹️ Stop]                  │
│                             │
│  Audio Playback:            │
│  ▶️ ━━━━━━━●─── 00:15      │
│                             │
└─────────────────────────────┘
```

### Real-time Logs

The screen shows everything happening:
```
📞 Initiating call...
✅ Call connected
🎵 "Welcome to Meow-Now! Press 1 for..."
⌨️ Key pressed: 1
✅ Option 1 selected: Meow Mockery
🎵 "Get ready to be mocked! Start talking..."
🔔 BEEP!
🎤 Recording started... speak now!
⏹️ Recording stopped, processing...
✅ Voice analysis complete
   - Mean pitch: 185.3 Hz
   - Segments: 4
🐱 Generated meow mockery!
🎵 Playing meow mockery...
👋 Thanks for letting us mock you! Goodbye!
📞 Call ended
```

### Status Indicators

- **IDLE** - Ready to test
- **RINGING** - Call initiating (pulsing animation)
- **CONNECTED** - Call active
- **RECORDING** - Microphone recording (red pulsing dot)
- **PROCESSING** - Analyzing/generating audio

## How It Works

### Architecture

```
Browser (You)
    ↓ WebRTC Audio
Flask Test Server (test_interface.py)
    ↓ Process Recording
Voice Analyzer (services/voice_analyzer.py)
    ↓ Extract Pitch/Rhythm
Meow Synthesizer (services/meow_generator.py)
    ↓ Generate Meows
Browser ← Play Audio
```

### What Gets Tested

✅ **IVR Menu Logic** - Call routing works
✅ **Voice Analysis** - Pitch detection algorithms
✅ **Meow Synthesis** - Real-time meow generation
✅ **Cat Personalities** - Text generation and TTS
✅ **Audio Processing** - Full audio pipeline
✅ **Timing** - 60-second limits, auto-hangup

### What Doesn't Get Tested

❌ **Asterisk Integration** - No SIP/AGI testing
❌ **Phone Network** - No real telephony
❌ **NumberBarn** - No trunk configuration
❌ **Codec Conversion** - Uses WAV instead of ulaw/alaw
❌ **DTMF Detection** - Simulated with buttons

## Requirements

### Browser Requirements

- **Modern browser** with Web Audio API support
  - Chrome 70+
  - Firefox 65+
  - Safari 14+
  - Edge 79+
- **Microphone access** - Allow when prompted
- **JavaScript enabled**

### System Requirements

- **Python 3.8+**
- **FFmpeg** (for audio conversion)
  ```bash
  # macOS
  brew install ffmpeg

  # Linux
  sudo apt install ffmpeg

  # Windows
  # Download from: https://ffmpeg.org/download.html
  ```

- **Piper TTS Model** (optional, for cat personalities)
  ```bash
  cd models/piper
  wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
  wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
  ```

## Troubleshooting

### "Microphone access denied"

**Fix**:
1. Browser Settings → Privacy → Microphone
2. Allow `localhost` or `127.0.0.1`
3. Refresh page and try again

### "No audio playback"

**Check**:
- Browser console for errors (F12)
- Generated audio file exists: `audio/generated/`
- Audio format supported by browser

### "Voice analysis failed"

**Possible causes**:
- Recording too short (speak for at least 2-3 seconds)
- Microphone not working (test in system settings)
- FFmpeg not installed
- Check logs: `tail -f logs/meow-now.log`

### "Cat personalities don't work"

**Fix**:
1. Check Piper model exists: `ls models/piper/*.onnx`
2. If missing, download (see Requirements above)
3. Try without Ollama (uses fallback monologues)
4. Check logs for TTS errors

### "FFmpeg not found"

**Symptoms**: Recording fails with conversion error

**Fix**:
```bash
# Verify FFmpeg installed
ffmpeg -version

# If not installed, install it:
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Or download from: https://ffmpeg.org/
```

## Testing Tips

### For Meow Mockery

1. **Vary your pitch**:
   - Speak in high voice → High-pitched meows
   - Speak in low voice → Low-pitched meows
   - Sing → Musical meows

2. **Try different patterns**:
   - Short bursts: "Cat. Cat. Cat." → Quick meows
   - Long sentences → Extended meow sequences
   - Pauses between words → Gaps between meows

3. **Test edge cases**:
   - Whisper (very low volume)
   - Shout (very high volume)
   - Rapid speech
   - Slow speech
   - Singing

### For Talkative Cats

1. **Test all personalities**:
   - Refresh page and call again
   - Each time gets random cat
   - Note the different speaking styles

2. **With Ollama** (if configured):
   - Responses will be unique each time
   - More natural and varied

3. **Without Ollama**:
   - Uses pre-written fallback monologues
   - Still entertaining!

## Comparing to Real Calls

### What's the Same
- IVR menu flow
- Voice analysis algorithms
- Meow synthesis
- Cat personality logic
- Audio generation
- Timing and limits

### What's Different
- **Audio Quality**: Browser WebM vs. telephony ulaw (8kHz)
- **Input Method**: Mouse clicks vs. phone DTMF tones
- **Network**: Local vs. SIP/RTP over internet
- **Latency**: Instant vs. network delays

## Next Steps After Testing

Once you've tested locally:

1. **Verify Everything Works**
   - Meow mockery generates correct pitches
   - Cat personalities are entertaining
   - Audio quality is good
   - No errors in logs

2. **Customize**
   - Tweak meow generation parameters
   - Add new cat personalities
   - Adjust timing

3. **Deploy for Real**
   - Set up NumberBarn (see [docs/NUMBERBARN.md](docs/NUMBERBARN.md))
   - Configure Asterisk
   - Deploy Docker containers
   - Test with real phone calls

## Advanced Testing

### Test Voice Analysis Directly

```python
from services.voice_analyzer import VoiceAnalyzer
from pathlib import Path

analyzer = VoiceAnalyzer()
analysis = analyzer.analyze_audio_file(Path('test.wav'))

print(f"Mean pitch: {analysis['mean_pitch']:.1f} Hz")
print(f"Segments: {len(analysis['speech_segments'])}")
```

### Test Meow Generation

```python
from services.meow_generator import MeowSynthesizer
import soundfile as sf

synth = MeowSynthesizer()
meow = synth.generate_meow(300, 0.8)  # 300Hz, 0.8 seconds

sf.write('test_meow.wav', meow, 8000)
```

### Test Cat Personalities

```python
from services.cat_personalities import GrumpyCat

cat = GrumpyCat()
text = cat.generate_monologue()
print(text)
```

## API Endpoints

The test interface exposes these APIs:

### POST `/api/test/meow-mockery`
- **Input**: Audio file (WebM/WAV)
- **Output**: JSON with analysis + generated meow file

### POST `/api/test/talkative-cats`
- **Output**: JSON with cat name, text, audio file

### GET `/api/test/audio/<filename>`
- **Output**: WAV audio file

You can test these directly:

```bash
# Test meow mockery
curl -X POST -F "audio=@recording.wav" \
  http://localhost:5001/api/test/meow-mockery

# Test talkative cats
curl -X POST http://localhost:5001/api/test/talkative-cats

# Download generated audio
curl http://localhost:5001/api/test/audio/test_meow_12345.wav -o meow.wav
```

## Recording Test Audio

Want to test without using the web interface?

```bash
# Record 5 seconds of audio
sox -d test_recording.wav trim 0 5

# Or use FFmpeg
ffmpeg -f avfoundation -i ":0" -t 5 test_recording.wav

# Test it
curl -X POST -F "audio=@test_recording.wav" \
  http://localhost:5001/api/test/meow-mockery
```

## Integration Testing

Before deploying to production:

1. **Test Locally** ✅ (this guide)
2. **Test with Asterisk** (internal calls)
3. **Test with SIP trunk** (without real number)
4. **Test with NumberBarn** (real calls)

Each step adds more complexity. Start here!

## Getting Help

If something doesn't work:

1. **Check browser console** (F12 → Console tab)
2. **Check server logs**:
   ```bash
   # Server output shows real-time logs
   # Or check file:
   tail -f logs/meow-now.log
   ```
3. **Enable debug mode**:
   ```python
   # In test_interface.py, line ~520
   app.run(debug=True)  # Already enabled
   ```
4. **Test components separately** (see Advanced Testing above)

## Fun Experiments

Try these once you have it working:

1. **Beat Boxing**: Beat box into the mic, hear beat box meows
2. **Singing**: Sing a song, hear it meowed back
3. **Different Languages**: Speak another language
4. **Sound Effects**: Make weird sounds, see how they're interpreted
5. **Multiple Speakers**: Have someone else talk, compare meows
6. **Music Playback**: Play music near mic, see musical meows

## Performance Notes

- **First call slower**: Models loading, caches warming up
- **Subsequent calls faster**: Everything cached
- **Large recordings**: >30 seconds may take time to process
- **CPU usage**: Check `top` or Activity Monitor

## Cleanup

Generated files accumulate in `audio/generated/`. Clean up periodically:

```bash
# Remove old test files
rm audio/generated/test_*

# Or keep last 10
ls -t audio/generated/test_* | tail -n +11 | xargs rm
```

---

**Have fun testing!** 🐱 This is the fastest way to see Meow-Now in action without setting up any phone infrastructure.

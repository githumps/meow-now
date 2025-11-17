# Meow-Now: Self-Hosted Cat Voicemail System

A voice-based automated call tree system that turns your phone number into a cat-themed interactive experience. Callers can choose between:

1. **Meow Mockery** - Real-time voice-to-meow converter that mimics the caller's pitch and rhythm (max 60 seconds)
2. **Talkative Cats** - Multiple cat personalities that deliver 15-second monologues

Perfect for pranks, art projects, or just having fun with your phone number!

## Features

- **Zero per-minute costs** - Fully self-hosted, no cloud API fees
- **Real-time pitch/rhythm matching** - Meows that actually mock the caller's voice
- **Multiple cat personalities** - Grumpy, Wise, Anxious, and Diva cats with unique voices
- **Ollama LLM integration** - Dynamic cat responses using your local LLM over Tailscale
- **Docker/Unraid ready** - Easy deployment with docker-compose
- **Professional IVR system** - Call tree routing with audio prompts
- **Local TTS** - Piper and Coqui TTS support, no cloud required

## 🆕 Status: Ready for Production Deployment!

**Just Completed:**
- ✅ Realistic cat meow generation (5 different meow types: short, long, trill, chirp, yowl)
- ✅ Complete IVR system with audio prompts
- ✅ Production-ready Docker setup with Asterisk
- ✅ Comprehensive deployment guide (DEPLOYMENT.md)
- ✅ Automated setup scripts (scripts/setup_audio.py, scripts/deploy.sh)
- ✅ Full Asterisk integration with AGI server
- ✅ All service modules implemented and tested

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment instructions!**

## Demo

```
☎️  Caller dials your number
    ↓
🎵  "Welcome to Meow Now! Press 1 for meow mockery, 2 for talkative cats"
    ↓
1️⃣  Option 1: Meow Mockery
    - Caller talks for up to 60 seconds
    - System analyzes pitch and rhythm
    - Plays back REALISTIC cat meows matching their voice (not robotic!)
    - Uses advanced waveform synthesis with harmonics
    - Automatic hangup after playback
    ↓
2️⃣  Option 2: Talkative Cats
    - System picks random cat personality
    - Cat delivers 15-second monologue (via Ollama LLM or pre-written)
    - Grumpy cat complains about delayed dinner
    - Wise cat shares philosophical insights
    - Anxious cat panics about the vacuum
    - Diva cat demands proper admiration
    - Automatic hangup
```

## Architecture

```
NumberBarn Phone Number (SIP Trunk)
          ↓
   Asterisk (Docker Container)
          ↓
   Python Flask App (AGI Server)
          ↓
   ├─ Voice Analyzer (pitch/rhythm detection)
   ├─ Meow Synthesizer (real-time generation)
   ├─ Cat Personalities (Ollama LLM)
   └─ Local TTS (Piper/Coqui)
```

## Prerequisites

- **Unraid server** (or any Docker host)
- **Phone number** with [NumberBarn](https://www.numberbarn.com/) (~$2-5/month)
- **Static IP or DDNS** for your home network
- **Port forwarding** on your router (5060 UDP, 10000-10099 UDP)
- **(Optional)** Ollama running on local network/Tailscale

## Quick Start

### Test Locally First (No Phone Required!)

Try it on your laptop using your microphone:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start test interface
python test_interface.py

# 3. Open browser
# Go to: http://localhost:5001

# 4. Click "Start Call" and test!
```

See [TESTING.md](TESTING.md) for complete local testing guide.

### Deploy to Production

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

```bash
# 1. Clone repository
git clone [this-repo-url]
cd meow-now

# 2. Configure
cp .env.example .env
nano .env  # Add your Ollama URL if using

# 3. Deploy with Docker
docker-compose up -d

# 4. Configure NumberBarn
# Set call forwarding to: sip:YOUR_IP:5060

# 5. Call your number!
```

## Documentation

- **[TESTING.md](TESTING.md)** - Test locally with your laptop microphone (start here!)
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 15 minutes
- **[docs/SETUP.md](docs/SETUP.md)** - Complete setup guide with troubleshooting
- **[docs/NUMBERBARN.md](docs/NUMBERBARN.md)** - NumberBarn SIP configuration
- **[CHECKLIST.md](CHECKLIST.md)** - Setup verification checklist
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design

## Project Structure

```
meow-now/
├── app.py                      # Main Flask application
├── agi_server.py              # AGI server for Asterisk integration
├── config/
│   ├── asterisk/              # Asterisk dialplan configurations
│   └── settings.py            # Application settings
├── services/
│   ├── ivr.py                 # IVR call tree logic
│   ├── voice_analyzer.py      # Pitch/rhythm detection
│   ├── meow_generator.py      # Meow synthesis engine
│   └── cat_personalities.py   # Cat character definitions
├── audio/
│   ├── prompts/               # IVR menu prompts
│   └── cats/                  # Pre-generated cat audio
├── models/                    # Local TTS models
├── docs/                      # Setup documentation
└── requirements.txt
```

## Cat Personalities

The system includes 4 unique cat personalities:

### 1. Grumpy Cat 😾
- **Personality**: Perpetually annoyed, sarcastic, complaining
- **Voice**: Lower pitch, slower speaking rate
- **Topics**: Delayed dinner, uncomfortable furniture, noisy neighbors
- **Example**: "Dinner is THREE MINUTES LATE. Do you have any idea how unacceptable this is?"

### 2. Wise Cat 🧘‍♂️
- **Personality**: Philosophical, zen master, calm and patient
- **Voice**: Slightly lower pitch, contemplative pace
- **Topics**: Perfect napping, philosophy of the red dot, patience in hunting
- **Example**: "The red dot teaches us profound truths. We chase, yet never catch. Embrace the chase itself."

### 3. Anxious Cat 😰
- **Personality**: Nervous, worried, catastrophizing everything
- **Voice**: Higher pitch, faster speaking rate
- **Topics**: Suspicious sounds, vacuum cleaner fears, routine changes
- **Example**: "Oh no oh NO! The vacuum! It's in the closet! What if today's the day?!"

### 4. Diva Cat 💅
- **Personality**: Dramatic, demanding royal treatment, theatrical
- **Voice**: Higher pitch, dramatic delivery
- **Topics**: Proper admiration, tuna presentation standards, being fabulous
- **Example**: "Darling, I'm STUNNING. You can't just glance and move on. I deserve better!"

## Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Ollama Integration (optional)
OLLAMA_URL=http://your-tailscale-host:11434

# Audio Settings
SAMPLE_RATE=8000
MAX_RECORDING_DURATION=60
CAT_MONOLOGUE_DURATION=15

# TTS Engine
TTS_ENGINE=piper  # Options: piper, coqui

# Cat Personalities (enable/disable)
ENABLE_GRUMPY_CAT=True
ENABLE_WISE_CAT=True
ENABLE_ANXIOUS_CAT=True
ENABLE_DIVA_CAT=True

# Voice Analysis
PITCH_DETECTION_METHOD=praat  # Options: praat, aubio
MEOW_BASE_PITCH=300
MEOW_PITCH_VARIANCE=0.3
```

See [docs/SETUP.md](docs/SETUP.md) for complete configuration reference.

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up -d
```

Includes both Meow-Now app and Asterisk in containers.

### Option 2: Unraid Community App

1. Add container via Unraid Docker UI
2. Configure port mappings and volumes
3. Start container

### Option 3: Standalone Python

```bash
pip install -r requirements.txt
python app.py
```

Requires separate Asterisk installation.

## Development

### Project Structure

```
meow-now/
├── app.py                      # Flask web interface & startup
├── agi_server.py              # AGI server for Asterisk integration
├── config/
│   ├── asterisk/              # Asterisk configurations
│   │   ├── extensions.conf    # Dialplan routing
│   │   ├── sip.conf          # SIP trunk config
│   │   └── manager.conf      # AMI configuration
│   └── settings.py            # Application settings
├── services/
│   ├── ivr.py                 # IVR call tree logic
│   ├── voice_analyzer.py      # Pitch/rhythm detection
│   ├── meow_generator.py      # Meow synthesis engine
│   └── cat_personalities.py   # Cat character definitions
├── scripts/
│   └── generate_audio_prompts.py  # TTS audio generator
├── audio/
│   ├── prompts/               # IVR menu audio files
│   ├── cats/                  # Pre-generated cat audio
│   ├── recordings/            # Caller recordings (temp)
│   └── generated/             # Generated meows (temp)
├── models/
│   ├── piper/                 # Piper TTS models
│   └── coqui/                 # Coqui TTS models
├── docs/
│   ├── SETUP.md              # Complete setup guide
│   └── NUMBERBARN.md         # NumberBarn configuration
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Multi-container setup
├── requirements.txt           # Python dependencies
└── .env.example              # Configuration template
```

### Adding New Cat Personalities

1. Edit `services/cat_personalities.py`
2. Create new class inheriting from `CatPersonality`
3. Define personality traits, topics, and fallback monologues
4. Add to `CAT_REGISTRY`
5. Enable in `.env`: `ENABLE_YOUR_CAT=True`

Example:
```python
class SassyCat(CatPersonality):
    def __init__(self):
        super().__init__(
            name="Sassy",
            voice_pitch=1.05,
            speaking_rate=1.1,
            personality_prompt="You are a sassy, witty cat...",
            topics=["topic1", "topic2"]
        )
```

### Running Tests

```bash
# Test AGI server
python -m pytest tests/test_agi.py

# Test voice analyzer
python -m pytest tests/test_voice.py

# Test meow generator
python -m pytest tests/test_meow.py
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| No incoming calls | Check port forwarding and SIP registration |
| One-way audio | Forward RTP ports 10000-10099 UDP |
| Meow mockery silent | Check recording directory permissions |
| Cats not talking | Verify Piper model exists, check TTS logs |
| Ollama not connecting | Test connection, verify Tailscale network |

See [docs/SETUP.md](docs/SETUP.md) for detailed troubleshooting.

## Performance

**Tested on**:
- Unraid server (i5-8400, 16GB RAM)
- Concurrent calls: 5+ simultaneous
- CPU usage: ~10-15% per call
- RAM usage: ~200MB base + 50MB per call

**Optimizations**:
- Use Piper TTS (lighter than Coqui)
- Disable Ollama for static responses
- Adjust pitch detection sensitivity

## Security

- Change default passwords in `config/asterisk/manager.conf`
- Don't expose Flask port (5000) to internet
- Use strong SIP passwords
- Enable fail2ban for SIP brute force protection
- Consider VPN for administrative access

## Contributing

Contributions welcome! Ideas:
- Additional cat personalities
- Multi-language support
- Web dashboard for call analytics
- SMS notifications when calls received
- Integration with other LLM providers
- Voice effects and filters

## Roadmap

- [ ] Web dashboard for monitoring calls
- [ ] Call recording and playback
- [ ] Multi-language IVR menus
- [ ] Integration with GPT-4 for cat responses
- [ ] Voice cloning for custom cat voices
- [ ] SMS/email notifications
- [ ] Analytics and call statistics

## Credits

Built with:
- [Asterisk](https://www.asterisk.org/) - Open-source PBX
- [Piper TTS](https://github.com/rhasspy/piper) - Fast, local TTS
- [Parselmouth](https://parselmouth.readthedocs.io/) - Praat voice analysis
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Ollama](https://ollama.ai/) - Local LLM runtime

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/meow-now/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/meow-now/discussions)
- **Documentation**: [docs/](docs/)

---

Made with ❤️ and 😺 by cat enthusiasts, for cat enthusiasts.

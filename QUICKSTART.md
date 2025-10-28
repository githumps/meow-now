# Meow-Now Quick Start Guide

Get up and running in 15 minutes!

## TL;DR

```bash
# 1. Clone and configure
git clone https://github.com/yourusername/meow-now.git
cd meow-now
cp .env.example .env
nano .env  # Edit configuration

# 2. Start services
docker-compose up -d

# 3. Configure NumberBarn to forward to your IP
# SIP URI: sip:YOUR_EXTERNAL_IP:5060

# 4. Call your number and enjoy cats!
```

## Prerequisites Checklist

- [ ] Unraid server (or any Docker host)
- [ ] Phone number with NumberBarn
- [ ] Static IP or DDNS setup
- [ ] Ports 5060 and 10000-10099 forwarded
- [ ] (Optional) Ollama running for dynamic cats

## Step-by-Step Setup

### 1. Deploy on Unraid

**Option A: Docker Compose (Recommended)**

```bash
# SSH into Unraid
cd /mnt/user/appdata
git clone [repository-url] meow-now
cd meow-now

# Configure
cp .env.example .env
nano .env
```

Edit these key values:
```bash
OLLAMA_URL=http://your-ollama-host:11434  # Optional
```

Start services:
```bash
docker-compose up -d
```

**Option B: Unraid UI**

1. Apps → Docker → Add Container
2. Name: `meow-now`
3. Repository: Build from Dockerfile or use pre-built image
4. Add port mappings: 5000:5000, 4573:4573
5. Add volume mappings for /app/audio, /app/logs, /app/models
6. Start container

### 2. Configure Network

**Get Your Public IP**:
```bash
curl ifconfig.me
```

**Set Up DDNS** (if IP changes):
- Sign up at [DuckDNS](https://www.duckdns.org/)
- Create subdomain: `mymeow.duckdns.org`
- Update Unraid with DuckDNS client

**Port Forward** (on your router):
```
5060 UDP → Unraid IP
10000-10099 UDP → Unraid IP
```

### 3. Configure NumberBarn

1. Log into NumberBarn
2. Go to your phone number settings
3. Set Call Forwarding to: `sip:YOUR_IP:5060`
   - Or: `sip:mymeow.duckdns.org:5060`
4. Save and test

**Alternative: SIP Registration**
If NumberBarn gives you SIP credentials:

Edit `config/asterisk/sip.conf`:
```ini
[numberbarn-trunk]
username=YOUR_USERNAME
secret=YOUR_PASSWORD
register => YOUR_USERNAME:YOUR_PASSWORD@sip.numberbarn.com/YOUR_NUMBER
```

Restart Asterisk:
```bash
docker-compose restart asterisk
```

### 4. Generate Audio Prompts

**Option A: Use Piper TTS** (Included in Docker)

```bash
# Download Piper model first (if not in Docker)
docker exec -it meow-now python scripts/generate_audio_prompts.py
```

**Option B: Manual Creation**

Create these files in `audio/prompts/` (8kHz, mono WAV):
- `welcome.wav` - "Welcome to Meow Now!"
- `main_menu.wav` - "Press 1 for meow mockery, 2 for talkative cats"
- `meow_instructions.wav` - "Start talking after beep..."
- `meow_goodbye.wav` - "Thanks for calling!"
- `cats_intro.wav` - "Connecting to a cat..."
- `goodbye.wav` - "Goodbye!"
- `error.wav` - "Error occurred"

### 5. Test Your System

**Test 1: Web Interface**
```bash
# Visit in browser
http://UNRAID_IP:5000
```

Should show green "Running" status.

**Test 2: Health Check**
```bash
curl http://UNRAID_IP:5000/health
```

**Test 3: Asterisk Status**
```bash
docker exec -it meow-asterisk asterisk -rvvv
CLI> sip show registry  # Should show "Registered"
CLI> sip show peers     # Should show NumberBarn peer
```

**Test 4: Make a Call**

Call your NumberBarn number from your phone:
1. Hear welcome message
2. Press 1 → Meow mockery (talk, then hear meows back)
3. Press 2 → Talkative cat (hear a cat monologue)

### 6. Enable Ollama (Optional)

For dynamic cat personalities with LLM:

**On Ollama Machine**:
```bash
ollama pull llama2
# Or: ollama pull llama3
```

**In Meow-Now `.env`**:
```bash
OLLAMA_URL=http://ollama-tailscale-hostname:11434
```

**Test Connection**:
```bash
docker exec -it meow-now curl http://ollama-host:11434/api/tags
```

Restart:
```bash
docker-compose restart meow-now
```

## Troubleshooting

### Can't receive calls?

```bash
# Check SIP registration
docker exec -it meow-asterisk asterisk -rx "sip show registry"

# Check ports
netstat -tulpn | grep 5060

# Test from external network
nmap -sU -p 5060 YOUR_EXTERNAL_IP
```

### No audio on calls?

```bash
# Check RTP ports
netstat -tulpn | grep -E "1000[0-9]"

# Verify NAT settings in config/asterisk/sip.conf
```

### Meow mockery not working?

```bash
# Check logs
tail -f logs/meow-now.log | grep voice_analyzer

# Verify recording permissions
ls -la audio/recordings/
```

### Cats not talking?

```bash
# Check TTS
docker exec -it meow-now piper --version

# Check Ollama connection (if using)
docker exec -it meow-now curl $OLLAMA_URL/api/tags

# Check audio files
ls -la audio/cats/
```

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "No route to destination" | Check port forwarding |
| "One-way audio" | Forward RTP ports 10000-10099 |
| "Registration failed" | Check SIP credentials in sip.conf |
| "Call goes to voicemail" | Verify NumberBarn forwarding is active |
| "TTS not working" | Check Piper model in models/piper/ |

## Next Steps

✅ **System is running!**

Now you can:

1. **Customize Cat Personalities**
   - Edit `services/cat_personalities.py`
   - Add new cats with unique voices

2. **Create Custom Audio**
   - Record professional prompts
   - Add background music
   - Create themed variations

3. **Monitor Calls**
   - Check logs: `tail -f logs/meow-now.log`
   - View Asterisk: `docker logs -f meow-asterisk`

4. **Tune Performance**
   - Adjust pitch detection sensitivity
   - Tweak meow generation parameters
   - Optimize for your server

5. **Add Features**
   - Multiple menu options
   - Call recording
   - Analytics dashboard
   - SMS notifications

## Configuration Reference

### Audio Quality

```bash
# .env
SAMPLE_RATE=8000        # Telephony standard
MAX_RECORDING_DURATION=60
CAT_MONOLOGUE_DURATION=15
```

### Meow Generation

```bash
MEOW_BASE_PITCH=300     # Hz
MEOW_PITCH_VARIANCE=0.3 # 30% variation
```

### Cat Personalities

```bash
ENABLE_GRUMPY_CAT=True
ENABLE_WISE_CAT=True
ENABLE_ANXIOUS_CAT=True
ENABLE_DIVA_CAT=True
```

## Resources

- **Full Documentation**: See `docs/SETUP.md`
- **NumberBarn Guide**: See `docs/NUMBERBARN.md`
- **GitHub Issues**: Report bugs/request features
- **Asterisk Docs**: https://wiki.asterisk.org/

## Support

Having issues? Try these:

1. **Check Logs**
   ```bash
   tail -f logs/meow-now.log
   docker logs meow-now
   docker logs meow-asterisk
   ```

2. **Enable Debug Mode**
   ```bash
   # .env
   LOG_LEVEL=DEBUG

   # Restart
   docker-compose restart
   ```

3. **Test Components**
   ```bash
   # Test AGI
   telnet localhost 4573

   # Test Asterisk
   docker exec -it meow-asterisk asterisk -rvvv
   ```

4. **Review Configuration**
   ```bash
   # Check settings
   curl http://localhost:5000/config
   ```

## Security Notes

🔒 **Important**:
- Change default passwords in `manager.conf`
- Don't expose port 5000 to internet
- Use strong SIP passwords
- Consider VPN for admin access
- Keep system updated

## Performance Tips

**For Powerful Servers**:
- Enable all cat personalities
- Use Coqui TTS for better quality
- Connect to Ollama for dynamic responses

**For Limited Resources**:
- Use Piper TTS (lighter)
- Disable Ollama (use static responses)
- Reduce enabled cat personalities

## Have Fun!

Your cat voicemail system is now live! 🐱

Call your number and enjoy the meows!

---

Need help? Check the full docs or open an issue on GitHub.

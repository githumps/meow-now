# Meow-Now Setup Checklist

Use this checklist to ensure you've completed all setup steps.

## Pre-Deployment

### Hardware & Network
- [ ] Unraid server (or Docker host) is running
- [ ] Server has adequate resources (4GB+ RAM, 2+ CPU cores)
- [ ] Network has stable internet connection
- [ ] Router admin access available

### Accounts & Services
- [ ] NumberBarn account created
- [ ] Phone number purchased/active on NumberBarn
- [ ] (Optional) DDNS service account (DuckDNS, No-IP, etc.)
- [ ] (Optional) Ollama installed and running
- [ ] (Optional) Tailscale set up (if using remote Ollama)

### Network Configuration
- [ ] Public IP address identified (`curl ifconfig.me`)
- [ ] DDNS hostname configured (if using dynamic IP)
- [ ] Port forwarding rules created on router:
  - [ ] 5060 UDP → Unraid IP (SIP signaling)
  - [ ] 10000-10099 UDP → Unraid IP (RTP audio)
- [ ] Firewall rules allow inbound on above ports
- [ ] Router's SIP ALG disabled (if present)

## Application Deployment

### Docker Setup
- [ ] Repository cloned to `/mnt/user/appdata/meow-now` (or similar)
- [ ] `.env` file created from `.env.example`
- [ ] `.env` configured with correct values:
  - [ ] OLLAMA_URL (if using)
  - [ ] TTS_ENGINE selected
  - [ ] Cat personalities enabled/disabled
  - [ ] Sample rate and audio settings verified
- [ ] Directories created (audio/, logs/, models/)
- [ ] Docker Compose installed
- [ ] Containers built: `docker-compose build`
- [ ] Containers started: `docker-compose up -d`
- [ ] Containers running: `docker ps` shows meow-now and asterisk

### Asterisk Configuration
- [ ] `config/asterisk/sip.conf` edited:
  - [ ] External IP or DDNS hostname set
  - [ ] Local network configured
  - [ ] NumberBarn credentials added
  - [ ] SIP registration line configured
- [ ] `config/asterisk/extensions.conf` edited:
  - [ ] DID number (your phone number) added
  - [ ] Context routing verified
- [ ] `config/asterisk/manager.conf` password changed
- [ ] Asterisk container restarted: `docker-compose restart asterisk`
- [ ] SIP registration successful: `docker exec -it meow-asterisk asterisk -rx "sip show registry"`

### Audio Files
- [ ] Piper TTS model downloaded to `models/piper/`
  - [ ] `en_US-lessac-medium.onnx`
  - [ ] `en_US-lessac-medium.onnx.json`
- [ ] Audio prompts generated or created:
  - [ ] `audio/prompts/welcome.wav`
  - [ ] `audio/prompts/main_menu.wav`
  - [ ] `audio/prompts/meow_instructions.wav`
  - [ ] `audio/prompts/meow_goodbye.wav`
  - [ ] `audio/prompts/cats_intro.wav`
  - [ ] `audio/prompts/goodbye.wav`
  - [ ] `audio/prompts/error.wav`
- [ ] Audio files are 8kHz, mono, WAV format
- [ ] Audio files tested (playable)

### Ollama Integration (Optional)
- [ ] Ollama server accessible from Meow-Now container
- [ ] Connection tested: `docker exec -it meow-now curl $OLLAMA_URL/api/tags`
- [ ] LLM model pulled on Ollama machine: `ollama pull llama2`
- [ ] OLLAMA_URL set in `.env`

## NumberBarn Configuration

### SIP Trunk Setup
- [ ] NumberBarn account logged in
- [ ] Phone number selected
- [ ] Call forwarding configured:
  - [ ] Forward type: SIP URI
  - [ ] SIP URI: `sip:YOUR_IP:5060` or `sip:yourname.ddns.org:5060`
  - [ ] Forwarding enabled
- [ ] (Alternative) SIP credentials obtained from NumberBarn
- [ ] Test call placed to verify forwarding

## Testing

### Basic Connectivity
- [ ] Web interface accessible: `http://UNRAID_IP:5000`
- [ ] Status page shows "Running"
- [ ] Health check returns 200: `curl http://UNRAID_IP:5000/health`
- [ ] Logs show no errors: `tail -f logs/meow-now.log`

### Asterisk Testing
- [ ] Asterisk CLI accessible: `docker exec -it meow-asterisk asterisk -rvvv`
- [ ] SIP registration shows "Registered": `sip show registry`
- [ ] SIP peers visible: `sip show peers`
- [ ] No error messages in Asterisk log

### External Network Testing
- [ ] Port 5060 open from external network: `nmap -sU -p 5060 YOUR_EXTERNAL_IP`
- [ ] RTP ports open: `nmap -sU -p 10000-10010 YOUR_EXTERNAL_IP`
- [ ] Test call from mobile phone (on cellular data, not WiFi)

### Call Flow Testing
- [ ] Call reaches Asterisk (visible in Asterisk CLI)
- [ ] Welcome message plays
- [ ] DTMF tones (key presses) detected
- [ ] Option 1 (Meow Mockery) works:
  - [ ] Recording starts after beep
  - [ ] Can record voice
  - [ ] Meow playback occurs
  - [ ] Call hangs up after meows
- [ ] Option 2 (Talkative Cats) works:
  - [ ] Cat intro plays
  - [ ] Cat monologue plays (15 seconds)
  - [ ] Call hangs up automatically

### Audio Quality
- [ ] Audio is clear (not choppy or robotic)
- [ ] Volume is appropriate
- [ ] No echo or feedback
- [ ] DTMF tones recognized correctly

### Advanced Features
- [ ] Ollama generating dynamic responses (if enabled)
- [ ] Multiple cat personalities available
- [ ] Pitch detection working (logs show detected pitch)
- [ ] Meow synthesis matches caller voice

## Post-Deployment

### Monitoring
- [ ] Bookmark web interface: `http://UNRAID_IP:5000`
- [ ] Set up log rotation (if needed)
- [ ] Configure monitoring/alerts (optional)
- [ ] Test call once per day for first week

### Security
- [ ] Changed default AMI password in `manager.conf`
- [ ] Flask SECRET_KEY is not default value
- [ ] Port 5000 NOT exposed to internet
- [ ] Strong SIP passwords in use
- [ ] fail2ban configured (optional but recommended)

### Optimization
- [ ] CPU usage acceptable during calls
- [ ] RAM usage stable
- [ ] No disk space issues
- [ ] Audio latency acceptable

### Documentation
- [ ] Saved configuration backup
- [ ] Documented any custom changes
- [ ] Noted your specific setup (IP, DID, etc.)

## Maintenance Tasks

### Weekly
- [ ] Check logs for errors: `tail logs/meow-now.log`
- [ ] Verify SIP registration: `sip show registry`
- [ ] Test call to ensure system working

### Monthly
- [ ] Review call logs
- [ ] Check disk space: `df -h`
- [ ] Clean up old recordings: `rm audio/recordings/*`
- [ ] Clean up old generated meows: `rm audio/generated/*`

### Quarterly
- [ ] Update Docker images: `docker-compose pull && docker-compose up -d`
- [ ] Update Python packages: `docker exec meow-now pip install -U -r requirements.txt`
- [ ] Review and update cat personalities
- [ ] Backup configuration files

## Troubleshooting Reference

If issues occur, check:

1. **Logs**:
   - Application: `tail -f logs/meow-now.log`
   - Docker: `docker logs meow-now`
   - Asterisk: `docker exec -it meow-asterisk tail -f /var/log/asterisk/full`

2. **Status**:
   - Containers: `docker ps`
   - Health: `curl http://localhost:5000/health`
   - SIP: `docker exec -it meow-asterisk asterisk -rx "sip show registry"`

3. **Network**:
   - Ports: `netstat -tulpn | grep -E "(5060|1000[0-9])"`
   - External: `nmap -sU -p 5060 YOUR_EXTERNAL_IP`

4. **Resources**:
   - CPU: `top` or `htop`
   - Memory: `free -h`
   - Disk: `df -h`

## Getting Help

If stuck:

1. Review [docs/SETUP.md](docs/SETUP.md) for detailed troubleshooting
2. Check [docs/NUMBERBARN.md](docs/NUMBERBARN.md) for SIP issues
3. Enable debug logging: `LOG_LEVEL=DEBUG` in `.env`
4. Search GitHub Issues
5. Create new issue with:
   - Logs (last 50 lines)
   - Configuration (sanitized)
   - Steps to reproduce
   - Expected vs actual behavior

## Success Criteria

Your system is fully operational when:

✅ Calls from external numbers reach your system
✅ IVR menu plays and accepts input
✅ Both menu options (1 and 2) work correctly
✅ Audio quality is good
✅ System runs stably for 24+ hours
✅ No errors in logs
✅ Calls hang up properly
✅ Resources (CPU/RAM) are within acceptable limits

## Next Steps After Setup

Once everything is working:

1. **Share**: Give friends your number and watch their reactions
2. **Customize**: Add more cat personalities or modify existing ones
3. **Enhance**: Add new menu options or features
4. **Monitor**: Set up analytics to see call patterns
5. **Expand**: Use this as a base for other voice applications

---

**Congratulations!** Your Meow-Now system is ready to mock callers with cat meows! 🎉🐱

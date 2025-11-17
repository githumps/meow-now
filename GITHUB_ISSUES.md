# GitHub Issues for Meow Now Phone Tree System

This document outlines all the GitHub issues that should be created to track the implementation and launch of the Meow Now phone tree system.

## High Priority - Core Functionality

### Issue #1: Generate Realistic Cat Meow Audio Samples
**Labels:** `enhancement`, `audio`, `high-priority`
**Description:**
Implement and test realistic cat meow audio generation using the RealMeowGenerator class. The meows need to sound genuinely cat-like, not synthetic.

**Tasks:**
- [x] RealMeowGenerator class already implemented in `/services/real_meow_generator.py`
- [ ] Generate diverse meow samples (short, long, trill, chirp, yowl)
- [ ] Test audio quality and realism
- [ ] Store samples in `audio/meow_samples/` directory
- [ ] Verify pitch-shifting and time-stretching functionality
- [ ] Test meow sequence generation matching voice patterns

**Acceptance Criteria:**
- At least 5 different meow types generated
- Meows sound realistic (not robotic or synthetic)
- Pitch-shifting works correctly to match caller's voice
- Audio files are in correct format (8kHz WAV for Asterisk)

---

### Issue #2: Create IVR Audio Prompts
**Labels:** `audio`, `ivr`, `high-priority`
**Description:**
Generate or record all required IVR audio prompts for the phone tree system.

**Required Prompts:**
- [ ] `welcome.wav` - Initial greeting
- [ ] `main_menu.wav` - "Welcome to Meow-Now! Press 1 for meow mockery, press 2 for talkative cats"
- [ ] `meow_instructions.wav` - "Get ready to be mocked by a cat! Start talking after the beep. You have 60 seconds. Press pound when finished."
- [ ] `meow_goodbye.wav` - Goodbye message after meow mockery
- [ ] `cats_intro.wav` - "Connecting you to one of our talkative felines..."
- [ ] `goodbye.wav` - General goodbye message
- [ ] `error.wav` - Error message for invalid input

**Acceptance Criteria:**
- All prompts created and saved in `audio/prompts/`
- Audio format: 8kHz, mono, WAV
- Clear, professional voice quality
- Files tested with Asterisk playback

---

### Issue #3: Complete Docker Containerization
**Labels:** `docker`, `deployment`, `high-priority`
**Description:**
Finalize Docker setup for both Asterisk and Meow-Now application containers.

**Tasks:**
- [ ] Review and test Dockerfile for Meow-Now app
- [ ] Test docker-compose.yml configuration
- [ ] Verify network connectivity between containers
- [ ] Test volume mounts for audio files and logs
- [ ] Configure proper health checks
- [ ] Test AGI communication between Asterisk and Python app
- [ ] Document environment variables in .env.example

**Acceptance Criteria:**
- `docker-compose up -d` starts both containers successfully
- Containers can communicate over meow-network
- AGI server accessible from Asterisk container
- Audio files accessible in both containers
- Health checks pass

---

### Issue #4: Test End-to-End Phone Call Flow
**Labels:** `testing`, `integration`, `high-priority`
**Description:**
Test the complete phone call flow from incoming call to hangup.

**Test Scenarios:**
- [ ] Test Option 1: Meow Mockery
  - Record caller voice
  - Analyze pitch and rhythm
  - Generate matching meows
  - Play back meows
  - Verify proper hangup
- [ ] Test Option 2: Talkative Cats
  - Select random cat personality
  - Generate or play cat monologue
  - Verify proper hangup
- [ ] Test invalid input handling
- [ ] Test timeout scenarios
- [ ] Test DTMF tone detection

**Acceptance Criteria:**
- Both menu options work end-to-end
- Audio quality is acceptable
- No crashes or errors in logs
- Calls hang up properly
- DTMF tones detected correctly

---

## Medium Priority - Production Readiness

### Issue #5: Configure Asterisk SIP Trunk
**Labels:** `asterisk`, `sip`, `configuration`
**Description:**
Configure Asterisk to work with NumberBarn or other SIP provider for production deployment.

**Tasks:**
- [ ] Update `config/asterisk/sip.conf` with production settings
- [ ] Configure external IP/DDNS hostname
- [ ] Set up SIP registration with provider
- [ ] Configure RTP ports (10000-10099)
- [ ] Test SIP registration status
- [ ] Verify inbound call routing
- [ ] Test NAT traversal

**Acceptance Criteria:**
- SIP registration shows "Registered"
- Incoming calls route to AGI server
- Two-way audio works
- No audio quality issues

---

### Issue #6: Implement TTS for Audio Prompt Generation
**Labels:** `enhancement`, `tts`, `audio`
**Description:**
Implement Text-to-Speech system to automatically generate IVR prompts instead of manual recording.

**Tasks:**
- [ ] Install Piper TTS or Coqui TTS
- [ ] Create script to generate prompts from text
- [ ] Add to `scripts/generate_audio_prompts.py`
- [ ] Test voice quality and clarity
- [ ] Generate all required prompts
- [ ] Document TTS setup in README

**Acceptance Criteria:**
- TTS system installed and working
- Script can generate all prompts automatically
- Audio quality is acceptable for phone calls
- Process is documented for future updates

---

### Issue #7: Add Configuration Management
**Labels:** `enhancement`, `configuration`
**Description:**
Improve configuration management for production deployment.

**Tasks:**
- [ ] Complete `.env.example` with all variables
- [ ] Add validation for required config values
- [ ] Document all configuration options
- [ ] Create setup wizard or script
- [ ] Add configuration health check endpoint
- [ ] Validate SIP credentials format

**Acceptance Criteria:**
- All config options documented
- Missing required config triggers clear error
- Setup process is straightforward
- Configuration can be validated before deployment

---

### Issue #8: Create Deployment Documentation
**Labels:** `documentation`, `deployment`
**Description:**
Create comprehensive deployment documentation for production use.

**Tasks:**
- [ ] Document NumberBarn setup process
- [ ] Document router port forwarding
- [ ] Create step-by-step deployment guide
- [ ] Add troubleshooting section
- [ ] Document testing procedures
- [ ] Create FAQ for common issues
- [ ] Add system requirements documentation

**Acceptance Criteria:**
- Complete deployment guide exists
- Guide tested by following it step-by-step
- Common issues documented with solutions
- System requirements clearly stated

---

## Lower Priority - Enhancements

### Issue #9: Add Web Dashboard for Call Monitoring
**Labels:** `enhancement`, `web-interface`
**Description:**
Enhance the Flask web interface with call monitoring and statistics.

**Tasks:**
- [ ] Add call history tracking
- [ ] Display recent calls with metadata
- [ ] Show system status and health
- [ ] Add call statistics (total, by option, duration)
- [ ] Create admin configuration interface
- [ ] Add real-time call monitoring

**Acceptance Criteria:**
- Dashboard shows recent call activity
- Statistics are accurate
- Interface is user-friendly
- No impact on call handling performance

---

### Issue #10: Implement Call Recording Storage
**Labels:** `enhancement`, `storage`
**Description:**
Add optional feature to save interesting meow mockeries for later listening.

**Tasks:**
- [ ] Add configuration option for recording storage
- [ ] Implement recording retention policy
- [ ] Add playback interface
- [ ] Implement automatic cleanup
- [ ] Add privacy considerations documentation

**Acceptance Criteria:**
- Recordings can be optionally saved
- Playback interface works
- Disk space managed automatically
- Privacy implications documented

---

### Issue #11: Add Multi-Language Support
**Labels:** `enhancement`, `i18n`
**Description:**
Add support for multiple languages in IVR prompts.

**Tasks:**
- [ ] Design language selection system
- [ ] Create prompt text templates
- [ ] Generate prompts in multiple languages
- [ ] Add language configuration
- [ ] Test with non-English speakers

---

### Issue #12: Integration with More SIP Providers
**Labels:** `enhancement`, `sip`
**Description:**
Test and document setup with various SIP providers beyond NumberBarn.

**Providers to test:**
- [ ] NumberBarn (primary)
- [ ] Twilio SIP
- [ ] Vonage/Nexmo
- [ ] VoIP.ms
- [ ] Flowroute

**Acceptance Criteria:**
- Documentation for each provider
- Known limitations documented
- Configuration templates provided

---

### Issue #13: Add SMS Notifications
**Labels:** `enhancement`, `notifications`
**Description:**
Send SMS notification when someone calls the system.

**Tasks:**
- [ ] Choose SMS provider (Twilio, etc.)
- [ ] Implement notification system
- [ ] Add configuration options
- [ ] Test delivery reliability
- [ ] Document setup process

---

### Issue #14: Implement Voice Cloning for Custom Cats
**Labels:** `enhancement`, `advanced`, `audio`
**Description:**
Allow users to create custom cat personalities with voice cloning.

**Tasks:**
- [ ] Research voice cloning options
- [ ] Implement voice cloning integration
- [ ] Create voice sample recording interface
- [ ] Test quality and latency
- [ ] Document ethical considerations

---

### Issue #15: Add Analytics and Metrics
**Labels:** `enhancement`, `analytics`
**Description:**
Track detailed metrics about system usage and performance.

**Metrics to track:**
- [ ] Calls per day/week/month
- [ ] Popular menu options
- [ ] Average call duration
- [ ] Voice analysis statistics
- [ ] System performance metrics
- [ ] Error rates

**Acceptance Criteria:**
- Metrics collected automatically
- Dashboard displays key metrics
- Historical data preserved
- Export functionality available

---

## Testing & Quality

### Issue #16: Create Automated Test Suite
**Labels:** `testing`, `quality`
**Description:**
Implement automated tests for core functionality.

**Test Areas:**
- [ ] Unit tests for voice analyzer
- [ ] Unit tests for meow generator
- [ ] Unit tests for cat personalities
- [ ] Integration tests for AGI server
- [ ] Integration tests for IVR flow
- [ ] Mock Asterisk tests

**Acceptance Criteria:**
- Test coverage >80%
- Tests pass consistently
- CI/CD integration possible
- Tests run in <5 minutes

---

### Issue #17: Performance Testing and Optimization
**Labels:** `testing`, `performance`
**Description:**
Test system performance under load and optimize bottlenecks.

**Tasks:**
- [ ] Test concurrent call handling
- [ ] Measure CPU usage per call
- [ ] Measure memory usage
- [ ] Test audio processing latency
- [ ] Optimize voice analysis
- [ ] Optimize meow generation
- [ ] Document performance limits

**Acceptance Criteria:**
- System handles 5+ concurrent calls
- CPU usage <20% per call
- Memory usage <100MB per call
- Audio latency <2 seconds

---

### Issue #18: Security Audit
**Labels:** `security`, `testing`
**Description:**
Perform security audit and implement security best practices.

**Tasks:**
- [ ] Review SIP security (authentication, encryption)
- [ ] Implement rate limiting for calls
- [ ] Add fail2ban configuration
- [ ] Secure Flask endpoints
- [ ] Review environment variable handling
- [ ] Document security best practices
- [ ] Test for common vulnerabilities

**Acceptance Criteria:**
- No critical security vulnerabilities
- Best practices documented
- Rate limiting implemented
- Credentials properly protected

---

## Documentation

### Issue #19: Create Video Tutorial
**Labels:** `documentation`, `tutorial`
**Description:**
Create video walkthrough of setup and usage.

**Content:**
- [ ] Introduction and overview
- [ ] Prerequisites and requirements
- [ ] Step-by-step deployment
- [ ] Configuration walkthrough
- [ ] Testing the system
- [ ] Troubleshooting demo

---

### Issue #20: Improve Code Documentation
**Labels:** `documentation`, `code`
**Description:**
Add comprehensive code documentation and examples.

**Tasks:**
- [ ] Add docstrings to all functions
- [ ] Create architecture diagrams
- [ ] Document API endpoints
- [ ] Add inline comments for complex logic
- [ ] Create developer guide
- [ ] Document testing procedures

---

## Notes

- The system should work with free/low-cost SIP providers
- Priority is on realistic cat sounds, not synthetic
- System must be self-hosted (no cloud API costs)
- Target deployment: Docker on Unraid or similar
- Real phone number forwarding is essential for production use

---

## Issue Creation Priority

1. Issues #1-4: Must complete before launch
2. Issues #5-8: Required for production deployment
3. Issues #9-15: Post-launch enhancements
4. Issues #16-20: Ongoing quality improvements

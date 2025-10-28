# NumberBarn SIP Configuration Guide

Detailed instructions for configuring NumberBarn to work with your self-hosted Meow-Now system.

## Overview

NumberBarn supports SIP forwarding, which allows you to route calls to your own server instead of their default voicemail system. This guide covers:

1. Setting up SIP credentials
2. Configuring call forwarding
3. Network requirements
4. Testing and troubleshooting

## Prerequisites

- Active NumberBarn account with a phone number
- Static IP address or Dynamic DNS (DDNS) for your home network
- Router access for port forwarding
- Basic understanding of SIP protocol

## Step-by-Step Setup

### 1. Access NumberBarn SIP Settings

1. Log in to [NumberBarn](https://www.numberbarn.com/)
2. Click on **My Numbers**
3. Select the number you want to use
4. Navigate to **Call Settings** or **Forwarding Settings**

### 2. Enable SIP Forwarding

1. Look for **Call Forwarding** options
2. Select **Forward to SIP Address** (may be called "SIP URI" or "Custom SIP")
3. If you don't see this option:
   - Check if your plan supports SIP forwarding
   - Contact NumberBarn support to enable it

### 3. Get Your SIP Credentials

NumberBarn should provide:

```
SIP Server: sip.numberbarn.com (or similar)
Username: your_username_here
Password: your_password_here
DID: +15551234567 (your phone number)
```

**Note**: If credentials aren't visible:
- Check the **Advanced Settings** or **SIP Settings** section
- Contact NumberBarn support to generate SIP credentials

### 4. Configure Call Forwarding

Enter your server details:

**Format 1: Simple SIP URI**
```
sip:YOUR_EXTERNAL_IP:5060
```

Example:
```
sip:203.0.113.45:5060
```

**Format 2: With Username**
```
sip:asterisk@YOUR_EXTERNAL_IP:5060
```

**Format 3: Using DDNS**
```
sip:yourname.ddns.net:5060
```

### 5. Alternative: SIP Registration

If NumberBarn supports inbound registration (where your Asterisk registers to their server):

They'll provide:
- **SIP Server**: `sip.numberbarn.com`
- **Port**: `5060`
- **Username**: Your account username
- **Password**: Your account password

In this case, your Asterisk server initiates the connection to NumberBarn.

## Network Configuration

### Get Your Public IP

```bash
curl ifconfig.me
```

Or visit: https://whatismyipaddress.com/

### Dynamic DNS (Recommended for Home Use)

If your ISP changes your IP address:

**Popular DDNS Services**:
- [DuckDNS](https://www.duckdns.org/) - Free, simple
- [No-IP](https://www.noip.com/) - Free tier available
- [Dynu](https://www.dynu.com/) - Free
- [Cloudflare](https://www.cloudflare.com/) - Free (if you own domain)

**Setup Example (DuckDNS)**:

1. Create account at duckdns.org
2. Create subdomain: `mymeow.duckdns.org`
3. Install DuckDNS updater on Unraid:
   ```bash
   # Add to Unraid cron
   */5 * * * * curl "https://www.duckdns.org/update?domains=mymeow&token=YOUR_TOKEN"
   ```
4. Use `mymeow.duckdns.org` in NumberBarn forwarding

### Router Port Forwarding

Configure these forwarding rules:

**For SIP (Signaling)**:
```
External Port: 5060 UDP
Internal Port: 5060 UDP
Internal IP: <Your Unraid Server IP>
Protocol: UDP
```

**For RTP (Audio)**:
```
External Port: 10000-10099 UDP
Internal Port: 10000-10099 UDP
Internal IP: <Your Unraid Server IP>
Protocol: UDP
```

**Example on Common Routers**:

**Netgear**:
1. Advanced → Port Forwarding/Triggering
2. Add Custom Service
3. Enter details above

**TP-Link**:
1. Forwarding → Virtual Servers
2. Add New
3. Enter details above

**Asus**:
1. WAN → Virtual Server / Port Forwarding
2. Add profile
3. Enter details above

**UniFi**:
1. Settings → Routing & Firewall → Port Forwarding
2. Create New Port Forward Rule
3. Enter details above

### Firewall Configuration

If you have a firewall on Unraid:

```bash
# Allow SIP
iptables -A INPUT -p udp --dport 5060 -j ACCEPT

# Allow RTP
iptables -A INPUT -p udp --dport 10000:10099 -j ACCEPT
```

For persistent rules, add to Unraid Go file.

## Asterisk Configuration

### Method 1: NumberBarn Registers to You

If you gave NumberBarn your IP address, configure Asterisk to accept calls:

**sip.conf**:
```ini
[numberbarn-incoming]
type=friend
context=from-numberbarn
host=sip.numberbarn.com
insecure=port,invite
disallow=all
allow=ulaw
allow=alaw
nat=force_rport,comedia
```

### Method 2: You Register to NumberBarn

If NumberBarn expects you to register:

**sip.conf**:
```ini
[numberbarn-trunk]
type=friend
host=sip.numberbarn.com
fromdomain=sip.numberbarn.com
context=from-numberbarn
username=YOUR_USERNAME
secret=YOUR_PASSWORD
fromuser=YOUR_USERNAME
disallow=all
allow=ulaw
allow=alaw
insecure=port,invite
nat=force_rport,comedia

register => YOUR_USERNAME:YOUR_PASSWORD@sip.numberbarn.com/YOUR_DID
```

**Test Registration**:
```bash
asterisk -rvvv
CLI> sip show registry
```

Should show: `Registered` status.

## Testing

### Test 1: Network Connectivity

**From External Network** (use your phone's mobile data):

```bash
# Test SIP port
nmap -sU -p 5060 YOUR_EXTERNAL_IP

# Or use online tool
# https://www.yougetsignal.com/tools/open-ports/
```

### Test 2: SIP OPTIONS

Send test SIP message:

```bash
# Install sipvicious
pip install sipvicious

# Send OPTIONS
svmap YOUR_EXTERNAL_IP
```

### Test 3: Make a Test Call

1. From your mobile phone (not on your home WiFi)
2. Call your NumberBarn number
3. Should hear welcome message from Meow-Now

**Expected Flow**:
```
Your Phone → NumberBarn → Your Public IP → Router → Asterisk → AGI Server → Python App
```

### Test 4: Check Asterisk Logs

During a call:

```bash
docker exec -it meow-asterisk asterisk -rvvv

# Watch for incoming calls
# Should see:
# "NOTICE[xxxxx]: chan_sip.c: Call from '...' to extension '...' accepted"
```

## Troubleshooting

### Issue: "No route to destination"

**Symptoms**: Calls fail immediately

**Solutions**:
1. Verify port forwarding is correct
2. Check firewall isn't blocking SIP
3. Confirm external IP is correct:
   ```bash
   curl ifconfig.me
   ```
4. Test port is open:
   ```bash
   nmap -sU -p 5060 YOUR_EXTERNAL_IP
   ```

### Issue: "One-way audio"

**Symptoms**: You can't hear caller (or vice versa)

**Solutions**:
1. Check RTP ports (10000-10099) are forwarded
2. Verify NAT settings in `sip.conf`:
   ```ini
   nat=force_rport,comedia
   externip=YOUR_EXTERNAL_IP
   ```
3. Check router doesn't have SIP ALG enabled:
   - SIP ALG interferes with SIP; disable it
4. Verify codecs match:
   ```ini
   allow=ulaw
   allow=alaw
   ```

### Issue: "Registration Failed"

**Symptoms**: `sip show registry` shows "Failed" or "Timeout"

**Solutions**:
1. Double-check credentials in `sip.conf`
2. Verify NumberBarn SIP server address
3. Check if NumberBarn requires registration
4. Test DNS resolution:
   ```bash
   nslookup sip.numberbarn.com
   ```
5. Check Asterisk can reach NumberBarn:
   ```bash
   docker exec -it meow-asterisk ping -c 4 sip.numberbarn.com
   ```

### Issue: "403 Forbidden"

**Symptoms**: Calls rejected with 403 error

**Solutions**:
1. Verify SIP credentials are correct
2. Check if IP authentication is required
3. Add your IP to NumberBarn's whitelist (if supported)
4. Review `insecure` settings:
   ```ini
   insecure=port,invite
   ```

### Issue: "Call connects but goes to NumberBarn voicemail"

**Symptoms**: Your server never receives call

**Solutions**:
1. Verify call forwarding is enabled in NumberBarn
2. Check SIP URI format is correct
3. Ensure forwarding is set to "Always" not "When busy"
4. Check NumberBarn dashboard for call routing logs
5. Contact NumberBarn support to verify forwarding is active

### Issue: "Calls work internally but not externally"

**Symptoms**: Internal test extension works, external calls don't

**Solutions**:
1. Test from truly external network (mobile data, not WiFi)
2. Verify router port forwarding is active:
   ```bash
   # From external network
   nmap -sU -p 5060 YOUR_EXTERNAL_IP
   ```
3. Check if ISP blocks SIP ports:
   - Some ISPs block port 5060
   - Try alternative port (e.g., 5061) and update everywhere
4. Disable router's SIP ALG feature

## Advanced Configuration

### Using Alternative SIP Port

If port 5060 is blocked:

1. **In Asterisk** (`sip.conf`):
   ```ini
   [general]
   bindport=5061
   ```

2. **Port Forward**:
   ```
   External: 5061 UDP → Internal: 5061 UDP
   ```

3. **NumberBarn Forwarding**:
   ```
   sip:YOUR_EXTERNAL_IP:5061
   ```

### SIP TLS (Encrypted)

For secure SIP:

1. **Generate Certificate**:
   ```bash
   openssl req -new -x509 -days 365 -nodes \
     -out /etc/asterisk/keys/asterisk.pem \
     -keyout /etc/asterisk/keys/asterisk.key
   ```

2. **Configure** (`sip.conf`):
   ```ini
   [general]
   tlsenable=yes
   tlsbindaddr=0.0.0.0:5061
   tlscertfile=/etc/asterisk/keys/asterisk.pem
   tlscafile=/etc/asterisk/keys/ca.crt
   ```

3. **Forward port 5061 TCP**

4. **Update NumberBarn**:
   ```
   sips:YOUR_EXTERNAL_IP:5061
   ```

### Multiple NumberBarn Numbers

Handle multiple DIDs:

**sip.conf**:
```ini
register => USERNAME1:PASSWORD1@sip.numberbarn.com/15551111111
register => USERNAME2:PASSWORD2@sip.numberbarn.com/15552222222
```

**extensions.conf**:
```ini
[from-numberbarn]
exten => 15551111111,1,Goto(meow-menu,s,1)
exten => 15552222222,1,Goto(different-menu,s,1)
```

### Bandwidth Optimization

For limited bandwidth:

**sip.conf**:
```ini
[general]
disallow=all
allow=gsm  ; Lower bandwidth codec (compressed)
```

**Note**: Audio quality will be reduced.

## Security Best Practices

1. **Use Strong Passwords**
   - Generate random SIP passwords
   - Don't reuse passwords

2. **IP Whitelisting**
   - If NumberBarn supports it, whitelist only their IPs
   - In `sip.conf`:
     ```ini
     permit=NUMBERBARN_IP/32
     deny=0.0.0.0/0.0.0.0
     ```

3. **Fail2Ban**
   - Install Fail2Ban to block SIP attacks
   - Common on port 5060

4. **Regular Updates**
   - Keep Asterisk updated
   - Monitor security advisories

5. **Monitor Logs**
   - Watch for unauthorized calls
   - Set up alerts for unusual activity

## Getting Help from NumberBarn

If you're stuck:

**Contact Info**:
- Email: support@numberbarn.com
- Phone: Check their website for support number

**What to Provide**:
1. Your phone number (DID)
2. Description of issue
3. SIP URI you're using
4. Error messages from Asterisk logs
5. Results of connection tests

**Questions to Ask**:
- "Does my plan support SIP forwarding?"
- "What SIP server should I register to?"
- "Can you provide my SIP credentials?"
- "Is there an IP whitelist I need to be added to?"
- "What codecs do you support?"

## Alternative SIP Providers

If NumberBarn doesn't work well:

- **Twilio** - $1/month + per-minute
- **Bandwidth.com** - Developer-friendly
- **VoIP.ms** - Popular for home use
- **Flowroute** - Reliable, pay-as-you-go
- **Telnyx** - Modern API, good docs

All support SIP and work with this setup.

## Resources

- [Asterisk SIP Configuration](https://wiki.asterisk.org/wiki/display/AST/Configuring+chan_sip)
- [NumberBarn Support](https://www.numberbarn.com/support)
- [SIP Testing Tools](https://www.voip-info.org/sip-test/)
- [Port Forwarding Guide](https://portforward.com/)

## Quick Reference

**SIP Configuration Template**:
```ini
[numberbarn-trunk]
type=friend
host=sip.numberbarn.com
context=from-numberbarn
username=YOUR_USERNAME
secret=YOUR_PASSWORD
fromuser=YOUR_USERNAME
disallow=all
allow=ulaw
allow=alaw
insecure=port,invite
nat=force_rport,comedia

register => YOUR_USERNAME:YOUR_PASSWORD@sip.numberbarn.com/YOUR_PHONE_NUMBER
```

**Port Forwarding**:
```
5060 UDP (SIP)
10000-10099 UDP (RTP)
```

**Test Commands**:
```bash
# Check registration
asterisk -rx "sip show registry"

# Check peers
asterisk -rx "sip show peers"

# Test external connectivity
nmap -sU -p 5060 YOUR_EXTERNAL_IP

# View full Asterisk log
tail -f /var/log/asterisk/full
```

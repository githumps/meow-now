#!/bin/bash
# Meow Now - Deployment Script
# This script helps deploy Meow Now to production

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo "============================================================"
echo " Meow Now - Deployment Script"
echo "============================================================"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check prerequisites
log_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi
log_success "Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install it first."
    exit 1
fi
log_success "Docker Compose found: $(docker-compose --version)"

# Check if .env exists
if [ ! -f ".env" ]; then
    log_warning ".env file not found. Creating from template..."
    cp .env.example .env
    log_success "Created .env file from template"
    log_warning "Please edit .env with your configuration before deploying!"
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if audio files exist
log_info "Checking audio files..."
if [ ! -d "audio/meow_samples" ] || [ -z "$(ls -A audio/meow_samples)" ]; then
    log_warning "Meow samples not found. Generating audio files..."
    python3 scripts/setup_audio.py
    if [ $? -eq 0 ]; then
        log_success "Audio files generated successfully"
    else
        log_error "Failed to generate audio files. Please run manually: python3 scripts/setup_audio.py"
        exit 1
    fi
else
    log_success "Audio files found"
fi

# Check Asterisk configuration
log_info "Checking Asterisk configuration..."

# Check if externip is set
if grep -q "externip=YOUR.PUBLIC.IP.ADDRESS" config/asterisk/sip.conf; then
    log_error "External IP not configured in config/asterisk/sip.conf"
    log_error "Please set your public IP address or DDNS hostname"
    log_error "Get your IP with: curl ifconfig.me"
    exit 1
fi

# Check if SIP credentials are set
if grep -q "YOUR_NUMBERBARN_USERNAME" config/asterisk/sip.conf; then
    log_error "SIP credentials not configured in config/asterisk/sip.conf"
    log_error "Please configure your SIP provider credentials"
    exit 1
fi

log_success "Asterisk configuration looks good"

# Ask for deployment confirmation
echo ""
log_warning "Ready to deploy. This will:"
echo "  - Build Docker images"
echo "  - Start Asterisk and Meow Now containers"
echo "  - Expose ports 5060 and 10000-10099 for SIP/RTP"
echo "  - Expose port 5000 for web interface"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Deployment cancelled"
    exit 0
fi

# Stop existing containers
log_info "Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || true

# Build containers
log_info "Building Docker images..."
docker-compose build
if [ $? -ne 0 ]; then
    log_error "Failed to build Docker images"
    exit 1
fi
log_success "Docker images built successfully"

# Start containers
log_info "Starting containers..."
docker-compose up -d
if [ $? -ne 0 ]; then
    log_error "Failed to start containers"
    exit 1
fi

# Wait for containers to start
log_info "Waiting for containers to start..."
sleep 10

# Check container status
log_info "Checking container status..."
if ! docker ps | grep -q "meow-now"; then
    log_error "Meow Now container is not running"
    docker logs meow-now
    exit 1
fi

if ! docker ps | grep -q "meow-asterisk"; then
    log_error "Asterisk container is not running"
    docker logs meow-asterisk
    exit 1
fi

log_success "Both containers are running"

# Check web interface
log_info "Checking web interface..."
sleep 5
if curl -s http://localhost:5000/health > /dev/null; then
    log_success "Web interface is responding"
else
    log_warning "Web interface not responding yet. Check logs: docker logs meow-now"
fi

# Check SIP registration
log_info "Checking SIP registration..."
sleep 5
REGISTRATION=$(docker exec meow-asterisk asterisk -rx "sip show registry" 2>/dev/null || echo "Failed")

if echo "$REGISTRATION" | grep -q "Registered"; then
    log_success "SIP registration successful!"
    echo "$REGISTRATION" | grep -E "Host|Registered"
elif echo "$REGISTRATION" | grep -q "Failed"; then
    log_warning "SIP registration failed. Check your configuration."
    log_info "To debug: docker exec -it meow-asterisk asterisk -rvvv"
else
    log_warning "Could not determine SIP registration status"
fi

# Final summary
echo ""
echo "============================================================"
log_success "Deployment Complete!"
echo "============================================================"
echo ""
echo "📱 Service URLs:"
echo "   Web Interface: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Health Check:  http://$(hostname -I | awk '{print $1}'):5000/health"
echo ""
echo "🔍 Monitoring:"
echo "   View logs:     docker-compose logs -f"
echo "   Check status:  docker ps"
echo "   Asterisk CLI:  docker exec -it meow-asterisk asterisk -rvvv"
echo ""
echo "📞 Testing:"
echo "   1. Ensure ports 5060 and 10000-10099 UDP are forwarded"
echo "   2. Configure your SIP provider to forward to: $(curl -s ifconfig.me):5060"
echo "   3. Call your phone number!"
echo ""
echo "📋 Next Steps:"
echo "   - Configure router port forwarding if not done"
echo "   - Configure SIP provider forwarding"
echo "   - Test by calling your phone number"
echo "   - Review logs for any issues"
echo ""
echo "📚 Documentation:"
echo "   - Deployment Guide: DEPLOYMENT.md"
echo "   - Testing Guide: TESTING.md"
echo "   - Architecture: ARCHITECTURE.md"
echo ""
echo "🐱 Meow Now is ready to mock your callers!"
echo ""

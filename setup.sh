#!/bin/bash

# Meow-Now Setup Helper Script
# Automates initial setup steps

set -e

echo "======================================"
echo "   Meow-Now Setup Helper"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' || echo "0.0")
required_version="3.8"

if (( $(echo "$python_version < $required_version" | bc -l 2>/dev/null || echo "1") )); then
    echo "❌ Python 3.8+ required (found: $python_version)"
    echo "   Please install Python 3.8 or higher"
    exit 1
else
    echo "✅ Python $python_version detected"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env if not exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file to configure your settings!"
    echo "   nano .env"
else
    echo "✅ .env file already exists"
fi

# Check for FFmpeg
echo ""
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
else
    echo "⚠️  FFmpeg not found (needed for audio conversion)"
    echo ""
    echo "Install FFmpeg:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Ubuntu:  sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
fi

# Check for Piper model
echo ""
echo "Checking for Piper TTS model..."
if [ -f "models/piper/en_US-lessac-medium.onnx" ]; then
    echo "✅ Piper model found"
else
    echo "⚠️  Piper model not found"
    echo ""
    read -p "Download Piper model now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading Piper TTS model..."
        mkdir -p models/piper
        cd models/piper

        wget -q --show-progress \
            https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx

        wget -q --show-progress \
            https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

        cd ../..
        echo "✅ Piper model downloaded"
    else
        echo "⚠️  Skipped Piper model download"
        echo "   Cat personalities won't work without it"
        echo "   Download later from: https://github.com/rhasspy/piper/releases"
    fi
fi

# Summary
echo ""
echo "======================================"
echo "   Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test locally (no phone required):"
echo "   python test_interface.py"
echo "   Then open: http://localhost:5001"
echo ""
echo "2. Or start full application:"
echo "   python app.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "3. For production deployment:"
echo "   - See QUICKSTART.md for Docker setup"
echo "   - See docs/SETUP.md for complete guide"
echo ""
echo "Documentation:"
echo "  📖 TESTING.md - Local testing guide"
echo "  📖 QUICKSTART.md - Production deployment"
echo "  📖 docs/SETUP.md - Complete setup guide"
echo ""
echo "======================================"

#!/bin/bash

echo "╔═══════════════════════════════════════════════════╗"
echo "║   DVR Face Recognition System - Installation      ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Please do not run as root"
    exit 1
fi

echo "📦 Installing system dependencies..."

# Update package list
sudo apt-get update

# Install Python and build tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    git

# Install OpenCV dependencies
sudo apt-get install -y \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-thread-dev

echo "✓ System dependencies installed"
echo ""

echo "🐍 Installing Python packages..."

# Upgrade pip
python3 -m pip install --upgrade pip

# Install Python requirements
cd system
python3 -m pip install -r requirements.txt
cd ..

echo "✓ Python packages installed"
echo ""

echo "📁 Creating directories..."

# Create necessary directories
mkdir -p data/images
mkdir -p config

echo "✓ Directories created"
echo ""

echo "🗄️  Initializing database..."

# Initialize database
python3 -c "import sys; sys.path.append('system'); from database import Database; Database('data/faces.db')"

echo "✓ Database initialized"
echo ""

echo "⚙️  Configuration..."

# Check if config exists
if [ ! -f "config/config.json" ]; then
    echo "📝 Creating default configuration..."
    cp config/config.json.example config/config.json 2>/dev/null || echo "{}" > config/config.json
fi

echo "✓ Configuration ready"
echo ""

echo "╔═══════════════════════════════════════════════════╗"
echo "║   Installation Complete! ✓                        ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit configuration:"
echo "   nano config/config.json"
echo ""
echo "2. Update DVR settings (IP, username, password)"
echo ""
echo "3. Start the system:"
echo "   ./start.sh"
echo ""
echo "4. Access web interface:"
echo "   http://localhost:5000"
echo ""
echo "📚 For more information, see README.md"
echo ""

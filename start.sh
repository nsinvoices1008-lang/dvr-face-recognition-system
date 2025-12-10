#!/bin/bash

echo "╔═══════════════════════════════════════════════════╗"
echo "║   DVR Face Recognition System - Starting          ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Check if config exists
if [ ! -f "config/config.json" ]; then
    echo "❌ Configuration file not found!"
    echo "📝 Please run ./install.sh first"
    exit 1
fi

# Check if database exists
if [ ! -f "data/faces.db" ]; then
    echo "⚠️  Database not found, creating..."
    python3 -c "import sys; sys.path.append('system'); from database import Database; Database('data/faces.db')"
fi

echo "🚀 Starting services..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $WEB_PID 2>/dev/null
    kill $FACE_PID 2>/dev/null
    echo "✓ Services stopped"
    exit 0
}

# Trap CTRL+C
trap cleanup INT TERM

# Start web interface in background
echo "🌐 Starting web interface..."
cd web
python3 app.py > ../logs/web.log 2>&1 &
WEB_PID=$!
cd ..

# Wait for web interface to start
sleep 3

# Check if web interface started successfully
if ps -p $WEB_PID > /dev/null; then
    echo "✓ Web interface started (PID: $WEB_PID)"
    echo "  Access at: http://localhost:5000"
else
    echo "❌ Failed to start web interface"
    exit 1
fi

echo ""

# Start face recognition engine
echo "🎥 Starting face recognition engine..."
cd system
python3 main.py &
FACE_PID=$!
cd ..

# Wait for face recognition to start
sleep 2

# Check if face recognition started successfully
if ps -p $FACE_PID > /dev/null; then
    echo "✓ Face recognition engine started (PID: $FACE_PID)"
else
    echo "❌ Failed to start face recognition engine"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   System Running ✓                                ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "📊 Web Dashboard: http://localhost:5000"
echo "🎥 Face Recognition: Active"
echo ""
echo "Press CTRL+C to stop all services"
echo ""

# Wait for processes
wait

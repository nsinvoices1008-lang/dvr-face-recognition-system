# Installation Guide

Complete step-by-step installation instructions for DVR Face Recognition System.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Method 1: Docker Installation (Recommended)](#method-1-docker-installation-recommended)
- [Method 2: Manual Installation](#method-2-manual-installation)
- [Method 3: Bootable USB Pendrive](#method-3-bootable-usb-pendrive)
- [Post-Installation Configuration](#post-installation-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements
- **Processing Device**: Raspberry Pi 4 (4GB+ RAM) / Mini PC / Server
- **USB Drive**: 16GB+ (for pendrive installation)
- **DVR**: CP Plus DVR with RTSP support
- **Network**: Both DVR and processing device on same network

### Software Requirements
- **Operating System**: Ubuntu 20.04+ / Debian 11+ / Raspberry Pi OS
- **Python**: 3.8 or higher
- **Docker**: 20.10+ (for Docker installation)
- **Internet Connection**: For initial setup

## Method 1: Docker Installation (Recommended)

### Step 1: Install Docker

```bash
# Update system
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Update the following values:
```env
DVR_IP=192.168.1.100          # Your DVR IP address
DVR_USERNAME=admin             # DVR username
DVR_PASSWORD=your_password     # DVR password
DVR_CHANNEL=1                  # Camera channel number
```

### Step 4: Start Services

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 5: Access Web Interface

Open browser and navigate to:
- **Local**: http://localhost:5000
- **Network**: http://YOUR_IP:5000

## Method 2: Manual Installation

### Step 1: System Dependencies

```bash
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
```

### Step 2: Clone Repository

```bash
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system
```

### Step 3: Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

### Step 4: Configure System

```bash
# Edit configuration file
nano config/config.json
```

Update DVR settings:
```json
{
  "dvr": {
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "your_password",
    "channel": 1
  }
}
```

### Step 5: Start System

```bash
chmod +x start.sh
./start.sh
```

## Method 3: Bootable USB Pendrive

### Step 1: Prepare USB Drive

**⚠️ WARNING: This will erase all data on the USB drive!**

```bash
# List available drives
lsblk

# Run setup script (replace /dev/sdX with your USB device)
sudo ./setup-pendrive.sh /dev/sdX
```

### Step 2: Configure Before First Boot

Mount the USB drive and edit configuration:

```bash
# Mount USB
sudo mount /dev/sdX2 /mnt

# Edit config
sudo nano /mnt/opt/dvr-face-recognition/config/config.json

# Unmount
sudo umount /mnt
```

### Step 3: Boot from USB

1. Insert USB drive into target device
2. Enter BIOS/UEFI (usually F2, F12, or DEL key)
3. Set USB as first boot device
4. Save and restart
5. System will auto-start on boot

## Post-Installation Configuration

### 1. DVR Connection Test

```bash
# Test RTSP connection
ffplay rtsp://username:password@DVR_IP:554/cam/realmonitor?channel=1&subtype=0

# Or use VLC media player
vlc rtsp://username:password@DVR_IP:554/cam/realmonitor?channel=1&subtype=0
```

### 2. Add First Person

1. Access web interface: http://localhost:5000
2. Navigate to "Persons" page
3. Click "Add Person"
4. Upload a clear photo of the person's face
5. Enter name and optional notes
6. Click "Add Person"

### 3. Configure Notifications (Optional)

#### Email Notifications (SendGrid)

1. Sign up for SendGrid: https://sendgrid.com
2. Create API key
3. Update config:

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "sendgrid_api_key": "SG.your_api_key",
      "from_email": "alerts@yourdomain.com",
      "to_email": "you@email.com"
    }
  }
}
```

#### Telegram Notifications

1. Create bot with @BotFather on Telegram
2. Get bot token
3. Get your chat ID (use @userinfobot)
4. Update config:

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "123456:ABC-DEF...",
      "chat_id": "123456789"
    }
  }
}
```

### 4. System Service (Auto-start on Boot)

Create systemd service:

```bash
sudo nano /etc/systemd/system/dvr-face-recognition.service
```

Add content:
```ini
[Unit]
Description=DVR Face Recognition System
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/dvr-face-recognition-system
ExecStart=/path/to/dvr-face-recognition-system/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dvr-face-recognition
sudo systemctl start dvr-face-recognition
```

## Troubleshooting

### Issue: Cannot connect to DVR

**Solution:**
1. Verify DVR IP address: `ping DVR_IP`
2. Check RTSP is enabled on DVR
3. Verify username/password
4. Check firewall: `sudo ufw allow 554`
5. Test with VLC or ffplay

### Issue: Face recognition not working

**Solution:**
1. Ensure good lighting in camera view
2. Check face is clearly visible (not too far)
3. Adjust recognition tolerance in settings
4. Verify person is added to database

### Issue: High CPU usage

**Solution:**
1. Increase `process_every_n_frames` in config
2. Reduce camera resolution on DVR
3. Use more powerful hardware

### Issue: Web interface not accessible

**Solution:**
1. Check if service is running: `docker-compose ps` or `ps aux | grep python`
2. Verify port 5000 is not in use: `sudo lsof -i :5000`
3. Check firewall: `sudo ufw allow 5000`
4. View logs: `docker-compose logs web-interface`

### Issue: Database errors

**Solution:**
```bash
# Backup existing database
cp data/faces.db data/faces.db.backup

# Reinitialize database
python3 -c "import sys; sys.path.append('system'); from database import Database; Database('data/faces.db')"
```

## Getting Help

- **GitHub Issues**: https://github.com/nsinvoices1008-lang/dvr-face-recognition-system/issues
- **Documentation**: See README.md
- **Logs**: Check `logs/` directory for error messages

## Next Steps

After successful installation:
1. Add known persons to the system
2. Test face recognition with live camera
3. Configure notifications
4. Set up automatic backups
5. Monitor system performance

---

**Need more help?** Open an issue on GitHub with:
- Your installation method
- Operating system details
- Error messages or logs
- Steps to reproduce the problem

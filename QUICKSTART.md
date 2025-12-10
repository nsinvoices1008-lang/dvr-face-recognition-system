# Quick Start Guide

Get up and running with DVR Face Recognition System in 5 minutes!

## 🚀 Fastest Way: Docker

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose
```

### 2. Clone & Configure

```bash
# Clone repository
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system

# Create environment file
cp .env.example .env

# Edit with your DVR details
nano .env
```

**Update these values:**
```env
DVR_IP=192.168.1.100        # Your DVR IP
DVR_USERNAME=admin          # DVR username
DVR_PASSWORD=admin123       # DVR password
```

### 3. Start System

```bash
docker-compose up -d
```

### 4. Access Dashboard

Open browser: **http://localhost:5000**

### 5. Add Your First Person

1. Click "Persons" in navigation
2. Click "+ Add Person"
3. Upload a clear photo
4. Enter name
5. Click "Add Person"

**Done!** The system is now monitoring your DVR feed.

---

## 📋 Manual Installation (No Docker)

### 1. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git cmake
```

### 2. Clone & Install

```bash
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system
chmod +x install.sh
./install.sh
```

### 3. Configure

```bash
nano config/config.json
```

Update DVR settings:
```json
{
  "dvr": {
    "ip": "192.168.1.100",
    "username": "admin",
    "password": "admin123"
  }
}
```

### 4. Start

```bash
./start.sh
```

### 5. Access

Open: **http://localhost:5000**

---

## ⚡ Testing DVR Connection

Before starting the system, test your DVR connection:

```bash
# Using VLC (install if needed: sudo apt-get install vlc)
vlc rtsp://admin:admin123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

# Or using ffplay (install: sudo apt-get install ffmpeg)
ffplay rtsp://admin:admin123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

If you see the camera feed, your DVR is configured correctly!

---

## 🔔 Enable Notifications (Optional)

### Email (SendGrid)

1. Sign up: https://sendgrid.com
2. Create API key
3. Update config:

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "sendgrid_api_key": "SG.your_key_here",
      "from_email": "alerts@yourdomain.com",
      "to_email": "you@email.com"
    }
  }
}
```

### Telegram

1. Create bot: Message @BotFather on Telegram
2. Get bot token
3. Get chat ID: Message @userinfobot
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

---

## 🎯 Common Issues

### "Cannot connect to DVR"

✅ **Fix:**
- Verify DVR IP: `ping 192.168.1.100`
- Check RTSP is enabled on DVR
- Verify username/password
- Test with VLC/ffplay

### "No face found in image"

✅ **Fix:**
- Use a clear, front-facing photo
- Ensure good lighting
- Face should be clearly visible
- Try a different photo

### "Port 5000 already in use"

✅ **Fix:**
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process or change port in config
```

---

## 📚 Next Steps

- [Full Installation Guide](INSTALLATION.md)
- [API Documentation](API.md)
- [Configuration Options](README.md#configuration)

---

## 🆘 Need Help?

- **Issues**: https://github.com/nsinvoices1008-lang/dvr-face-recognition-system/issues
- **Discussions**: https://github.com/nsinvoices1008-lang/dvr-face-recognition-system/discussions

---

**Enjoy your automated visitor recognition system! 🎉**

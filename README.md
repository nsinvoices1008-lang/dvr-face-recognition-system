# 🎥 DVR Face Recognition System

A complete pendrive-based OS solution that extends CP Plus DVR functionality with AI-powered facial recognition, visitor tracking, and real-time notifications.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## ✨ Features

- 🔍 **Real-time Face Recognition** - Automatically identify visitors from DVR camera feed
- 📊 **Web Dashboard** - Beautiful, responsive interface to monitor and manage visitors
- 🔔 **Multi-channel Notifications** - Email, Telegram, and web notifications
- 👥 **Person Management** - Easy add/edit/delete interface for registered persons
- ❓ **Unknown Visitor Detection** - Capture and identify new visitors
- 🐳 **Docker Support** - One-command deployment
- 💾 **Non-invasive Design** - Read-only access to DVR, no system modification
- 📱 **Mobile Responsive** - Access from any device
- 🔒 **Privacy Focused** - All data stored locally

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system

# Configure DVR settings
cp .env.example .env
nano .env  # Edit with your DVR IP, username, password

# Start with Docker
docker-compose up -d

# Access web interface
open http://localhost:5000
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/nsinvoices1008-lang/dvr-face-recognition-system.git
cd dvr-face-recognition-system

# Run installation script
chmod +x install.sh
./install.sh

# Configure settings
nano config/config.json

# Start services
./start.sh

# Access web interface
open http://localhost:5000
```

### Option 3: Bootable USB Pendrive

```bash
# Prepare USB drive (16GB+ recommended)
./setup-pendrive.sh /dev/sdX  # Replace sdX with your USB device

# Boot from USB on any compatible device
# System will auto-start on boot
```

## 📋 Requirements

### Hardware
- **USB Drive**: 16GB+ (for pendrive OS)
- **Processing Device**: Raspberry Pi 4 / Mini PC / Server
- **DVR**: CP Plus DVR with RTSP support
- **Network**: DVR and processing device on same network

### Software
- Python 3.8+
- OpenCV 4.x
- Docker (optional, for containerized deployment)
- CP Plus DVR with RTSP enabled

## 🔧 Configuration

### DVR Settings (`config/config.json`)

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

### Notification Settings

**Email (SendGrid):**
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "sendgrid_api_key": "your_api_key",
      "from_email": "alerts@yourdomain.com",
      "to_email": "you@email.com"
    }
  }
}
```

**Telegram:**
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

## 📱 Web Interface

Access the web dashboard at `http://localhost:5000` or `http://YOUR_IP:5000`

### Features:
- **Dashboard** - Real-time visitor monitoring and statistics
- **Persons** - Manage registered individuals
- **Unknown Visitors** - Review and identify new faces
- **Settings** - Configure DVR and notifications
- **Live Feed** - View camera stream (optional)

## 🏗️ Architecture

```
┌──────────────┐
│  CP Plus DVR │ (Unchanged - continues normal operation)
└──────┬───────┘
       │ RTSP Stream (Read-only)
       ↓
┌──────────────────────────────────┐
│   Face Recognition System        │
│  ┌────────────────────────────┐  │
│  │  Stream Capture Module     │  │
│  └────────────┬───────────────┘  │
│               ↓                   │
│  ┌────────────────────────────┐  │
│  │  Face Recognition Engine   │  │
│  │  (OpenCV + face_recognition)│ │
│  └────────────┬───────────────┘  │
│               ↓                   │
│  ┌────────────────────────────┐  │
│  │  SQLite Database           │  │
│  └────────────┬───────────────┘  │
│               ↓                   │
│  ┌────────────────────────────┐  │
│  │  Notification System       │  │
│  │  (Email, Telegram, Web)    │  │
│  └────────────┬───────────────┘  │
│               ↓                   │
│  ┌────────────────────────────┐  │
│  │  Web Dashboard (Flask)     │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## 📚 Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Docker Guide](DOCKER.md) - Container deployment
- [API Documentation](API.md) - REST API reference
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## 🔌 API Endpoints

```
GET  /api/persons              - List all registered persons
POST /api/person               - Add new person
PUT  /api/person/:id           - Update person
DELETE /api/person/:id         - Delete person

GET  /api/visits               - Get recent visits
GET  /api/unknown              - Get unknown visitors
POST /api/unknown/:id/identify - Identify unknown visitor

GET  /api/config               - Get configuration
POST /api/config               - Update configuration
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- face_recognition library by Adam Geitgey
- Flask for web framework
- CP Plus for DVR hardware

## 📞 Support

For issues and questions:
- Open an [Issue](https://github.com/nsinvoices1008-lang/dvr-face-recognition-system/issues)
- Check [Documentation](INSTALLATION.md)

## ⚠️ Important Notes

- This system is **non-invasive** - it only reads RTSP stream from DVR
- DVR continues normal operation independently
- All face data stored locally for privacy
- Requires network access between DVR and processing device
- First-time setup requires adding known faces to database

## 🎯 Roadmap

- [ ] Mobile app (iOS/Android)
- [ ] Multi-camera support
- [ ] Advanced analytics dashboard
- [ ] Cloud backup option
- [ ] Integration with access control systems
- [ ] Face mask detection
- [ ] Age/gender estimation

---

**Made with ❤️ for enhanced security and visitor management**

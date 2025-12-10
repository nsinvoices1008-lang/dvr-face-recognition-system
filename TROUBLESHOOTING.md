# Troubleshooting Guide

Common issues and solutions for DVR Face Recognition System.

## Table of Contents
- [DVR Connection Issues](#dvr-connection-issues)
- [Face Recognition Problems](#face-recognition-problems)
- [Web Interface Issues](#web-interface-issues)
- [Performance Issues](#performance-issues)
- [Notification Problems](#notification-problems)
- [Database Errors](#database-errors)
- [Docker Issues](#docker-issues)

---

## DVR Connection Issues

### ❌ "Cannot connect to DVR" or "Failed to read frame"

**Symptoms:**
- System cannot connect to DVR
- No video feed
- Connection timeout errors

**Solutions:**

1. **Verify DVR is online:**
```bash
ping 192.168.1.100  # Replace with your DVR IP
```

2. **Test RTSP stream:**
```bash
# Using VLC
vlc rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

# Using ffplay
ffplay rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

3. **Check DVR settings:**
- Ensure RTSP is enabled on DVR
- Verify port 554 is open
- Check username and password
- Confirm channel number is correct

4. **Check firewall:**
```bash
# Allow RTSP port
sudo ufw allow 554
```

5. **Verify network connectivity:**
```bash
# Check if both devices are on same network
ip addr show
```

### ❌ "Connection keeps dropping"

**Solutions:**

1. **Check network stability:**
```bash
# Continuous ping test
ping -c 100 192.168.1.100
```

2. **Reduce stream quality:**
- Use subtype=1 (sub stream) instead of subtype=0 (main stream)
- Lower resolution on DVR settings

3. **Increase reconnection timeout:**
Edit `system/dvr_connector.py`:
```python
self.max_reconnect_attempts = 10  # Increase from 5
```

---

## Face Recognition Problems

### ❌ "No face found in image"

**Symptoms:**
- Cannot add person to database
- Error when uploading photo

**Solutions:**

1. **Use better quality photos:**
- Front-facing, clear photo
- Good lighting
- Face clearly visible
- No sunglasses or masks
- Minimum 200x200 pixels

2. **Check image format:**
- Supported: JPG, JPEG, PNG
- Avoid: GIF, BMP, WEBP

3. **Test face detection:**
```python
import face_recognition
image = face_recognition.load_image_file("photo.jpg")
faces = face_recognition.face_locations(image)
print(f"Found {len(faces)} faces")
```

### ❌ "Person not being recognized"

**Symptoms:**
- Known person shows as "Unknown"
- Low confidence scores
- Inconsistent recognition

**Solutions:**

1. **Adjust recognition tolerance:**
```json
{
  "recognition": {
    "tolerance": 0.7  // Increase from 0.6 for more lenient matching
  }
}
```

2. **Add multiple photos:**
- Add same person with different angles
- Different lighting conditions
- Various expressions

3. **Improve camera conditions:**
- Better lighting
- Reduce camera distance
- Clean camera lens
- Adjust camera angle

4. **Check face quality in database:**
```bash
# View person details
curl http://localhost:5000/api/person/1
```

### ❌ "False positives (wrong person identified)"

**Solutions:**

1. **Decrease tolerance:**
```json
{
  "recognition": {
    "tolerance": 0.5  // Decrease from 0.6 for stricter matching
  }
}
```

2. **Use better quality enrollment photos**

3. **Remove duplicate or similar-looking persons**

---

## Web Interface Issues

### ❌ "Cannot access web interface"

**Symptoms:**
- Browser shows "Connection refused"
- Page not loading
- Timeout errors

**Solutions:**

1. **Check if web server is running:**
```bash
# For Docker
docker-compose ps

# For manual installation
ps aux | grep "python.*app.py"
```

2. **Verify port 5000 is available:**
```bash
sudo lsof -i :5000
```

3. **Check firewall:**
```bash
sudo ufw allow 5000
```

4. **Try different port:**
Edit `web/app.py`:
```python
app.run(host='0.0.0.0', port=8080)  # Change from 5000
```

5. **Check logs:**
```bash
# Docker
docker-compose logs web-interface

# Manual
tail -f logs/web.log
```

### ❌ "Images not loading"

**Solutions:**

1. **Check image directory permissions:**
```bash
chmod -R 755 data/images
```

2. **Verify images exist:**
```bash
ls -la data/images/
```

3. **Check browser console for errors:**
- Press F12 in browser
- Look for 404 errors

---

## Performance Issues

### ❌ "High CPU usage"

**Symptoms:**
- System slow or unresponsive
- CPU at 100%
- Overheating

**Solutions:**

1. **Reduce processing frequency:**
```json
{
  "recognition": {
    "process_every_n_frames": 12  // Increase from 6
  }
}
```

2. **Use lower resolution stream:**
- Change DVR to sub stream (subtype=1)
- Reduce camera resolution

3. **Limit concurrent processes:**
```bash
# Check CPU usage
top
htop
```

4. **Upgrade hardware:**
- Use more powerful device
- Add cooling
- Increase RAM

### ❌ "Slow face recognition"

**Solutions:**

1. **Reduce image processing size:**
Edit `system/main.py`:
```python
small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)  # Reduce from 0.25
```

2. **Use GPU acceleration (if available):**
```bash
pip install opencv-python-headless
```

3. **Optimize database:**
```bash
sqlite3 data/faces.db "VACUUM;"
```

### ❌ "Memory leaks"

**Solutions:**

1. **Restart services regularly:**
```bash
# Add to crontab
0 3 * * * docker-compose restart
```

2. **Monitor memory:**
```bash
free -h
watch -n 1 free -h
```

3. **Limit image retention:**
```bash
# Delete old images (older than 30 days)
find data/images -type f -mtime +30 -delete
```

---

## Notification Problems

### ❌ "Email notifications not working"

**Solutions:**

1. **Verify SendGrid API key:**
```bash
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

2. **Check email configuration:**
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "sendgrid_api_key": "SG.valid_key_here",
      "from_email": "verified@yourdomain.com",
      "to_email": "recipient@email.com"
    }
  }
}
```

3. **Verify sender email:**
- Must be verified in SendGrid
- Check spam folder

4. **Check logs:**
```bash
grep "Email" logs/system.log
```

### ❌ "Telegram notifications not working"

**Solutions:**

1. **Verify bot token:**
```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
```

2. **Get correct chat ID:**
- Message @userinfobot on Telegram
- Use the ID provided

3. **Test bot:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

4. **Ensure bot is started:**
- Send /start to your bot on Telegram

---

## Database Errors

### ❌ "Database locked" or "Database is locked"

**Solutions:**

1. **Close other connections:**
```bash
# Find processes using database
lsof data/faces.db
```

2. **Restart system:**
```bash
docker-compose restart
# or
./start.sh
```

3. **Backup and recreate:**
```bash
cp data/faces.db data/faces.db.backup
rm data/faces.db
python3 -c "import sys; sys.path.append('system'); from database import Database; Database()"
```

### ❌ "Corrupted database"

**Solutions:**

1. **Check database integrity:**
```bash
sqlite3 data/faces.db "PRAGMA integrity_check;"
```

2. **Repair database:**
```bash
sqlite3 data/faces.db ".recover" | sqlite3 data/faces_recovered.db
mv data/faces_recovered.db data/faces.db
```

3. **Restore from backup:**
```bash
cp data/faces.db.backup data/faces.db
```

---

## Docker Issues

### ❌ "Docker container won't start"

**Solutions:**

1. **Check logs:**
```bash
docker-compose logs
```

2. **Rebuild containers:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

3. **Check disk space:**
```bash
df -h
docker system df
```

4. **Clean Docker:**
```bash
docker system prune -a
```

### ❌ "Permission denied" errors

**Solutions:**

1. **Fix file permissions:**
```bash
sudo chown -R $USER:$USER .
chmod -R 755 .
```

2. **Run with sudo:**
```bash
sudo docker-compose up -d
```

---

## General Debugging

### Enable Debug Mode

1. **For web interface:**
Edit `web/app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

2. **For face recognition:**
Edit `system/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Logs

```bash
# Docker
docker-compose logs -f

# Manual installation
tail -f logs/system.log
tail -f logs/web.log
```

### Check System Status

```bash
# Docker
docker-compose ps
docker stats

# Manual
ps aux | grep python
top
```

---

## Getting Help

If you're still experiencing issues:

1. **Check existing issues:**
   https://github.com/nsinvoices1008-lang/dvr-face-recognition-system/issues

2. **Open new issue with:**
   - Operating system and version
   - Installation method (Docker/Manual/USB)
   - Complete error message
   - Steps to reproduce
   - Relevant log files

3. **Provide system info:**
```bash
# System information
uname -a
python3 --version
docker --version

# Configuration (remove sensitive data)
cat config/config.json
```

---

**Still need help?** Open an issue on GitHub with detailed information about your problem.

#!/usr/bin/env python3
"""
DVR Connector Module
Handles connection to CP Plus DVR via RTSP stream
"""

import cv2
import time
from datetime import datetime

class DVRConnector:
    def __init__(self, config):
        """Initialize DVR connection"""
        self.config = config
        self.rtsp_url = self._build_rtsp_url(config)
        self.cap = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.connect()
    
    def _build_rtsp_url(self, config):
        """Build RTSP URL for CP Plus DVR"""
        username = config.get('username', 'admin')
        password = config.get('password', 'admin')
        ip = config['ip']
        port = config.get('port', 554)
        channel = config.get('channel', 1)
        subtype = config.get('subtype', 0)  # 0=main stream, 1=sub stream
        
        # CP Plus DVR RTSP URL format
        # Format: rtsp://username:password@ip:port/cam/realmonitor?channel=X&subtype=Y
        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype={subtype}"
        
        return rtsp_url
    
    def connect(self):
        """Connect to DVR stream"""
        print(f"📡 Connecting to DVR at {self.config['ip']}...")
        
        try:
            # Release existing connection if any
            if self.cap is not None:
                self.cap.release()
            
            # Create new connection
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Try to read a test frame
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✓ Connected to DVR successfully")
                    print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    self.reconnect_attempts = 0
                    return True
            
            print("⚠ Failed to connect to DVR")
            self.reconnect_attempts += 1
            
            if self.reconnect_attempts < self.max_reconnect_attempts:
                print(f"  Retrying in 3 seconds... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                time.sleep(3)
                return self.connect()
            else:
                print(f"❌ Failed to connect after {self.max_reconnect_attempts} attempts")
                print("\n🔍 Troubleshooting tips:")
                print("  1. Check if DVR is powered on and connected to network")
                print("  2. Verify DVR IP address is correct")
                print("  3. Ensure RTSP is enabled on DVR")
                print("  4. Check username and password")
                print("  5. Verify firewall settings allow RTSP (port 554)")
                print(f"\n📝 Current RTSP URL (password hidden):")
                safe_url = self.rtsp_url.replace(self.config.get('password', ''), '****')
                print(f"  {safe_url}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to DVR: {e}")
            return False
    
    def get_frame(self):
        """Get a single frame from DVR"""
        if not self.cap or not self.cap.isOpened():
            print("⚠ DVR connection lost, reconnecting...")
            if not self.connect():
                return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print(f"⚠ Failed to read frame at {datetime.now().strftime('%H:%M:%S')}")
                # Try to reconnect
                if not self.connect():
                    return None
                # Try reading again after reconnect
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    return None
            
            return frame
            
        except Exception as e:
            print(f"❌ Error reading frame: {e}")
            return None
    
    def get_stream_info(self):
        """Get information about the video stream"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        info = {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'codec': int(self.cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        return info
    
    def is_connected(self):
        """Check if DVR is connected"""
        return self.cap is not None and self.cap.isOpened()
    
    def release(self):
        """Release the DVR connection"""
        if self.cap:
            print("🔌 Releasing DVR connection...")
            self.cap.release()
            self.cap = None
            print("✓ DVR connection released")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.release()

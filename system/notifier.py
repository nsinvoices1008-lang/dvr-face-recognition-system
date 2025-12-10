#!/usr/bin/env python3
"""
Notification Module
Handles multi-channel notifications (Console, Email, Telegram, Web)
"""

import requests
from datetime import datetime
import json
import os

class Notifier:
    def __init__(self, config):
        """Initialize notification system"""
        self.config = config
        self.enabled = config.get('enabled', True)
        
        # Email configuration (SendGrid)
        self.email_enabled = config.get('email', {}).get('enabled', False)
        self.sendgrid_api_key = config.get('email', {}).get('sendgrid_api_key')
        self.from_email = config.get('email', {}).get('from_email')
        self.to_email = config.get('email', {}).get('to_email')
        
        # Telegram configuration
        self.telegram_enabled = config.get('telegram', {}).get('enabled', False)
        self.telegram_bot_token = config.get('telegram', {}).get('bot_token')
        self.telegram_chat_id = config.get('telegram', {}).get('chat_id')
        
        # Web notifications (stored for dashboard)
        self.web_notifications = []
        self.max_web_notifications = 100
        
        if self.enabled:
            print("✓ Notification system initialized")
            if self.email_enabled:
                print("  📧 Email notifications: Enabled")
            if self.telegram_enabled:
                print("  📱 Telegram notifications: Enabled")
    
    def send_notification(self, title, message, image_path=None, confidence=None):
        """Send notification through all enabled channels"""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format message with confidence if available
        if confidence is not None:
            full_message = f"{message} (Confidence: {confidence:.1%})"
        else:
            full_message = message
        
        # Console notification (always enabled)
        self._send_console_notification(title, full_message, timestamp)
        
        # Web notification (store for dashboard)
        self._store_web_notification(title, full_message, image_path, timestamp)
        
        # Email notification
        if self.email_enabled:
            self._send_email_notification(title, full_message, image_path)
        
        # Telegram notification
        if self.telegram_enabled:
            self._send_telegram_notification(title, full_message, image_path)
    
    def _send_console_notification(self, title, message, timestamp):
        """Print notification to console"""
        print(f"📢 [{timestamp}] {title}")
        print(f"   {message}")
    
    def _store_web_notification(self, title, message, image_path, timestamp):
        """Store notification for web dashboard"""
        notification = {
            'title': title,
            'message': message,
            'image_path': image_path,
            'timestamp': timestamp
        }
        
        self.web_notifications.insert(0, notification)
        
        # Keep only last N notifications
        if len(self.web_notifications) > self.max_web_notifications:
            self.web_notifications = self.web_notifications[:self.max_web_notifications]
        
        # Save to file for persistence
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/notifications.json', 'w') as f:
                json.dump(self.web_notifications, f, indent=2)
        except Exception as e:
            print(f"⚠ Failed to save web notifications: {e}")
    
    def _send_email_notification(self, title, message, image_path=None):
        """Send email notification via SendGrid"""
        if not self.sendgrid_api_key or not self.from_email or not self.to_email:
            return
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            # Build email content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">{title}</h2>
                <p style="font-size: 16px;">{message}</p>
                <p style="color: #666; font-size: 14px;">
                    Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
                <hr style="border: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">
                    DVR Face Recognition System
                </p>
            </body>
            </html>
            """
            
            data = {
                "personalizations": [{
                    "to": [{"email": self.to_email}],
                    "subject": f"🎥 {title}"
                }],
                "from": {"email": self.from_email},
                "content": [{
                    "type": "text/html",
                    "value": html_content
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 202:
                print(f"  ✓ Email sent successfully")
            else:
                print(f"  ⚠ Email failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Email error: {e}")
    
    def _send_telegram_notification(self, title, message, image_path=None):
        """Send Telegram notification"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return
        
        try:
            # Format message
            telegram_message = f"🎥 *{title}*\n\n{message}\n\n_Time: {datetime.now().strftime('%H:%M:%S')}_"
            
            if image_path and os.path.exists(image_path):
                # Send photo with caption
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        'chat_id': self.telegram_chat_id,
                        'caption': telegram_message,
                        'parse_mode': 'Markdown'
                    }
                    
                    response = requests.post(url, files=files, data=data)
            else:
                # Send text message only
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                
                data = {
                    'chat_id': self.telegram_chat_id,
                    'text': telegram_message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print(f"  ✓ Telegram notification sent")
            else:
                print(f"  ⚠ Telegram failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Telegram error: {e}")
    
    def get_recent_notifications(self, limit=20):
        """Get recent web notifications"""
        return self.web_notifications[:limit]
    
    def clear_notifications(self):
        """Clear all web notifications"""
        self.web_notifications = []
        try:
            if os.path.exists('data/notifications.json'):
                os.remove('data/notifications.json')
        except Exception as e:
            print(f"⚠ Failed to clear notifications: {e}")

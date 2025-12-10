#!/usr/bin/env python3
"""
DVR Face Recognition System - Main Engine
Connects to CP Plus DVR and performs real-time face recognition
"""

import cv2
import face_recognition
import numpy as np
import time
import threading
from datetime import datetime
from database import Database
from dvr_connector import DVRConnector
from notifier import Notifier
import json
import os
import sys

class FaceRecognitionSystem:
    def __init__(self, config_path='config/config.json'):
        """Initialize the face recognition system"""
        print("🚀 Initializing DVR Face Recognition System...")
        
        # Load configuration
        if not os.path.exists(config_path):
            print(f"❌ Configuration file not found: {config_path}")
            sys.exit(1)
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize components
        self.db = Database()
        self.dvr = DVRConnector(self.config['dvr'])
        self.notifier = Notifier(self.config.get('notifications', {}))
        
        # Load known faces
        self.known_faces = self.load_known_faces()
        print(f"✓ Loaded {len(self.known_faces['names'])} known faces")
        
        # System state
        self.running = False
        self.last_seen = {}  # Track last seen time to avoid duplicate notifications
        
    def load_known_faces(self):
        """Load all known faces from database"""
        persons = self.db.get_all_persons()
        known_faces = {
            'encodings': [],
            'names': [],
            'ids': []
        }
        
        for person in persons:
            try:
                encoding = np.frombuffer(person['face_encoding'], dtype=np.float64)
                known_faces['encodings'].append(encoding)
                known_faces['names'].append(person['name'])
                known_faces['ids'].append(person['id'])
            except Exception as e:
                print(f"⚠ Error loading face for {person.get('name', 'unknown')}: {e}")
        
        return known_faces
    
    def reload_known_faces(self):
        """Reload known faces (call when database is updated)"""
        self.known_faces = self.load_known_faces()
        print(f"🔄 Reloaded {len(self.known_faces['names'])} known faces")
    
    def process_frame(self, frame):
        """Process a single frame for face recognition"""
        # Resize frame for faster processing (1/4 size)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find all faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        recognized_persons = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            name = "Unknown"
            person_id = None
            confidence = 0
            
            # Compare with known faces
            if len(self.known_faces['encodings']) > 0:
                matches = face_recognition.compare_faces(
                    self.known_faces['encodings'], 
                    face_encoding,
                    tolerance=self.config.get('recognition', {}).get('tolerance', 0.6)
                )
                
                if True in matches:
                    face_distances = face_recognition.face_distance(
                        self.known_faces['encodings'], 
                        face_encoding
                    )
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_faces['names'][best_match_index]
                        person_id = self.known_faces['ids'][best_match_index]
                        confidence = 1 - face_distances[best_match_index]
            
            # Scale back face location to original frame size
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Extract and save face image
            face_img = frame[top:bottom, left:right]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            # Create images directory if it doesn't exist
            os.makedirs('data/images', exist_ok=True)
            
            img_filename = f"{timestamp}_{name.replace(' ', '_')}.jpg"
            img_path = f"data/images/{img_filename}"
            cv2.imwrite(img_path, face_img)
            
            recognized_persons.append({
                'name': name,
                'person_id': person_id,
                'confidence': confidence,
                'image_path': img_path,
                'location': (top, right, bottom, left),
                'timestamp': datetime.now()
            })
        
        return recognized_persons
    
    def should_notify(self, person_id, cooldown_seconds=300):
        """Check if we should send notification (avoid spam)"""
        if person_id is None:
            return True  # Always notify for unknown persons
        
        current_time = time.time()
        last_time = self.last_seen.get(person_id, 0)
        
        if current_time - last_time > cooldown_seconds:
            self.last_seen[person_id] = current_time
            return True
        
        return False
    
    def run(self):
        """Main recognition loop"""
        self.running = True
        print("\n" + "="*50)
        print("✓ Face Recognition System Started")
        print("="*50)
        print(f"📹 DVR: {self.config['dvr']['ip']}")
        print(f"👥 Known Persons: {len(self.known_faces['names'])}")
        print(f"🔔 Notifications: {'Enabled' if self.config.get('notifications', {}).get('enabled') else 'Disabled'}")
        print("="*50 + "\n")
        
        frame_count = 0
        process_every_n_frames = self.config.get('recognition', {}).get('process_every_n_frames', 6)
        
        while self.running:
            try:
                # Get frame from DVR
                frame = self.dvr.get_frame()
                
                if frame is None:
                    print("⚠ Failed to get frame from DVR, retrying...")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Process every Nth frame to reduce CPU usage
                if frame_count % process_every_n_frames == 0:
                    persons = self.process_frame(frame)
                    
                    for person in persons:
                        if person['person_id']:
                            # Known person detected
                            if self.should_notify(person['person_id']):
                                self.db.log_visit(
                                    person['person_id'],
                                    person['confidence'],
                                    person['image_path']
                                )
                                
                                self.notifier.send_notification(
                                    title=f"✓ {person['name']} Detected",
                                    message=f"{person['name']} arrived at entrance",
                                    image_path=person['image_path'],
                                    confidence=person['confidence']
                                )
                                
                                print(f"✓ [{datetime.now().strftime('%H:%M:%S')}] Recognized: {person['name']} (confidence: {person['confidence']:.2%})")
                        else:
                            # Unknown person detected
                            if self.should_notify(None, cooldown_seconds=60):
                                self.db.log_unknown_visitor(person['image_path'])
                                
                                self.notifier.send_notification(
                                    title="⚠ Unknown Person Detected",
                                    message="Unknown visitor at entrance - please identify",
                                    image_path=person['image_path']
                                )
                                
                                print(f"⚠ [{datetime.now().strftime('%H:%M:%S')}] Unknown person detected")
                
                # Small delay to prevent CPU overload
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                print("\n⚠ Received shutdown signal...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop the system gracefully"""
        print("\n🛑 Stopping Face Recognition System...")
        self.running = False
        self.dvr.release()
        print("✓ System stopped successfully")

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║   DVR Face Recognition System v1.0                ║
    ║   Non-invasive CP Plus DVR Extension              ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Check if config exists
    if not os.path.exists('config/config.json'):
        print("❌ Configuration file not found!")
        print("📝 Please create config/config.json with your DVR settings")
        print("\nExample configuration:")
        print("""
{
  "dvr": {
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "admin123",
    "channel": 1
  },
  "notifications": {
    "enabled": true
  },
  "recognition": {
    "tolerance": 0.6,
    "process_every_n_frames": 6
  }
}
        """)
        sys.exit(1)
    
    # Initialize and run system
    system = FaceRecognitionSystem()
    
    try:
        system.run()
    except KeyboardInterrupt:
        print("\n")
    finally:
        system.stop()

if __name__ == "__main__":
    main()

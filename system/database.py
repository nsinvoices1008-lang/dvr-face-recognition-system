#!/usr/bin/env python3
"""
Database Module
Handles all database operations for face recognition system
"""

import sqlite3
from datetime import datetime
import numpy as np
import os

class Database:
    def __init__(self, db_path='data/faces.db'):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Persons table - stores registered individuals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                face_encoding BLOB NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Visits table - logs each visit by known persons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                image_path TEXT,
                FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
            )
        ''')
        
        # Unknown visitors table - stores unidentified faces
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                identified BOOLEAN DEFAULT 0,
                identified_as INTEGER,
                FOREIGN KEY (identified_as) REFERENCES persons(id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_visits_person_id 
            ON visits(person_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
            ON visits(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_unknown_timestamp 
            ON unknown_visitors(timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
        
        print("✓ Database initialized successfully")
    
    def add_person(self, name, face_encoding, notes=''):
        """Add a new person to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Convert numpy array to bytes
            encoding_blob = face_encoding.tobytes()
            
            cursor.execute('''
                INSERT INTO persons (name, face_encoding, notes)
                VALUES (?, ?, ?)
            ''', (name, encoding_blob, notes))
            
            person_id = cursor.lastrowid
            conn.commit()
            print(f"✓ Added person: {name} (ID: {person_id})")
            return person_id
            
        except sqlite3.IntegrityError:
            print(f"⚠ Person with name '{name}' already exists")
            return None
        except Exception as e:
            print(f"❌ Error adding person: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_persons(self):
        """Get all persons from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, face_encoding, first_seen, last_seen, 
                   visit_count, notes, created_at
            FROM persons
            ORDER BY name
        ''')
        
        persons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return persons
    
    def get_person(self, person_id):
        """Get a specific person by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, face_encoding, first_seen, last_seen,
                   visit_count, notes, created_at
            FROM persons 
            WHERE id = ?
        ''', (person_id,))
        
        person = cursor.fetchone()
        conn.close()
        
        return dict(person) if person else None
    
    def get_person_by_name(self, name):
        """Get a specific person by name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, face_encoding, first_seen, last_seen,
                   visit_count, notes, created_at
            FROM persons 
            WHERE name = ?
        ''', (name,))
        
        person = cursor.fetchone()
        conn.close()
        
        return dict(person) if person else None
    
    def update_person(self, person_id, name=None, notes=None):
        """Update person information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if name:
                cursor.execute('''
                    UPDATE persons SET name = ? WHERE id = ?
                ''', (name, person_id))
            
            if notes is not None:
                cursor.execute('''
                    UPDATE persons SET notes = ? WHERE id = ?
                ''', (notes, person_id))
            
            conn.commit()
            print(f"✓ Updated person ID: {person_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠ Person with name '{name}' already exists")
            return False
        except Exception as e:
            print(f"❌ Error updating person: {e}")
            return False
        finally:
            conn.close()
    
    def delete_person(self, person_id):
        """Delete a person and all their visits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete visits first (cascade should handle this, but being explicit)
            cursor.execute('DELETE FROM visits WHERE person_id = ?', (person_id,))
            
            # Delete person
            cursor.execute('DELETE FROM persons WHERE id = ?', (person_id,))
            
            conn.commit()
            print(f"✓ Deleted person ID: {person_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting person: {e}")
            return False
        finally:
            conn.close()
    
    def log_visit(self, person_id, confidence, image_path):
        """Log a visit by a known person"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert visit record
            cursor.execute('''
                INSERT INTO visits (person_id, confidence, image_path)
                VALUES (?, ?, ?)
            ''', (person_id, confidence, image_path))
            
            # Update person's last seen and visit count
            cursor.execute('''
                UPDATE persons 
                SET last_seen = CURRENT_TIMESTAMP,
                    visit_count = visit_count + 1
                WHERE id = ?
            ''', (person_id,))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"❌ Error logging visit: {e}")
            return None
        finally:
            conn.close()
    
    def log_unknown_visitor(self, image_path):
        """Log an unknown visitor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO unknown_visitors (image_path)
                VALUES (?)
            ''', (image_path,))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"❌ Error logging unknown visitor: {e}")
            return None
        finally:
            conn.close()
    
    def get_recent_visits(self, limit=50, person_id=None):
        """Get recent visits"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if person_id:
            cursor.execute('''
                SELECT v.*, p.name 
                FROM visits v
                JOIN persons p ON v.person_id = p.id
                WHERE v.person_id = ?
                ORDER BY v.timestamp DESC
                LIMIT ?
            ''', (person_id, limit))
        else:
            cursor.execute('''
                SELECT v.*, p.name 
                FROM visits v
                JOIN persons p ON v.person_id = p.id
                ORDER BY v.timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        visits = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return visits
    
    def get_unknown_visitors(self, limit=50, identified=False):
        """Get unknown visitors"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM unknown_visitors
            WHERE identified = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (1 if identified else 0, limit))
        
        visitors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return visitors
    
    def mark_unknown_as_identified(self, unknown_id, person_id):
        """Mark an unknown visitor as identified"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE unknown_visitors
                SET identified = 1, identified_as = ?
                WHERE id = ?
            ''', (person_id, unknown_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error marking as identified: {e}")
            return False
        finally:
            conn.close()
    
    def get_statistics(self):
        """Get system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total persons
        cursor.execute('SELECT COUNT(*) FROM persons')
        stats['total_persons'] = cursor.fetchone()[0]
        
        # Total visits
        cursor.execute('SELECT COUNT(*) FROM visits')
        stats['total_visits'] = cursor.fetchone()[0]
        
        # Unknown visitors
        cursor.execute('SELECT COUNT(*) FROM unknown_visitors WHERE identified = 0')
        stats['unknown_visitors'] = cursor.fetchone()[0]
        
        # Visits today
        cursor.execute('''
            SELECT COUNT(*) FROM visits 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        stats['visits_today'] = cursor.fetchone()[0]
        
        # Most frequent visitor
        cursor.execute('''
            SELECT p.name, p.visit_count
            FROM persons p
            ORDER BY p.visit_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        stats['most_frequent_visitor'] = {
            'name': result[0] if result else None,
            'count': result[1] if result else 0
        }
        
        conn.close()
        return stats

#!/usr/bin/env python3
"""
Web Interface for DVR Face Recognition System
Flask-based dashboard for monitoring and management
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os

# Add system directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'system'))

import face_recognition
import cv2
import numpy as np
from database import Database
import json
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db = Database('../data/faces.db')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with statistics"""
    stats = db.get_statistics()
    return render_template('dashboard.html', stats=stats)

@app.route('/persons')
def persons():
    """Person management page"""
    all_persons = db.get_all_persons()
    # Remove face encoding from response (too large for template)
    for person in all_persons:
        person.pop('face_encoding', None)
    return render_template('persons.html', persons=all_persons)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Endpoints

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/persons', methods=['GET'])
def get_persons():
    """Get all persons"""
    persons = db.get_all_persons()
    # Convert blob to list for JSON serialization
    for person in persons:
        person.pop('face_encoding', None)
    return jsonify(persons)

@app.route('/api/person/<int:person_id>', methods=['GET'])
def get_person(person_id):
    """Get specific person"""
    person = db.get_person(person_id)
    if person:
        person.pop('face_encoding', None)
        # Get recent visits for this person
        visits = db.get_recent_visits(limit=10, person_id=person_id)
        person['recent_visits'] = visits
        return jsonify(person)
    return jsonify({'error': 'Person not found'}), 404

@app.route('/api/person', methods=['POST'])
def add_person():
    """Add new person"""
    try:
        data = request.get_json()
        name = data.get('name')
        image_data = data.get('image_data')  # Base64 or file path
        notes = data.get('notes', '')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save uploaded file
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.replace(' ', '_')}.jpg"
            filepath = os.path.join('../data/images', filename)
            os.makedirs('../data/images', exist_ok=True)
            file.save(filepath)
            
            # Load image and generate encoding
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) == 0:
                os.remove(filepath)
                return jsonify({'error': 'No face found in image'}), 400
            
            encoding = encodings[0]
            person_id = db.add_person(name, encoding, notes)
            
            if person_id:
                return jsonify({
                    'success': True,
                    'person_id': person_id,
                    'message': f'Person {name} added successfully'
                })
            else:
                return jsonify({'error': 'Failed to add person'}), 500
        
        return jsonify({'error': 'No image provided'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/person/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    """Update person information"""
    data = request.get_json()
    name = data.get('name')
    notes = data.get('notes')
    
    success = db.update_person(person_id, name=name, notes=notes)
    
    if success:
        return jsonify({'success': True, 'message': 'Person updated successfully'})
    return jsonify({'error': 'Failed to update person'}), 500

@app.route('/api/person/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete person"""
    success = db.delete_person(person_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Person deleted successfully'})
    return jsonify({'error': 'Failed to delete person'}), 500

@app.route('/api/visits', methods=['GET'])
def get_visits():
    """Get recent visits"""
    limit = request.args.get('limit', 50, type=int)
    person_id = request.args.get('person_id', type=int)
    
    visits = db.get_recent_visits(limit=limit, person_id=person_id)
    return jsonify(visits)

@app.route('/api/unknown', methods=['GET'])
def get_unknown():
    """Get unknown visitors"""
    limit = request.args.get('limit', 50, type=int)
    unknown = db.get_unknown_visitors(limit=limit)
    return jsonify(unknown)

@app.route('/api/unknown/<int:unknown_id>/identify', methods=['POST'])
def identify_unknown(unknown_id):
    """Identify an unknown visitor"""
    data = request.get_json()
    name = data.get('name')
    notes = data.get('notes', '')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Get unknown visitor
    unknown_visitors = db.get_unknown_visitors(limit=1000)
    unknown = next((v for v in unknown_visitors if v['id'] == unknown_id), None)
    
    if not unknown:
        return jsonify({'error': 'Unknown visitor not found'}), 404
    
    image_path = unknown['image_path']
    
    # Add as new person
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) == 0:
            return jsonify({'error': 'No face found in image'}), 400
        
        encoding = encodings[0]
        person_id = db.add_person(name, encoding, notes)
        
        if person_id:
            # Mark unknown as identified
            db.mark_unknown_as_identified(unknown_id, person_id)
            
            return jsonify({
                'success': True,
                'person_id': person_id,
                'message': f'Unknown visitor identified as {name}'
            })
        else:
            return jsonify({'error': 'Failed to add person'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration (sensitive data removed)"""
    try:
        with open('../config/config.json', 'r') as f:
            config = json.load(f)
        
        # Remove sensitive data
        if 'dvr' in config:
            config['dvr'].pop('password', None)
        if 'notifications' in config:
            if 'email' in config['notifications']:
                config['notifications']['email'].pop('sendgrid_api_key', None)
            if 'telegram' in config['notifications']:
                config['notifications']['telegram'].pop('bot_token', None)
        
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        
        with open('../config/config.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images"""
    return send_from_directory('../data/images', filename)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    filepath = os.path.join('../data/images', filename)
    os.makedirs('../data/images', exist_ok=True)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': filepath
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║   DVR Face Recognition - Web Interface            ║
    ╚═══════════════════════════════════════════════════╝
    """)
    print("🌐 Starting web server...")
    print("📱 Access dashboard at: http://localhost:5000")
    print("🌍 Or from network: http://YOUR_IP:5000")
    print("\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

# API Documentation

Complete REST API reference for DVR Face Recognition System.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. For production use, implement authentication middleware.

## Endpoints

### Statistics

#### Get System Statistics

```http
GET /api/stats
```

**Response:**
```json
{
  "total_persons": 15,
  "total_visits": 342,
  "unknown_visitors": 5,
  "visits_today": 23,
  "most_frequent_visitor": {
    "name": "John Doe",
    "count": 45
  }
}
```

---

### Persons

#### List All Persons

```http
GET /api/persons
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "first_seen": "2024-01-15 10:30:00",
    "last_seen": "2024-01-20 14:25:00",
    "visit_count": 45,
    "notes": "Regular visitor",
    "created_at": "2024-01-15 10:30:00"
  }
]
```

#### Get Person Details

```http
GET /api/person/:id
```

**Parameters:**
- `id` (integer) - Person ID

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "first_seen": "2024-01-15 10:30:00",
  "last_seen": "2024-01-20 14:25:00",
  "visit_count": 45,
  "notes": "Regular visitor",
  "recent_visits": [
    {
      "id": 123,
      "timestamp": "2024-01-20 14:25:00",
      "confidence": 0.95,
      "image_path": "data/images/20240120_142500_John_Doe.jpg"
    }
  ]
}
```

#### Add New Person

```http
POST /api/person
```

**Request (multipart/form-data):**
```
file: [image file]
name: "John Doe"
notes: "Regular visitor"
```

**Response:**
```json
{
  "success": true,
  "person_id": 1,
  "message": "Person John Doe added successfully"
}
```

**Error Response:**
```json
{
  "error": "No face found in image"
}
```

#### Update Person

```http
PUT /api/person/:id
```

**Parameters:**
- `id` (integer) - Person ID

**Request Body:**
```json
{
  "name": "John Smith",
  "notes": "Updated notes"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Person updated successfully"
}
```

#### Delete Person

```http
DELETE /api/person/:id
```

**Parameters:**
- `id` (integer) - Person ID

**Response:**
```json
{
  "success": true,
  "message": "Person deleted successfully"
}
```

---

### Visits

#### Get Recent Visits

```http
GET /api/visits?limit=50&person_id=1
```

**Query Parameters:**
- `limit` (integer, optional) - Number of visits to return (default: 50)
- `person_id` (integer, optional) - Filter by specific person

**Response:**
```json
[
  {
    "id": 123,
    "person_id": 1,
    "name": "John Doe",
    "timestamp": "2024-01-20 14:25:00",
    "confidence": 0.95,
    "image_path": "data/images/20240120_142500_John_Doe.jpg"
  }
]
```

---

### Unknown Visitors

#### Get Unknown Visitors

```http
GET /api/unknown?limit=50
```

**Query Parameters:**
- `limit` (integer, optional) - Number of unknown visitors to return (default: 50)

**Response:**
```json
[
  {
    "id": 45,
    "timestamp": "2024-01-20 15:30:00",
    "image_path": "data/images/20240120_153000_Unknown.jpg",
    "identified": false
  }
]
```

#### Identify Unknown Visitor

```http
POST /api/unknown/:id/identify
```

**Parameters:**
- `id` (integer) - Unknown visitor ID

**Request Body:**
```json
{
  "name": "Jane Smith",
  "notes": "New employee"
}
```

**Response:**
```json
{
  "success": true,
  "person_id": 16,
  "message": "Unknown visitor identified as Jane Smith"
}
```

---

### Configuration

#### Get Configuration

```http
GET /api/config
```

**Response:**
```json
{
  "dvr": {
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "channel": 1
  },
  "notifications": {
    "enabled": true,
    "email": {
      "enabled": false,
      "from_email": "alerts@example.com",
      "to_email": "user@example.com"
    },
    "telegram": {
      "enabled": false,
      "chat_id": "123456789"
    }
  },
  "recognition": {
    "tolerance": 0.6,
    "process_every_n_frames": 6
  }
}
```

**Note:** Sensitive data (passwords, API keys) are removed from response.

#### Update Configuration

```http
POST /api/config
```

**Request Body:**
```json
{
  "dvr": {
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "new_password",
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
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated"
}
```

---

### File Upload

#### Upload Image

```http
POST /api/upload
```

**Request (multipart/form-data):**
```
file: [image file]
```

**Response:**
```json
{
  "success": true,
  "filename": "20240120_153000_photo.jpg",
  "path": "data/images/20240120_153000_photo.jpg"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Usage Examples

### Python

```python
import requests

# Get statistics
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
print(f"Total persons: {stats['total_persons']}")

# Add new person
files = {'file': open('photo.jpg', 'rb')}
data = {'name': 'John Doe', 'notes': 'Regular visitor'}
response = requests.post('http://localhost:5000/api/person', files=files, data=data)
result = response.json()
print(f"Person added: {result['person_id']}")

# Get recent visits
response = requests.get('http://localhost:5000/api/visits?limit=10')
visits = response.json()
for visit in visits:
    print(f"{visit['name']} - {visit['timestamp']}")
```

### JavaScript (Fetch API)

```javascript
// Get statistics
fetch('http://localhost:5000/api/stats')
  .then(response => response.json())
  .then(stats => {
    console.log(`Total persons: ${stats.total_persons}`);
  });

// Add new person
const formData = new FormData();
formData.append('file', photoFile);
formData.append('name', 'John Doe');
formData.append('notes', 'Regular visitor');

fetch('http://localhost:5000/api/person', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(result => {
    console.log(`Person added: ${result.person_id}`);
  });

// Get recent visits
fetch('http://localhost:5000/api/visits?limit=10')
  .then(response => response.json())
  .then(visits => {
    visits.forEach(visit => {
      console.log(`${visit.name} - ${visit.timestamp}`);
    });
  });
```

### cURL

```bash
# Get statistics
curl http://localhost:5000/api/stats

# Add new person
curl -X POST http://localhost:5000/api/person \
  -F "file=@photo.jpg" \
  -F "name=John Doe" \
  -F "notes=Regular visitor"

# Get recent visits
curl "http://localhost:5000/api/visits?limit=10"

# Update person
curl -X PUT http://localhost:5000/api/person/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"John Smith","notes":"Updated notes"}'

# Delete person
curl -X DELETE http://localhost:5000/api/person/1
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse.

## CORS

CORS is not enabled by default. To enable CORS for cross-origin requests, add Flask-CORS:

```python
from flask_cors import CORS
CORS(app)
```

---

## Webhooks (Future Feature)

Planned webhook support for real-time notifications:

```http
POST /api/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["person_detected", "unknown_visitor"]
}
```

---

For questions or issues with the API, please open an issue on GitHub.

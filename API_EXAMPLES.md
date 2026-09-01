# API Request & Response Examples

## Authentication Endpoints

### 1. Register User

**Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "dob": "1990-05-15",
  "securityQuestion": "firstConcert",
  "securityAnswer": "Coldplay"
}
```

**Response (201 Created):**
```json
{
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "dob": "1990-05-15",
    "createdAt": "2026-08-11T10:30:00"
  }
}
```

### 2. Login

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "dob": "1990-05-15",
    "createdAt": "2026-08-11T10:30:00"
  }
}
```

### 3. Reset Password

**Request:**
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com",
  "dob": "1990-05-15",
  "securityAnswer": "Coldplay",
  "newPassword": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

### 4. Get Current User

**Request:**
```http
GET /api/auth/me
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "dob": "1990-05-15",
  "createdAt": "2026-08-11T10:30:00"
}
```

---

## Trip Endpoints

### 1. Get All Trips (with filtering & pagination)

**Request:**
```http
GET /api/trips?status=current&page=1&limit=10&sort=start_date&order=desc
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Weekend in Kyoto",
      "destination": "Kyoto, Japan",
      "startDate": "2026-08-10",
      "endDate": "2026-08-15",
      "status": "current",
      "placesCount": 5,
      "completedPlacesCount": 3,
      "createdAt": "2026-07-20T14:30:00",
      "updatedAt": "2026-08-05T09:15:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

### 2. Get Single Trip (with places)

**Request:**
```http
GET /api/trips/1
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Weekend in Kyoto",
  "destination": "Kyoto, Japan",
  "startDate": "2026-08-10",
  "endDate": "2026-08-15",
  "status": "current",
  "createdAt": "2026-07-20T14:30:00",
  "updatedAt": "2026-08-05T09:15:00",
  "places": [
    {
      "id": 101,
      "name": "Fushimi Inari Taisha",
      "completed": true,
      "createdAt": "2026-08-01T10:00:00"
    },
    {
      "id": 102,
      "name": "Arashiyama Bamboo Grove",
      "completed": false,
      "createdAt": "2026-08-01T10:05:00"
    }
  ],
  "stats": {
    "totalPlaces": 5,
    "completedPlaces": 3,
    "progressPercent": 60
  }
}
```

### 3. Create Trip

**Request:**
```http
POST /api/trips
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "title": "Summer in Paris",
  "destination": "Paris, France",
  "startDate": "2026-07-01",
  "endDate": "2026-07-10"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Summer in Paris",
  "destination": "Paris, France",
  "startDate": "2026-07-01",
  "endDate": "2026-07-10",
  "status": "upcoming",
  "createdAt": "2026-08-11T15:20:00",
  "updatedAt": "2026-08-11T15:20:00",
  "places": [],
  "stats": {
    "totalPlaces": 0,
    "completedPlaces": 0,
    "progressPercent": 0
  }
}
```

### 4. Update Trip

**Request:**
```http
PUT /api/trips/2
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "title": "Summer in Paris - Extended",
  "endDate": "2026-07-15"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "title": "Summer in Paris - Extended",
  "destination": "Paris, France",
  "startDate": "2026-07-01",
  "endDate": "2026-07-15",
  "status": "upcoming",
  "createdAt": "2026-08-11T15:20:00",
  "updatedAt": "2026-08-11T15:25:00",
  "places": [],
  "stats": {
    "totalPlaces": 0,
    "completedPlaces": 0,
    "progressPercent": 0
  }
}
```

### 5. Delete Trip

**Request:**
```http
DELETE /api/trips/2
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "message": "Trip deleted successfully"
}
```

---

## Place Endpoints

### 1. Get Places for Trip

**Request:**
```http
GET /api/trips/1/places?completed=false&page=1&limit=20
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "tripId": 1,
  "data": [
    {
      "id": 102,
      "name": "Arashiyama Bamboo Grove",
      "completed": false,
      "createdAt": "2026-08-01T10:05:00"
    },
    {
      "id": 103,
      "name": "Kinkaku-ji Temple",
      "completed": false,
      "createdAt": "2026-08-01T10:10:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

### 2. Add Place to Trip

**Request:**
```http
POST /api/trips/1/places
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "name": "Visit Nijo Castle",
  "completed": false
}
```

**Response (201 Created):**
```json
{
  "id": 104,
  "name": "Visit Nijo Castle",
  "completed": false,
  "createdAt": "2026-08-11T16:00:00"
}
```

### 3. Update Place (Toggle Completed)

**Request:**
```http
PUT /api/places/102
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "completed": true
}
```

**Response (200 OK):**
```json
{
  "id": 102,
  "name": "Arashiyama Bamboo Grove",
  "completed": true,
  "createdAt": "2026-08-01T10:05:00"
}
```

### 4. Delete Place

**Request:**
```http
DELETE /api/places/104
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "message": "Place deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "error": "Unauthorized"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

---

## Authentication Header Format

All protected endpoints require the JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

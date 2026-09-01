# Trip Planner API

Flask REST API for the Trip Planner application with PostgreSQL database.

## Features

- ✅ JWT-based authentication
- ✅ User registration with security questions
- ✅ Password reset functionality
- ✅ CRUD operations for trips and places
- ✅ Filtering and pagination
- ✅ Trip status calculation (current/upcoming/past)
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ CORS support for React frontend

## Tech Stack

- **Flask** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin support
- **Flask-Migrate** - Database migrations

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### 2. Install Dependencies

```bash
cd trip-planner-api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database

```bash
# Create database
createdb trip_planner

# Or using psql
psql -U postgres
CREATE DATABASE trip_planner;
\q
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials and secret keys
```

Example `.env`:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=postgresql://username:password@localhost:5432/trip_planner
CORS_ORIGINS=http://localhost:3000
```

### 5. Initialize Database

```bash
# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run the API

```bash
flask run
# Or
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Create new account | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| POST | `/api/auth/logout` | Logout | Yes |
| POST | `/api/auth/reset-password` | Reset password | No |
| GET | `/api/auth/me` | Get current user | Yes |

### Trips

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/trips` | Get all trips (with filtering/pagination) | Yes |
| POST | `/api/trips` | Create new trip | Yes |
| GET | `/api/trips/:id` | Get single trip | Yes |
| PUT | `/api/trips/:id` | Update trip | Yes |
| DELETE | `/api/trips/:id` | Delete trip | Yes |

### Places

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/trips/:id/places` | Get all places for a trip | Yes |
| POST | `/api/trips/:id/places` | Add place to trip | Yes |
| GET | `/api/places/:id` | Get single place | Yes |
| PUT/PATCH | `/api/places/:id` | Update place | Yes |
| DELETE | `/api/places/:id` | Delete place | Yes |

## Query Parameters

### GET /api/trips
- `status` - Filter by status: `all`, `current`, `upcoming`, `past`
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 10, max: 100)
- `sort` - Sort field: `start_date`, `end_date`, `title`, `created_at`
- `order` - Sort order: `asc`, `desc`
- `search` - Search in title/destination

### GET /api/trips/:id/places
- `completed` - Filter by completion: `true`, `false`
- `page` - Page number
- `limit` - Items per page (max: 100)
- `search` - Search place names

## Project Structure

```
trip-planner-api/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication routes
│       ├── trips.py         # Trip routes
│       └── places.py        # Place routes
├── migrations/              # Database migrations
├── app.py                   # Application entry point
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email
- `password_hash` - Hashed password
- `dob` - Date of birth
- `security_question` - Security question
- `security_answer_hash` - Hashed security answer
- `created_at` - Account creation timestamp

### Trips Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `title` - Trip title
- `destination` - Destination
- `start_date` - Start date
- `end_date` - End date
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Places Table
- `id` - Primary key
- `trip_id` - Foreign key to trips
- `name` - Place/activity name
- `completed` - Completion status
- `created_at` - Creation timestamp

## License

MIT

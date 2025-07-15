# VPR System Backend

A comprehensive Python backend for the Vehicle Plate Recognition (VPR) System built with FastAPI and Supabase.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Supabase Integration**: PostgreSQL database with real-time capabilities
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Administrator, Operator, and Viewer roles
- **Comprehensive APIs**: Full CRUD operations for all entities
- **Data Validation**: Pydantic models for request/response validation
- **Analytics & Reporting**: Built-in analytics and report generation
- **Auto-Generated Documentation**: Interactive API docs at `/docs`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database connection and setup
│   │   └── security.py        # Authentication and security utilities
│   ├── models/                # Pydantic models
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   ├── violation.py
│   │   └── scan.py
│   └── api/
│       ├── deps.py            # API dependencies
│       └── v1/
│           ├── api.py         # API router
│           └── endpoints/     # API endpoints
│               ├── auth.py
│               ├── users.py
│               ├── vehicles.py
│               ├── violations.py
│               ├── scans.py
│               └── analytics.py
├── requirements.txt
├── .env.example
├── run.py                     # Application runner
└── README.md
```

## Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Update the `.env` file with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Database Setup

The application uses Supabase (PostgreSQL). You'll need to create the following tables:

#### Users Table
```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Viewer',
    status TEXT NOT NULL DEFAULT 'pending',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Vehicles Table
```sql
CREATE TABLE vehicles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plate_number TEXT UNIQUE NOT NULL,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    color TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    engine_number TEXT NOT NULL,
    chassis_number TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    owner_phone TEXT NOT NULL,
    owner_email TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    registration_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Violations Table
```sql
CREATE TABLE violations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plate_number TEXT NOT NULL,
    violation_type TEXT NOT NULL,
    location TEXT NOT NULL,
    date_time TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    description TEXT,
    fine_amount DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Scans Table
```sql
CREATE TABLE scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plate_number TEXT NOT NULL,
    location TEXT NOT NULL,
    scan_time TIMESTAMPTZ NOT NULL,
    confidence_score DECIMAL(5,4),
    image_url TEXT,
    camera_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Running the Application

```bash
# Using the runner script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

### Users Management
- `GET /api/v1/users/` - List users with filtering
- `GET /api/v1/users/pending` - Get pending approvals
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `POST /api/v1/users/{user_id}/approve` - Approve user
- `POST /api/v1/users/{user_id}/reject` - Reject user

### Vehicle Registry
- `GET /api/v1/vehicles/` - List vehicles with filtering
- `POST /api/v1/vehicles/` - Create vehicle registration
- `GET /api/v1/vehicles/{vehicle_id}` - Get vehicle by ID
- `PUT /api/v1/vehicles/{vehicle_id}` - Update vehicle
- `DELETE /api/v1/vehicles/{vehicle_id}` - Delete vehicle

### Violation Management
- `GET /api/v1/violations/` - List violations with filtering
- `POST /api/v1/violations/` - Create violation record
- `GET /api/v1/violations/{violation_id}` - Get violation by ID
- `PUT /api/v1/violations/{violation_id}` - Update violation
- `POST /api/v1/violations/{violation_id}/resolve` - Resolve violation
- `DELETE /api/v1/violations/{violation_id}` - Delete violation

### Scan Records
- `GET /api/v1/scans/` - List scans with filtering
- `POST /api/v1/scans/` - Create scan record
- `GET /api/v1/scans/{scan_id}` - Get scan by ID
- `GET /api/v1/scans/stats/daily` - Get daily scan statistics
- `DELETE /api/v1/scans/{scan_id}` - Delete scan

### Analytics & Reporting
- `GET /api/v1/analytics/dashboard` - Dashboard statistics
- `GET /api/v1/analytics/violations/trends` - Violation trends
- `GET /api/v1/analytics/scans/activity` - Scan activity stats
- `GET /api/v1/analytics/vehicles/statistics` - Vehicle statistics
- `GET /api/v1/analytics/reports/generate` - Generate reports

## User Roles & Permissions

### Administrator
- Full access to all endpoints
- User management and approvals
- System configuration

### Operator
- Vehicle registration and updates
- Violation management
- Scan record management
- Analytics viewing

### Viewer
- Read-only access to data
- Analytics and reporting
- Cannot modify records

## Security Features

- **JWT Token Authentication**: Secure token-based auth
- **Password Hashing**: Bcrypt password hashing
- **Role-Based Access Control**: Granular permissions
- **CORS Protection**: Configurable CORS settings
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: Supabase client protection

## Development

### Adding New Endpoints

1. Create model in `app/models/`
2. Add endpoint in `app/api/v1/endpoints/`
3. Include router in `app/api/v1/api.py`
4. Update database schema if needed

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

1. Set `DEBUG=False` in environment
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use HTTPS in production
5. Set up proper logging
6. Use a production WSGI server like Gunicorn

```bash
# Production server example
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Support

For issues and questions, please refer to the API documentation at `/docs` when the server is running.
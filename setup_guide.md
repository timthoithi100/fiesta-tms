# Fiesta TMS - Complete Setup Guide

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Creating Missing Frontend Files](#creating-missing-frontend-files)
3. [Database Setup](#database-setup)
4. [Running the Application](#running-the-application)
5. [Creating Admin User](#creating-admin-user)
6. [Testing](#testing)
7. [Common Issues](#common-issues)

## Initial Setup

### 1. Install Dependencies

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server
```

**On macOS:**
```bash
brew install python@3.11 postgresql redis
```

**On Windows:**
- Download Python 3.11 from python.org
- Download PostgreSQL from postgresql.org
- Download Redis from redis.io

### 2. Clone and Navigate
```bash
git clone <your-repo>
cd fiesta-tms
```

### 3. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Packages
```bash
pip install -r backend/requirements.txt
```

## Creating Missing Frontend Files

### Create Directory Structure
```bash
mkdir -p frontend/templates/student
mkdir -p frontend/templates/admin
mkdir -p frontend/static/css
mkdir -p frontend/static/js
mkdir -p frontend/static/images
```

### Student Module Templates

**1. frontend/templates/student/personal_info.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Information - Fiesta TMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/custom.css">
</head>
<body>
    <!-- Copy header, sidebar, overlay from home.html -->
    <header class="header"><!-- ... --></header>
    <nav class="sidebar" id="sidebar"><!-- ... --></nav>
    <div class="overlay" id="overlay"></div>

    <div class="dashboard-container">
        <h2 class="page-title">Personal Information</h2>
        
        <div class="form-container">
            <form id="personal-info-form">
                <h5 class="mb-3">Read-Only Information</h5>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Student ID</label>
                        <input type="text" class="form-control" id="display-student-id" readonly>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Gender</label>
                        <input type="text" class="form-control" id="display-gender" readonly>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Date of Birth</label>
                        <input type="text" class="form-control" id="display-dob" readonly>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Program</label>
                        <input type="text" class="form-control" id="display-program" readonly>
                    </div>
                </div>

                <h5 class="mb-3 mt-4">Editable Information</h5>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label class="form-label">First Name *</label>
                        <input type="text" class="form-control" id="first_name" required>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Middle Name</label>
                        <input type="text" class="form-control" id="middle_name">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Last Name *</label>
                        <input type="text" class="form-control" id="last_name" required>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Phone Number *</label>
                        <input type="tel" class="form-control" id="phone_number" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">City *</label>
                        <input type="text" class="form-control" id="city" required>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Address</label>
                    <input type="text" class="form-control" id="address">
                </div>
                <button type="submit" class="btn btn-primary">Update Information</button>
            </form>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/student.js"></script>
</body>
</html>
```

**Use this pattern for:**
- `fees.html` - Fee statement with tables
- `unit_registration.html` - Available and registered units
- `results.html` - Results table
- `graduation.html` - Graduation request form and list
- `clearance.html` - Clearance request form and list

### Admin Module Templates

Create similar files in `frontend/templates/admin/`:
- `students.html` - Student list with search
- `fee_management.html` - Fee creation and payment recording
- `unit_management.html` - Unit CRUD operations
- `results_management.html` - Results entry
- `clearance_processing.html` - Request processing
- `reports.html` - Analytics dashboard

## Database Setup

### 1. Create PostgreSQL Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE fiesta_db;
CREATE USER fiesta_user WITH PASSWORD 'fiesta_pass';
GRANT ALL PRIVILEGES ON DATABASE fiesta_db TO fiesta_user;
\q
```

### 2. Configure Environment
```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql+asyncpg://fiesta_user:fiesta_pass@localhost:5432/fiesta_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-min-32-characters-long
DEBUG=True
```

### 3. Initialize Database with Alembic
```bash
cd backend

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Running the Application

### Development Mode
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web alembic upgrade head

# Stop services
docker-compose down
```

## Creating Admin User

### Method 1: Python Shell
```bash
cd backend
python
```

```python
import asyncio
from app.database import async_session_maker
from app.models import User, UserRole
from app.security import get_password_hash

async def create_admin():
    async with async_session_maker() as session:
        admin = User(
            email="admin@fiesta.edu",
            hashed_password=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        session.add(admin)
        await session.commit()
        print("Admin user created!")

asyncio.run(create_admin())
```

### Method 2: SQL Direct
```sql
-- Connect to database
psql -U fiesta_user -d fiesta_db

-- Insert admin (use bcrypt hash for password)
INSERT INTO users (id, email, hashed_password, role, is_active, is_verified, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin@fiesta.edu',
    '$2b$12$[your-bcrypt-hash]',
    'admin',
    true,
    true,
    NOW(),
    NOW()
);
```

## Testing

### Access the Application
1. Open browser: http://localhost:8000
2. Sign up as a student
3. Login with admin credentials
4. Test all modules

### Test Credentials
- **Student**: Create via signup page
- **Admin**: admin@fiesta.edu / Admin@123

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@fiesta.edu","password":"Admin@123"}'
```

## Common Issues

### Issue 1: Database Connection Error
**Error:** `Connection refused to PostgreSQL`

**Solution:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Issue 2: Redis Connection Error
**Error:** `Connection refused to Redis`

**Solution:**
```bash
# Start Redis
sudo systemctl start redis

# Or on macOS
brew services start redis
```

### Issue 3: Import Errors
**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue 4: Migration Errors
**Error:** `Alembic migration failed`

**Solution:**
```bash
# Drop all tables and recreate
alembic downgrade base
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "Fix schema"
alembic upgrade head
```

### Issue 5: CORS Errors
**Error:** `CORS policy blocked`

**Solution:**
Update `.env`:
```env
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000
```

## Production Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Use PostgreSQL with proper user permissions
- [ ] Set up SSL/TLS certificates
- [ ] Configure Nginx reverse proxy
- [ ] Set up backup strategy
- [ ] Configure monitoring (Sentry)
- [ ] Enable rate limiting
- [ ] Review security headers

## Next Steps

1. **Customize**: Modify UI colors, logos, and branding
2. **Extend**: Add more features (email notifications, file uploads)
3. **Optimize**: Add caching, database indexes
4. **Monitor**: Set up logging and error tracking
5. **Scale**: Configure load balancing and replication

## Support

For issues and questions:
- Check API docs: http://localhost:8000/docs
- Review logs: `docker-compose logs -f web`
- Database queries: `psql -U fiesta_user -d fiesta_db`

---

**Happy Coding! 🚀**
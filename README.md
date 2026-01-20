# Fiesta Training Management System

A modern, secure, and scalable web-based training management system for Fiesta School built with FastAPI and Bootstrap 5.

## Features

### Student Portal
- **Dashboard**: Overview of registered units, fees, and personal information
- **Personal Information**: View and update personal details
- **Fee Statement**: Track fees billed, payments made, and outstanding balance
- **Unit Registration**: Browse and register for available courses
- **Provisional Results**: View published exam results
- **Graduation Request**: Submit graduation applications
- **Clearance Request**: Request clearance certificates

### Admin Portal
- **Student Management**: View, search, and manage student records
- **Unit Management**: Create and manage course units
- **Results Management**: Enter and publish student results
- **Fee Management**: Create fee structures and record payments
- **Clearance Processing**: Review and approve/reject student requests
- **Reports & Analytics**: View system statistics and generate reports

## Tech Stack

**Backend:**
- FastAPI (async web framework)
- PostgreSQL 15+ (database)
- Redis (caching & sessions)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- JWT (authentication)

**Frontend:**
- Bootstrap 5.3
- Vanilla JavaScript (ES6+)
- Custom CSS with animations

**DevOps:**
- Docker & Docker Compose
- Uvicorn (ASGI server)
- Gunicorn (process manager)

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd fiesta-tms
```

2. **Create environment file**
```bash
touch .env
# Edit .env, refer to .env.example
```

3. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up PostgreSQL & Redis**
```bash
# Install and start PostgreSQL
# Install and start Redis
```

6. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
 
## Project Structure

```
fiesta-tms/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   ├── security.py      # Auth & security
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── student/
│       └── admin/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Security Features

-  Password hashing with bcrypt
-  JWT-based authentication
-  Role-based access control (RBAC)
-  SQL injection prevention (SQLAlchemy ORM)
-  XSS protection
-  CSRF protection
-  Rate limiting
-  HTTPS enforcement
-  Security headers
-  Input validation (Pydantic)

## Creating Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Production Deployment

### Environment Variables
Update `.env` for production:
```env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<strong-random-key-min-32-chars>
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
ALLOWED_ORIGINS=https://yourdomain.com
```

### Using Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Default Admin Account

Create admin user via Python shell:
```python
from app.models import User, UserRole
from app.security import get_password_hash

# Create admin user
admin = User(
    email="admin@fiesta.edu",
    hashed_password=get_password_hash("Admin@123"),
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
# Add to database session and commit
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@fiesta.edu or create an issue in the repository.

---

**Built for Fiesta Training School**

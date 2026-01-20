# Fiesta TMS - Quick Reference

## 📁 Complete File Checklist

### ✅ Backend Files (Provided)
- [x] `backend/requirements.txt`
- [x] `backend/.env.example`
- [x] `backend/alembic.ini`
- [x] `backend/alembic/env.py`
- [x] `backend/app/__init__.py`
- [x] `backend/app/main.py`
- [x] `backend/app/config.py`
- [x] `backend/app/database.py`
- [x] `backend/app/security.py`
- [x] `backend/app/dependencies.py`
- [x] `backend/app/models/__init__.py`
- [x] `backend/app/models/user.py`
- [x] `backend/app/models/student.py`
- [x] `backend/app/models/unit.py`
- [x] `backend/app/models/fee.py`
- [x] `backend/app/models/request.py`
- [x] `backend/app/schemas/__init__.py`
- [x] `backend/app/schemas/auth.py`
- [x] `backend/app/schemas/student.py`
- [x] `backend/app/schemas/unit.py`
- [x] `backend/app/schemas/fee.py`
- [x] `backend/app/schemas/request.py`
- [x] `backend/app/routes/__init__.py`
- [x] `backend/app/routes/auth.py`
- [x] `backend/app/routes/student.py`
- [x] `backend/app/routes/admin.py`
- [x] `backend/app/utils/__init__.py`

### ✅ Frontend Files (Provided)
- [x] `frontend/static/css/custom.css`
- [x] `frontend/static/js/main.js`
- [x] `frontend/static/js/auth.js`
- [x] `frontend/static/js/student.js`
- [x] `frontend/static/js/admin.js`
- [x] `frontend/templates/index.html`
- [x] `frontend/templates/login.html`
- [x] `frontend/templates/signup.html`
- [x] `frontend/templates/student/home.html`
- [x] `frontend/templates/admin/home.html`

### ⚠️ Frontend Files (To Create)
Follow the pattern from provided examples:

**Student Templates:**
- [ ] `frontend/templates/student/personal_info.html`
- [ ] `frontend/templates/student/fees.html`
- [ ] `frontend/templates/student/unit_registration.html`
- [ ] `frontend/templates/student/results.html`
- [ ] `frontend/templates/student/graduation.html`
- [ ] `frontend/templates/student/clearance.html`

**Admin Templates:**
- [ ] `frontend/templates/admin/students.html`
- [ ] `frontend/templates/admin/fee_management.html`
- [ ] `frontend/templates/admin/unit_management.html`
- [ ] `frontend/templates/admin/results_management.html`
- [ ] `frontend/templates/admin/clearance_processing.html`
- [ ] `frontend/templates/admin/reports.html`

### ✅ Configuration Files (Provided)
- [x] `Dockerfile`
- [x] `docker-compose.yml`
- [x] `.gitignore`
- [x] `README.md`
- [x] `SETUP_GUIDE.md`

## 🚀 Quick Start Commands

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Database
createdb fiesta_db
cd backend
alembic upgrade head

# 3. Run
uvicorn app.main:app --reload

# 4. Access
# http://localhost:8000
```

## 📊 Database Models Summary

| Model | Fields | Purpose |
|-------|--------|---------|
| User | email, password, role | Authentication |
| Student | names, contact, program | Student info |
| Unit | code, name, credits | Course units |
| UnitRegistration | student, unit, semester | Enrollments |
| Result | registration, marks, grade | Grades |
| FeeStructure | student, amount, type | Fee billing |
| Payment | student, amount, reference | Payments |
| StudentRequest | student, type, status | Requests |

## 🔐 Default Roles

| Role | Access |
|------|--------|
| `student` | Personal info, fees, units, results, requests |
| `admin` | All student data, manage units, enter results, process requests |

## 🎨 UI Components Reference

### Dashboard Tile
```html
<div class="dashboard-tile">
    <div class="tile-title">Title</div>
    <div class="tile-content">Value</div>
    <p class="text-muted">Description</p>
</div>
```

### Form Container
```html
<div class="form-container">
    <form id="my-form">
        <div class="form-group">
            <label>Label</label>
            <input type="text" class="form-control">
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
</div>
```

### Table
```html
<div class="table-container">
    <table class="table">
        <thead>
            <tr><th>Column</th></tr>
        </thead>
        <tbody id="table-body">
            <!-- Populated by JS -->
        </tbody>
    </table>
</div>
```

## 🔄 API Endpoints Quick Reference

### Authentication
- `POST /api/auth/signup` - Register student
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Student
- `GET /api/student/dashboard` - Dashboard data
- `GET /api/student/profile` - Personal info
- `PUT /api/student/profile` - Update info
- `GET /api/student/fees` - Fee statement
- `GET /api/student/units/available` - Browse units
- `POST /api/student/units/register` - Register unit
- `GET /api/student/results` - View results
- `POST /api/student/requests` - Create request

### Admin
- `GET /admin/students` - List students
- `POST /admin/units` - Create unit
- `POST /admin/results` - Enter results
- `POST /admin/fees` - Create fee
- `POST /admin/payments` - Record payment
- `GET /admin/requests` - List requests
- `PUT /admin/requests/{id}` - Process request
- `GET /admin/reports/summary` - Statistics

## 🎯 Common Tasks

### Add New Field to Student
1. Update `backend/app/models/student.py`
2. Update `backend/app/schemas/student.py`
3. Create migration: `alembic revision --autogenerate -m "Add field"`
4. Apply: `alembic upgrade head`
5. Update frontend forms

### Add New API Endpoint
1. Add route function in `backend/app/routes/`
2. Test in `/docs`
3. Create frontend JS function
4. Add UI element

### Change Color Theme
Edit `frontend/static/css/custom.css`:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
}
```

## 🐛 Debug Commands

```bash
# View logs
docker-compose logs -f web

# Access database
psql -U fiesta_user -d fiesta_db

# Python shell
cd backend
python
>>> from app.database import *
>>> from app.models import *

# Check Redis
redis-cli
> KEYS *

# Test API
curl http://localhost:8000/health
```

## 📝 Environment Variables

| Variable | Development | Production |
|----------|-------------|------------|
| DEBUG | True | False |
| SECRET_KEY | dev-key | Random 32+ chars |
| DATABASE_URL | localhost | Production DB |
| ALLOWED_ORIGINS | localhost:8000 | yourdomain.com |

## 🔒 Security Checklist

- [x] Password hashing (bcrypt)
- [x] JWT tokens
- [x] RBAC implemented
- [x] SQL injection prevention
- [x] XSS protection
- [x] CSRF tokens (implement in forms)
- [x] Rate limiting
- [x] Input validation
- [ ] HTTPS (configure in production)
- [ ] Security headers (add more)

## 📞 Support Resources

- **API Docs**: http://localhost:8000/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Bootstrap Docs**: https://getbootstrap.com/docs

---

**Version**: 1.0.0
**Last Updated**: January 2026
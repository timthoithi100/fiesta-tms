from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import structlog
import os
from pathlib import Path
from app.config import settings
from app.database import init_db, close_db
from app.routes import auth, student, admin
from app.dependencies import RateLimitMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent.parent

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Fiesta TMS", version=settings.app_version)
    await init_db()
    yield
    logger.info("Shutting down Fiesta TMS")
    await close_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Training Management System for Fiesta School",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

app.include_router(auth.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/student/home", response_class=HTMLResponse)
async def student_home(request: Request):
    return templates.TemplateResponse("student/home.html", {"request": request})

@app.get("/student/graduation", response_class=HTMLResponse)
async def student_graduation(request: Request):
    return templates.TemplateResponse("student/graduation.html", {"request": request})

@app.get("/student/clearance", response_class=HTMLResponse)
async def student_clearance(request: Request):
    return templates.TemplateResponse("student/clearance.html", {"request": request})

@app.get("/student/personal_info", response_class=HTMLResponse)
async def student_personal_info(request: Request):
    return templates.TemplateResponse("student/personal_info.html", {"request": request})

@app.get("/student/fees", response_class=HTMLResponse)
async def student_fees(request: Request):
    return templates.TemplateResponse("student/fees.html", {"request": request})

@app.get("/student/unit_registration", response_class=HTMLResponse)
async def student_unit_reg(request: Request):
    return templates.TemplateResponse("student/unit_registration.html", {"request": request})

@app.get("/student/results", response_class=HTMLResponse)
async def student_results(request: Request):
    return templates.TemplateResponse("student/results.html", {"request": request})

@app.get("/admin/home", response_class=HTMLResponse)
async def admin_home(request: Request):
    return templates.TemplateResponse("admin/home.html", {"request": request})

@app.get("/admin/students", response_class=HTMLResponse)
async def admin_students(request: Request):
    return templates.TemplateResponse("admin/students.html", {"request": request})

@app.get("/admin/unit_management", response_class=HTMLResponse)
async def admin_units(request: Request):
    return templates.TemplateResponse("admin/unit_management.html", {"request": request})

@app.get("/admin/clearance_processing", response_class=HTMLResponse)
async def admin_clearance(request: Request):
    return templates.TemplateResponse("admin/clearance_processing.html", {"request": request})

@app.get("/admin/fee_management", response_class=HTMLResponse)
async def admin_fees(request: Request):
    return templates.TemplateResponse("admin/fee_management.html", {"request": request})

@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(request: Request):
    return templates.TemplateResponse("admin/reports.html", {"request": request})

@app.get("/admin/results_management", response_class=HTMLResponse)
async def admin_results(request: Request):
    return templates.TemplateResponse("admin/results_management.html", {"request": request})

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
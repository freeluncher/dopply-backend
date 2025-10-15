from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
from app.api.v1.endpoints import user
from app.api.v1.endpoints import admin_doctor_validation
from app.api.v1.endpoints import token_verify
from app.api.v1.endpoints import refresh
from app.api.v1.endpoints import patient
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from http import HTTPStatus
import time
from starlette.responses import StreamingResponse
import json
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_408_REQUEST_TIMEOUT, HTTP_429_TOO_MANY_REQUESTS, HTTP_502_BAD_GATEWAY, HTTP_503_SERVICE_UNAVAILABLE, HTTP_504_GATEWAY_TIMEOUT

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app with clean metadata
app = FastAPI(
    title="🩺 Dopply Backend API",
    description="""
## Fetal Heart Rate Monitoring System

Simple and clean API untuk monitoring detak jantung janin.
Backend yang disederhanakan dengan fokus pada fitur inti.

### Fitur Utama:
- 🔐 **Authentication**: User management dengan JWT
- 📊 **Monitoring**: Submit dan ambil riwayat monitoring  
- 👩‍⚕️ **Doctor-Patient**: Manajemen relasi dokter-pasien
- 🔔 **Notifications**: Sistem notifikasi real-time
- 👨‍💼 **Admin**: Verifikasi dokter oleh admin

### Quick Start:
1. Register akun sebagai patient/doctor/admin
2. Login untuk mendapatkan access token
3. Gunakan token untuk mengakses fitur monitoring
    """,
    version="2.0.0",
    contact={
        "name": "Dopply Team",
        "email": "support@dopply.com",
    },
    tags_metadata=[
        {
            "name": "Authentication",
            "description": "🔐 User authentication & JWT token management",
        },
        {
            "name": "Monitoring", 
            "description": "📊 Fetal heart rate monitoring & history",
        },
        {
            "name": "Admin",
            "description": "👨‍💼 Admin functions for doctor verification",
        },
    ]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dopply")

# Include routers - simplified and unified
app.include_router(user.router, prefix="/api/v1")

# Use unified monitoring endpoints (replaces both monitoring_simple and monitoring_requirements)
from app.api.v1.endpoints import monitoring
app.include_router(monitoring.router, prefix="/api/v1")

app.include_router(admin_doctor_validation.router, prefix="/api/v1/admin")
app.include_router(token_verify.router, prefix="/api/v1")
app.include_router(refresh.router, prefix="/api/v1/auth")
app.include_router(patient.router, prefix="/api/v1")

# Other endpoint routers
from app.api.v1.endpoints import doctor, auth
app.include_router(doctor.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

# Serve static files for user photos
app.mount(
    "/static/user_photos",
    StaticFiles(directory="app/static/user_photos"),
    name="user_photos"
)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(name)s] %(message)s')
logger = logging.getLogger("dopply")

# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Middleware (e.g., CORS)
@app.on_event("startup")
def startup_event():
    logger.info("Application startup")
    print("Application startup")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutdown")
    print("Application shutdown")

SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "authorization"}
MAX_LOG_BODY_SIZE = 10 * 1024  # 10 KB

def mask_sensitive(data):
    if isinstance(data, dict):
        return {k: ("***" if k.lower() in SENSITIVE_FIELDS else mask_sensitive(v)) for k, v in data.items()}
    elif isinstance(data, list):
        return [mask_sensitive(item) for item in data]
    return data

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "-"
    user_agent = request.headers.get("user-agent", "-")
    auth_header = request.headers.get("authorization", None)
    auth_info = f"auth={auth_header[:15]}..." if auth_header else "auth=None"
    # Log request body jika JSON dan kecil
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="ignore")
    log_body = None
    if request.headers.get("content-type", "").startswith("application/json") and len(body_bytes) < MAX_LOG_BODY_SIZE:
        try:
            body_json = json.loads(body_str)
            log_body = mask_sensitive(body_json)
        except Exception:
            log_body = "<invalid json>"
    logger.info(f"Incoming request: {request.method} {request.url} from {client_host} UA='{user_agent}' {auth_info} body={log_body}")
    # Agar body bisa dibaca downstream, buat ulang request stream
    async def receive():
        return {"type": "http.request", "body": body_bytes}
    request = Request(request.scope, receive)
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        # Log response body jika JSON dan kecil
        resp_body = b""
        if hasattr(response, "body_iterator"):
            resp_body = b"".join([chunk async for chunk in response.body_iterator])
            response.body_iterator = iter([resp_body])
        elif hasattr(response, "body"):
            resp_body = response.body
        log_resp = None
        if response.headers.get("content-type", "").startswith("application/json") and resp_body and len(resp_body) < MAX_LOG_BODY_SIZE:
            try:
                resp_json = json.loads(resp_body.decode("utf-8", errors="ignore"))
                log_resp = mask_sensitive(resp_json)
            except Exception:
                log_resp = "<invalid json>"
        logger.info(f"Response: {request.method} {request.url} - {response.status_code} ({process_time:.2f} ms) from {client_host} resp={log_resp}")
        if resp_body and hasattr(response, "body_iterator"):
            return StreamingResponse(iter([resp_body]), status_code=response.status_code, headers=dict(response.headers))
        return response
    except Exception as exc:
        logger.error(f"Exception during request: {request.method} {request.url} from {client_host} - {exc}")
        raise

def get_error_code(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_error",
    }
    return mapping.get(status_code, "unknown_error")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {request.method} {request.url} - {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "error_code": get_error_code(exc.status_code),
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP error occurred",
            "error_type": "HTTPException",
            "detail": exc.detail if not isinstance(exc.detail, str) else None
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {request.method} {request.url} - {exc}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": HTTP_500_INTERNAL_SERVER_ERROR,
            "error_code": "internal_error",
            "message": "Internal server error",
            "error_type": "InternalServerError",
            "detail": None
        },
    )

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"RequestValidationError: {request.method} {request.url} - {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "error_code": "validation_error",
            "message": "Request validation error",
            "error_type": "RequestValidationError",
            "detail": exc.errors()
        },
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(f"ValidationError: {request.method} {request.url} - {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "error_code": "validation_error",
            "message": "Validation error",
            "error_type": "ValidationError",
            "detail": exc.errors()
        },
    )

@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.error(f"IntegrityError: {request.method} {request.url} - {exc}")
    return JSONResponse(
        status_code=409,
        content={
            "status": "error",
            "code": 409,
            "error_code": "conflict",
            "message": "Database integrity error",
            "error_type": "IntegrityError",
            "detail": str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        },
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Handle 408, 429, 502, 503, 504 with custom message
    if exc.status_code == HTTP_408_REQUEST_TIMEOUT:
        msg = "Request timeout"
        code = "timeout"
    elif exc.status_code == HTTP_429_TOO_MANY_REQUESTS:
        msg = "Too many requests"
        code = "too_many_requests"
    elif exc.status_code == HTTP_502_BAD_GATEWAY:
        msg = "Bad gateway"
        code = "bad_gateway"
    elif exc.status_code == HTTP_503_SERVICE_UNAVAILABLE:
        msg = "Service unavailable"
        code = "service_unavailable"
    elif exc.status_code == HTTP_504_GATEWAY_TIMEOUT:
        msg = "Gateway timeout"
        code = "gateway_timeout"
    else:
        return await http_exception_handler(request, exc)
    logger.warning(f"StarletteHTTPException: {request.method} {request.url} - {exc.status_code} - {msg}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "error_code": code,
            "message": msg,
            "error_type": "StarletteHTTPException",
            "detail": None
        },
    )

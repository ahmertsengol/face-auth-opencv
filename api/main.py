"""
Face Recognition Dashboard - FastAPI Backend
Optimized with enhanced error handling, CORS support, and static file serving
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dashboard")

# Global variables for core modules
face_detector = None
face_recognizer = None
user_manager = None
camera_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for FastAPI application startup and shutdown
    """
    global face_detector, face_recognizer, user_manager, camera_manager
    
    try:
        logger.info("🚀 Starting Face Recognition Dashboard...")
        
        # Import and initialize core modules
        from core.face_detector import FaceDetector
        from core.face_recognizer import FaceRecognizer
        from core.user_manager import UserManager
        from utils.camera import CameraManager
        
        # Initialize components
        face_detector = FaceDetector()
        face_recognizer = FaceRecognizer()
        user_manager = UserManager()
        camera_manager = CameraManager()
        
        logger.info("✅ All core modules initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info("🔄 Cleaning up resources...")
        if camera_manager:
            camera_manager.release()
        logger.info("👋 Dashboard shutdown complete")

# Create FastAPI application with lifespan manager
app = FastAPI(
    title="Face Recognition Dashboard",
    description="Advanced web interface for face recognition system",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Static files and templates setup
static_dir = project_root / "static"
templates_dir = project_root / "templates"

# Ensure directories exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Mount static files with detailed configuration
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"❌ Unhandled error in {request.url}: {str(e)}")
        logger.error(traceback.format_exc())
        
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Internal server error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

# Dependency for checking module availability
async def get_modules():
    """
    Dependency to ensure all modules are available
    """
    if not all([face_detector, face_recognizer, user_manager, camera_manager]):
        raise HTTPException(
            status_code=503,
            detail="Core modules not initialized. Please restart the server."
        )
    return {
        "face_detector": face_detector,
        "face_recognizer": face_recognizer,
        "user_manager": user_manager,
        "camera_manager": camera_manager
    }

# API Routes
@app.get("/", response_class=HTMLResponse, name="dashboard")
async def dashboard(request: Request):
    """
    Main dashboard page with enhanced template context
    """
    try:
        context = {
            "request": request,
            "title": "Face Recognition Dashboard",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
        return templates.TemplateResponse("dashboard.html", context)
    except Exception as e:
        logger.error(f"❌ Template error: {str(e)}")
        raise HTTPException(status_code=500, detail="Template rendering failed")

@app.get("/api/health")
async def health_check():
    """
    Enhanced health check endpoint with detailed status
    """
    try:
        # Check module availability
        modules_status = {
            "face_detector": face_detector is not None,
            "face_recognizer": face_recognizer is not None,
            "user_manager": user_manager is not None,
            "camera_manager": camera_manager is not None
        }
        
        all_healthy = all(modules_status.values())
        
        return {
            "success": True,
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "modules": modules_status,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/users")
async def get_users(modules: dict = Depends(get_modules)):
    """
    Get all users with enhanced error handling and metadata
    """
    try:
        user_manager = modules["user_manager"]
        users_data = user_manager.load_all_users()
        
        # Transform data for API response
        users_list = []
        for user in users_data:
            user_info = {
                "name": user.name,
                "face_count": len(user.face_encodings),
                "created_at": user.created_at,
                "last_seen": None,  # We can add this field later
                "confidence_threshold": 0.6  # Default value
            }
            users_list.append(user_info)
        
        # Sort by creation date (newest first)
        users_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "users": users_list,
            "count": len(users_list),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error loading users: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"Failed to load users: {str(e)}",
            "users": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stats")
async def get_statistics(modules: dict = Depends(get_modules)):
    """
    Get system statistics with enhanced metrics
    """
    try:
        user_manager = modules["user_manager"]
        users_data = user_manager.load_all_users()
        
        # Calculate statistics
        total_users = len(users_data)
        total_encodings = sum(len(user.face_encodings) for user in users_data)
        avg_encodings = round(total_encodings / total_users, 1) if total_users > 0 else 0
        
        # Additional stats (placeholder for now)
        active_users = total_users  # All users are considered active for now
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_face_encodings": total_encodings,
                "average_encodings_per_user": avg_encodings,
                "active_users": active_users,
                "system_uptime": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error loading statistics: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"Failed to load statistics: {str(e)}",
            "stats": {
                "total_users": 0,
                "total_face_encodings": 0,
                "average_encodings_per_user": 0,
                "active_users": 0
            },
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/user/{username}")
async def get_user_details(username: str, modules: dict = Depends(get_modules)):
    """
    Get detailed information about a specific user
    """
    try:
        user_manager = modules["user_manager"]
        user_data = user_manager.load_user(username)
        
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "name": user_data.name,
                "face_count": len(user_data.face_encodings),
                "created_at": user_data.created_at,
                "last_seen": None,  # We can add this field later
                "confidence_threshold": 0.6,  # Default value
                "encodings": len(user_data.face_encodings)  # Don't expose actual encodings
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error loading user {username}: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to load user: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    Custom 404 error handler
    """
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "API endpoint not found",
                "path": request.url.path,
                "timestamp": datetime.now().isoformat()
            }
        )
    else:
        # Redirect to dashboard for non-API routes
        return templates.TemplateResponse("dashboard.html", {"request": request})

# Additional utility endpoints
@app.get("/api/system/info")
async def system_info():
    """
    Get system information
    """
    import platform
    import psutil
    
    try:
        return {
            "success": True,
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Face Recognition Dashboard Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 
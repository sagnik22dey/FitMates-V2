from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import database as db_module
from routes import auth, admin, forms, reports, client
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

db = db_module.db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting FitMates V2 API...")
    await db.connect()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down FitMates V2 API...")
    await db.disconnect()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="FitMates V2 API",
    description="Fitness Client Management System with Dynamic Forms and Reporting",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if not settings.is_production() else None,
    redoc_url="/api/redoc" if not settings.is_production() else None,
)

# Configure CORS with environment-specific settings
allowed_origins = settings.get_allowed_origins()
logger.info(f"Configuring CORS with origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Register API routes
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(forms.router)
app.include_router(reports.router)
app.include_router(client.router)

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    
    Returns system health status including database connectivity
    """
    return {
        "status": "healthy",
        "service": "FitMates V2 API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }

# Serve static files (frontend) - must be last
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Serving frontend from: {frontend_path}")
else:
    logger.warning(f"Frontend directory not found: {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development(),
        log_level=settings.LOG_LEVEL.lower()
    )

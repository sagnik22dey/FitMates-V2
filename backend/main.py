from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import database as db_module
from routes import auth, admin, forms, reports, client

db = db_module.db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()

# Create FastAPI app
app = FastAPI(
    title="FitMates V2 API",
    description="Fitness Client Management System with Dynamic Forms and Reporting",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(forms.router)
app.include_router(reports.router)
app.include_router(client.router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FitMates V2 API",
        "version": "2.0.0"
    }

# Serve static files (frontend) - must be last
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ Serving frontend from: {frontend_path}")
else:
    print(f"⚠️  Frontend directory not found: {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import database as db_module
import models
from utils import verify_password, create_access_token

db = db_module.db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=models.TokenResponse)
async def login(credentials: models.LoginRequest):
    """Login endpoint for both admin and client users"""
    
    # Try to find user in admins table
    admin = await db.fetchrow(
        "SELECT id, email, password FROM admins WHERE email = $1",
        credentials.email
    )
    
    if admin:
        # Verify admin password
        if verify_password(credentials.password, admin['password']):
            # Create JWT token
            token = create_access_token({
                "sub": str(admin['id']),
                "email": admin['email'],
                "role": "admin"
            })
            
            return models.TokenResponse(
                access_token=token,
                role="admin",
                user_id=str(admin['id']),
                email=admin['email'],
                name="Admin"
            )
    
    # Try to find user in clients table
    client = await db.fetchrow(
        "SELECT id, email, password, name FROM clients WHERE email = $1",
        credentials.email
    )
    
    if client:
        # Verify client password
        if verify_password(credentials.password, client['password']):
            # Create JWT token
            token = create_access_token({
                "sub": str(client['id']),
                "email": client['email'],
                "role": "client"
            })
            
            return models.TokenResponse(
                access_token=token,
                role="client",
                user_id=str(client['id']),
                email=client['email'],
                name=client['name']
            )
    
    # Invalid credentials
    raise HTTPException(status_code=401, detail="Invalid email or password")

@router.get("/verify")
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token"""
    from utils import get_token_data
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    token_data = get_token_data(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "valid": True,
        "user_id": token_data['user_id'],
        "role": token_data['role'],
        "email": token_data['email']
    }

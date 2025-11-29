from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import config as config_module

settings = config_module.settings

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_token_data(token: str) -> Optional[Dict]:
    """Extract data from token"""
    payload = verify_token(token)
    if payload is None:
        return None
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role"),
        "email": payload.get("email")
    }

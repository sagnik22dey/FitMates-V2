from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
import logging
import config as config_module

settings = config_module.settings
logger = logging.getLogger(__name__)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing token payload (user_id, role, email)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    logger.debug(f"Created access token for user: {data.get('email')}")
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None

def get_token_data(token: str) -> Optional[Dict]:
    """
    Extract user data from token
    
    Args:
        token: JWT token string
        
    Returns:
        Dict with user_id, role, and email or None if invalid
    """
    payload = verify_token(token)
    if payload is None:
        return None
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role"),
        "email": payload.get("email")
    }

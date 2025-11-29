"""
Utility helper functions for the FitMates V2 application
"""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def parse_jsonb_field(data: Any) -> Dict:
    """
    Parse JSONB field from database
    
    Args:
        data: JSONB data which could be string or dict
        
    Returns:
        Parsed dictionary
    """
    if data is None:
        return {}
    
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSONB data: {e}")
            return {}
    
    if isinstance(data, dict):
        return data
    
    logger.warning(f"Unexpected JSONB data type: {type(data)}")
    return {}


def serialize_jsonb_field(data: Any) -> str:
    """
    Serialize data to JSONB string for database
    
    Args:
        data: Dictionary or JSON-serializable data
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize data to JSON: {e}")
        raise ValueError(f"Cannot serialize data to JSON: {str(e)}")


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime to ISO format string
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO formatted string or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def safe_float_conversion(value: Any) -> Optional[float]:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        
    Returns:
        Float value or None
    """
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert {value} to float")
        return None


def create_response_dict(record: Any, fields: Dict[str, str]) -> Dict:
    """
    Create response dictionary from database record
    
    Args:
        record: Database record
        fields: Dictionary mapping field names to types
        
    Returns:
        Formatted response dictionary
    """
    if not record:
        return {}
    
    result = {}
    for field, field_type in fields.items():
        value = record.get(field)
        
        if field_type == 'datetime':
            result[field] = format_datetime(value)
        elif field_type == 'float':
            result[field] = safe_float_conversion(value)
        elif field_type == 'jsonb':
            result[field] = parse_jsonb_field(value)
        elif field_type == 'str':
            result[field] = str(value) if value is not None else None
        else:
            result[field] = value
    
    return result


class StandardResponse:
    """Standard API response formatter"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict:
        """
        Create success response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted success response
        """
        response = {
            "success": True,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, code: str = "ERROR", details: Any = None) -> Dict:
        """
        Create error response
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
            
        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
        if details is not None:
            response["error"]["details"] = details
        return response
    
    @staticmethod
    def paginated(data: list, page: int, page_size: int, total: int) -> Dict:
        """
        Create paginated response
        
        Args:
            data: List of items
            page: Current page number
            page_size: Items per page
            total: Total number of items
            
        Returns:
            Formatted paginated response
        """
        return {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
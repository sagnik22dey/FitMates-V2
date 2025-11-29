from fastapi import APIRouter, HTTPException, Depends
import database as db_module
import models
from routes.forms import verify_auth

db = db_module.db

router = APIRouter(prefix="/api/client", tags=["Client"])

@router.get("/profile", response_model=models.ClientResponse)
async def get_my_profile(user: dict = Depends(verify_auth)):
    """Get current client's profile"""
    
    # Only clients can access this endpoint
    if user['role'] != 'client':
        raise HTTPException(status_code=403, detail="Client access only")
    
    client = await db.fetchrow("""
        SELECT id, name, email, dob, height, weight, mobile, medical_history, created_at
        FROM clients
        WHERE id = $1
    """, int(user['user_id']))
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {
        "id": client['id'],
        "name": client['name'],
        "email": client['email'],
        "dob": client['dob'],
        "height": float(client['height']) if client['height'] else None,
        "weight": float(client['weight']) if client['weight'] else None,
        "mobile": client['mobile'],
        "medical_history": client['medical_history'],
        "created_at": client['created_at'].isoformat()
    }

@router.put("/profile", response_model=models.ClientResponse)
async def update_my_profile(client_update: models.ClientUpdate, user: dict = Depends(verify_auth)):
    """Update current client's profile"""
    
    # Only clients can access this endpoint
    if user['role'] != 'client':
        raise HTTPException(status_code=403, detail="Client access only")
    
    client_id = int(user['user_id'])
    
    # Build update query dynamically
    update_fields = []
    values = []
    param_count = 1
    
    if client_update.name is not None:
        update_fields.append(f"name = ${param_count}")
        values.append(client_update.name)
        param_count += 1
    
    if client_update.dob is not None:
        update_fields.append(f"dob = ${param_count}")
        values.append(client_update.dob)
        param_count += 1
    
    if client_update.height is not None:
        update_fields.append(f"height = ${param_count}")
        values.append(client_update.height)
        param_count += 1
    
    if client_update.weight is not None:
        update_fields.append(f"weight = ${param_count}")
        values.append(client_update.weight)
        param_count += 1
    
    if client_update.mobile is not None:
        update_fields.append(f"mobile = ${param_count}")
        values.append(client_update.mobile)
        param_count += 1
    
    if client_update.medical_history is not None:
        update_fields.append(f"medical_history = ${param_count}")
        values.append(client_update.medical_history)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Add updated_at
    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
    
    # Add client_id to values
    values.append(client_id)
    
    # Execute update
    query = f"""
        UPDATE clients
        SET {', '.join(update_fields)}
        WHERE id = ${param_count}
        RETURNING id, name, email, dob, height, weight, mobile, medical_history, created_at
    """
    
    updated_client = await db.fetchrow(query, *values)
    
    return {
        "id": updated_client['id'],
        "name": updated_client['name'],
        "email": updated_client['email'],
        "dob": updated_client['dob'],
        "height": float(updated_client['height']) if updated_client['height'] else None,
        "weight": float(updated_client['weight']) if updated_client['weight'] else None,
        "mobile": updated_client['mobile'],
        "medical_history": updated_client['medical_history'],
        "created_at": updated_client['created_at'].isoformat()
    }

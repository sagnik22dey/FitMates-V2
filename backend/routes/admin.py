from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
import database as db_module
import models
from utils import hash_password, get_token_data

db = db_module.db

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Dependency to verify admin role
async def verify_admin(authorization: Optional[str] = Header(None)):
    """Verify that the user is an admin"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.split(" ")[1]
    token_data = get_token_data(token)
    
    if not token_data or token_data['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return token_data

@router.get("/dashboard/analytics")
async def get_dashboard_analytics(admin: dict = Depends(verify_admin)):
    """Get analytics data for admin dashboard"""
    
    # Get total clients count
    total_clients = await db.fetchval("SELECT COUNT(*) FROM clients")
    
    # Get total forms count
    total_forms = await db.fetchval("SELECT COUNT(*) FROM forms")
    
    # Get published forms count
    published_forms = await db.fetchval(
        "SELECT COUNT(*) FROM forms WHERE status = 'published'"
    )
    
    # Get total submissions count
    total_submissions = await db.fetchval("SELECT COUNT(*) FROM submissions")
    
    # Get total reports count
    total_reports = await db.fetchval("SELECT COUNT(*) FROM reports")
    
    # Get recent submissions (last 5)
    recent_submissions = await db.fetch("""
        SELECT s.id, s.submitted_at, c.name as client_name, f.title as form_title
        FROM submissions s
        JOIN clients c ON s.client_id = c.id
        JOIN forms f ON s.form_id = f.id
        ORDER BY s.submitted_at DESC
        LIMIT 5
    """)
    
    return {
        "total_clients": total_clients,
        "total_forms": total_forms,
        "published_forms": published_forms,
        "total_submissions": total_submissions,
        "total_reports": total_reports,
        "recent_activity": [
            {
                "id": str(row['id']),
                "client_name": row['client_name'],
                "form_title": row['form_title'],
                "submitted_at": row['submitted_at'].isoformat()
            }
            for row in recent_submissions
        ]
    }

@router.get("/clients", response_model=List[models.ClientResponse])
async def get_all_clients(admin: dict = Depends(verify_admin)):
    """Get all clients"""
    
    clients = await db.fetch("""
        SELECT id, name, email, dob, height, weight, mobile, medical_history, created_at
        FROM clients
        ORDER BY created_at DESC
    """)
    
    return [
        {
            "id": row['id'],
            "name": row['name'],
            "email": row['email'],
            "dob": row['dob'],
            "height": float(row['height']) if row['height'] else None,
            "weight": float(row['weight']) if row['weight'] else None,
            "mobile": row['mobile'],
            "medical_history": row['medical_history'],
            "created_at": row['created_at'].isoformat()
        }
        for row in clients
    ]

@router.get("/clients/{client_id}", response_model=models.ClientResponse)
async def get_client(client_id: int, admin: dict = Depends(verify_admin)):
    """Get a specific client by ID"""
    
    client = await db.fetchrow("""
        SELECT id, name, email, dob, height, weight, mobile, medical_history, created_at
        FROM clients
        WHERE id = $1
    """, client_id)
    
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

@router.post("/clients", response_model=models.ClientResponse)
async def create_client(client: models.ClientCreate, admin: dict = Depends(verify_admin)):
    """Create a new client"""
    
    # Check if email already exists
    existing = await db.fetchval("SELECT id FROM clients WHERE email = $1", client.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(client.password)
    
    # Insert client
    new_client = await db.fetchrow("""
        INSERT INTO clients (name, email, password, dob, height, weight, mobile, medical_history)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id, name, email, dob, height, weight, mobile, medical_history, created_at
    """, client.name, client.email, hashed_password, client.dob, client.height, 
        client.weight, client.mobile, client.medical_history)
    
    return {
        "id": new_client['id'],
        "name": new_client['name'],
        "email": new_client['email'],
        "dob": new_client['dob'],
        "height": float(new_client['height']) if new_client['height'] else None,
        "weight": float(new_client['weight']) if new_client['weight'] else None,
        "mobile": new_client['mobile'],
        "medical_history": new_client['medical_history'],
        "created_at": new_client['created_at'].isoformat()
    }

@router.put("/clients/{client_id}", response_model=models.ClientResponse)
async def update_client(client_id: int, client_update: models.ClientUpdate, admin: dict = Depends(verify_admin)):
    """Update a client"""
    
    # Check if client exists
    existing = await db.fetchrow("SELECT id FROM clients WHERE id = $1", client_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")
    
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

@router.delete("/clients/{client_id}")
async def delete_client(client_id: int, admin: dict = Depends(verify_admin)):
    """Delete a client"""
    
    # Check if client exists
    existing = await db.fetchrow("SELECT id FROM clients WHERE id = $1", client_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Delete client (cascade will handle related records)
    await db.execute("DELETE FROM clients WHERE id = $1", client_id)
    
    return {"message": "Client deleted successfully"}

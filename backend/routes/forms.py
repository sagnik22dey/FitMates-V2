from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List
import json
import models
import database as db_module
from utils.auth import get_token_data

db = db_module.db

router = APIRouter(prefix="/api/forms", tags=["Forms"])

# Dependency to verify authentication
async def verify_auth(authorization: str = Header(None)):
    """Verify that the user is authenticated"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.split(" ")[1]
    token_data = get_token_data(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token_data

@router.get("/client/{client_id}", response_model=List[models.FormResponse])
async def get_client_forms(client_id: int, user: dict = Depends(verify_auth)):
    """Get all forms for a specific client"""
    
    # Verify access (admin can see all, client can only see their own)
    if user['role'] != 'admin' and str(user['user_id']) != str(client_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        forms = await db.fetch("""
            SELECT id, client_id, title, data, status, is_template, created_at, updated_at
            FROM forms
            WHERE client_id = $1
            ORDER BY created_at DESC
        """, client_id)
        
        result = []
        for row in forms:
            # Handle JSONB data field - it might be a string or dict
            data = row['data']
            if isinstance(data, str):
                data = json.loads(data)
            
            result.append({
                "id": str(row['id']),
                "client_id": row['client_id'],
                "title": row['title'],
                "data": data,
                "status": row['status'],
                "is_template": row['is_template'],
                "created_at": row['created_at'].isoformat(),
                "updated_at": row['updated_at'].isoformat()
            })
        
        return result
    except Exception as e:
        print(f"Error in get_client_forms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/published/{client_id}", response_model=List[models.FormResponse])
async def get_published_forms(client_id: int, user: dict = Depends(verify_auth)):
    """Get published forms for a client (for client dashboard)"""
    
    # Verify access
    if user['role'] != 'admin' and str(user['user_id']) != str(client_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        forms = await db.fetch("""
            SELECT id, client_id, title, data, status, is_template, created_at, updated_at
            FROM forms
            WHERE client_id = $1 AND status = 'published'
            ORDER BY created_at DESC
        """, client_id)
        
        result = []
        for row in forms:
            data = row['data']
            if isinstance(data, str):
                data = json.loads(data)
            
            result.append({
                "id": str(row['id']),
                "client_id": row['client_id'],
                "title": row['title'],
                "data": data,
                "status": row['status'],
                "is_template": row['is_template'],
                "created_at": row['created_at'].isoformat(),
                "updated_at": row['updated_at'].isoformat()
            })
        
        return result
    except Exception as e:
        print(f"Error in get_published_forms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[models.FormResponse])
async def get_templates(user: dict = Depends(verify_auth)):
    """Get all form templates"""
    
    # Only admin can access templates
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        templates = await db.fetch("""
            SELECT id, client_id, title, data, status, is_template, created_at, updated_at
            FROM forms
            WHERE is_template = true
            ORDER BY created_at DESC
        """)
        
        result = []
        for row in templates:
            data = row['data']
            if isinstance(data, str):
                data = json.loads(data)
            
            result.append({
                "id": str(row['id']),
                "client_id": row['client_id'],
                "title": row['title'],
                "data": data,
                "status": row['status'],
                "is_template": row['is_template'],
                "created_at": row['created_at'].isoformat(),
                "updated_at": row['updated_at'].isoformat()
            })
        
        return result
    except Exception as e:
        print(f"Error in get_templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=models.FormResponse)
async def create_form(form: models.FormCreate, user: dict = Depends(verify_auth)):
    """Create a new form"""
    
    # Only admin can create forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Verify client exists
        client = await db.fetchval("SELECT id FROM clients WHERE id = $1", form.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Insert form
        new_form = await db.fetchrow("""
            INSERT INTO forms (client_id, title, data, status, is_template)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, client_id, title, data, status, is_template, created_at, updated_at
        """, form.client_id, form.title, json.dumps(form.data), form.status, form.is_template)
        
        # Handle JSONB data field
        data = new_form['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(new_form['id']),
            "client_id": new_form['client_id'],
            "title": new_form['title'],
            "data": data,
            "status": new_form['status'],
            "is_template": new_form['is_template'],
            "created_at": new_form['created_at'].isoformat(),
            "updated_at": new_form['updated_at'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{form_id}", response_model=models.FormResponse)
async def update_form(form_id: str, form_update: models.FormUpdate, user: dict = Depends(verify_auth)):
    """Update a form"""
    
    # Only admin can update forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if form exists
    existing = await db.fetchrow("SELECT id FROM forms WHERE id = $1", form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Build update query
    update_fields = []
    values = []
    param_count = 1
    
    if form_update.title is not None:
        update_fields.append(f"title = ${param_count}")
        values.append(form_update.title)
        param_count += 1
    
    if form_update.data is not None:
        update_fields.append(f"data = ${param_count}")
        values.append(json.dumps(form_update.data))
        param_count += 1
    
    if form_update.status is not None:
        update_fields.append(f"status = ${param_count}")
        values.append(form_update.status)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Add updated_at
    update_fields.append(f"updated_at = NOW()")
    
    # Add form_id to values
    values.append(form_id)
    
    try:
        # Update form
        query = f"""
            UPDATE forms
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING id, client_id, title, data, status, is_template, created_at, updated_at
        """
        
        updated_form = await db.fetchrow(query, *values)
        
        # Handle JSONB data field
        data = updated_form['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(updated_form['id']),
            "client_id": updated_form['client_id'],
            "title": updated_form['title'],
            "data": data,
            "status": updated_form['status'],
            "is_template": updated_form['is_template'],
            "created_at": updated_form['created_at'].isoformat(),
            "updated_at": updated_form['updated_at'].isoformat()
        }
    except Exception as e:
        print(f"Error in update_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{form_id}/publish", response_model=models.FormResponse)
async def publish_form(form_id: str, user: dict = Depends(verify_auth)):
    """Publish a form to client"""
    
    # Only admin can publish forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Update form status to published
        updated_form = await db.fetchrow("""
            UPDATE forms
            SET status = 'published', updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING id, client_id, title, data, status, is_template, created_at, updated_at
        """, form_id)
        
        if not updated_form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Handle JSONB data field
        data = updated_form['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(updated_form['id']),
            "client_id": updated_form['client_id'],
            "title": updated_form['title'],
            "data": data,
            "status": updated_form['status'],
            "is_template": updated_form['is_template'],
            "created_at": updated_form['created_at'].isoformat(),
            "updated_at": updated_form['updated_at'].isoformat()
        }
    except Exception as e:
        print(f"Error in publish_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{form_id}/unpublish", response_model=models.FormResponse)
async def unpublish_form(form_id: str, user: dict = Depends(verify_auth)):
    """Unpublish a form (revert to draft)"""
    
    # Only admin can unpublish forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Update form status to draft
        updated_form = await db.fetchrow("""
            UPDATE forms
            SET status = 'draft', updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING id, client_id, title, data, status, is_template, created_at, updated_at
        """, form_id)
        
        if not updated_form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Handle JSONB data field
        data = updated_form['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(updated_form['id']),
            "client_id": updated_form['client_id'],
            "title": updated_form['title'],
            "data": data,
            "status": updated_form['status'],
            "is_template": updated_form['is_template'],
            "created_at": updated_form['created_at'].isoformat(),
            "updated_at": updated_form['updated_at'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in unpublish_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{form_id}/copy", response_model=models.FormResponse)
async def copy_form(form_id: str, client_id: int, user: dict = Depends(verify_auth)):
    """Copy a form as a template or to another client"""
    
    # Only admin can copy forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get original form
        original = await db.fetchrow("""
            SELECT title, data FROM forms WHERE id = $1
        """, form_id)
        
        if not original:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Create copy
        new_form = await db.fetchrow("""
            INSERT INTO forms (client_id, title, data, status, is_template)
            VALUES ($1, $2, $3, 'draft', false)
            RETURNING id, client_id, title, data, status, is_template, created_at, updated_at
        """, client_id, f"{original['title']} (Copy)", original['data'])
        
        # Handle JSONB data field
        data = new_form['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(new_form['id']),
            "client_id": new_form['client_id'],
            "title": new_form['title'],
            "data": data,
            "status": new_form['status'],
            "is_template": new_form['is_template'],
            "created_at": new_form['created_at'].isoformat(),
            "updated_at": new_form['updated_at'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in copy_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{form_id}")
async def delete_form(form_id: str, user: dict = Depends(verify_auth)):
    """Delete a form"""
    
    # Only admin can delete forms
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if form exists
    existing = await db.fetchrow("SELECT id FROM forms WHERE id = $1", form_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Delete form
    await db.execute("DELETE FROM forms WHERE id = $1", form_id)
    
    return {"message": "Form deleted successfully"}

# Submission endpoints
@router.post("/submit", response_model=models.SubmissionResponse)
async def submit_form(submission: models.SubmissionCreate, user: dict = Depends(verify_auth)):
    """Submit a form (client side) - Creates new or updates existing submission"""
    
    # Verify client is submitting their own form
    if user['role'] == 'client' and str(user['user_id']) != str(submission.client_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Verify form exists
        form = await db.fetchrow("""
            SELECT id, status FROM forms WHERE id = $1 AND client_id = $2
        """, submission.form_id, submission.client_id)
        
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Check if submission already exists
        existing_submission = await db.fetchrow("""
            SELECT id FROM submissions 
            WHERE client_id = $1 AND form_id = $2
        """, submission.client_id, submission.form_id)
        
        if existing_submission:
            # UPDATE existing submission
            updated_submission = await db.fetchrow("""
                UPDATE submissions 
                SET data = $1, submitted_at = CURRENT_TIMESTAMP
                WHERE id = $2
                RETURNING id, client_id, form_id, data, submitted_at
            """, json.dumps(submission.data), existing_submission['id'])
            
            result_submission = updated_submission
        else:
            # INSERT new submission
            new_submission = await db.fetchrow("""
                INSERT INTO submissions (client_id, form_id, data)
                VALUES ($1, $2, $3)
                RETURNING id, client_id, form_id, data, submitted_at
            """, submission.client_id, submission.form_id, json.dumps(submission.data))
            
            result_submission = new_submission
        
        # Note: We don't update form status here because the database constraint
        # only allows 'draft' and 'published'. Completion status is determined
        # by checking if a submission exists in the submissions table.
        
        # Handle JSONB data field
        data = result_submission['data']
        if isinstance(data, str):
            data = json.loads(data)
        
        return {
            "id": str(result_submission['id']),
            "client_id": result_submission['client_id'],
            "form_id": str(result_submission['form_id']),
            "data": data,
            "submitted_at": result_submission['submitted_at'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in submit_form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions/client/{client_id}", response_model=List[models.SubmissionResponse])
async def get_client_submissions(client_id: int, user: dict = Depends(verify_auth)):
    """Get all submissions for a client"""
    
    # Verify access
    if user['role'] != 'admin' and str(user['user_id']) != str(client_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        submissions = await db.fetch("""
            SELECT id, client_id, form_id, data, submitted_at
            FROM submissions
            WHERE client_id = $1
            ORDER BY submitted_at DESC
        """, client_id)
        
        result = []
        for row in submissions:
            data = row['data']
            if isinstance(data, str):
                data = json.loads(data)
                
            result.append({
                "id": str(row['id']),
                "client_id": row['client_id'],
                "form_id": str(row['form_id']),
                "data": data,
                "submitted_at": row['submitted_at'].isoformat()
            })
        
        return result
    except Exception as e:
        print(f"Error in get_client_submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


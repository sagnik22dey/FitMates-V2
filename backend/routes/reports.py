from fastapi import APIRouter, HTTPException, Depends
from typing import List
import json
import database as db_module
import models
from utils.report_generator import generate_report
from routes.forms import verify_auth

db = db_module.db

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.post("/generate", response_model=models.ReportResponse)
async def generate_report_from_submission(report_request: models.ReportCreate, user: dict = Depends(verify_auth)):
    """Generate a report from a submission"""
    
    # Only admin can generate reports
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get submission data
    submission = await db.fetchrow("""
        SELECT id, client_id, form_id, data
        FROM submissions
        WHERE id = $1
    """, report_request.submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Verify client_id matches
    if submission['client_id'] != report_request.client_id:
        raise HTTPException(status_code=400, detail="Client ID mismatch")
    
    # Get form data (for targets)
    form = await db.fetchrow("""
        SELECT data FROM forms WHERE id = $1
    """, str(submission['form_id']))
    
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Generate report
    report_data = generate_report(
        form_data=form['data'],
        submission_data=submission['data'],
        period=report_request.period
    )
    
    # Save report to database
    new_report = await db.fetchrow("""
        INSERT INTO reports (client_id, submission_id, generated_report_data, period)
        VALUES ($1, $2, $3, $4)
        RETURNING id, client_id, submission_id, generated_report_data, period, created_at
    """, report_request.client_id, report_request.submission_id, 
        json.dumps(report_data), report_request.period)
    
    return {
        "id": str(new_report['id']),
        "client_id": new_report['client_id'],
        "submission_id": str(new_report['submission_id']),
        "generated_report_data": new_report['generated_report_data'],
        "period": new_report['period'],
        "created_at": new_report['created_at'].isoformat()
    }

@router.get("/client/{client_id}", response_model=List[models.ReportResponse])
async def get_client_reports(client_id: int, user: dict = Depends(verify_auth)):
    """Get all reports for a client"""
    
    # Verify access
    if user['role'] != 'admin' and str(user['user_id']) != str(client_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    reports = await db.fetch("""
        SELECT id, client_id, submission_id, generated_report_data, period, created_at
        FROM reports
        WHERE client_id = $1
        ORDER BY created_at DESC
    """, client_id)
    
    return [
        {
            "id": str(row['id']),
            "client_id": row['client_id'],
            "submission_id": str(row['submission_id']),
            "generated_report_data": row['generated_report_data'],
            "period": row['period'],
            "created_at": row['created_at'].isoformat()
        }
        for row in reports
    ]

@router.get("/{report_id}", response_model=models.ReportResponse)
async def get_report(report_id: str, user: dict = Depends(verify_auth)):
    """Get a specific report"""
    
    report = await db.fetchrow("""
        SELECT id, client_id, submission_id, generated_report_data, period, created_at
        FROM reports
        WHERE id = $1
    """, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Verify access
    if user['role'] != 'admin' and str(user['user_id']) != str(report['client_id']):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": str(report['id']),
        "client_id": report['client_id'],
        "submission_id": str(report['submission_id']),
        "generated_report_data": report['generated_report_data'],
        "period": report['period'],
        "created_at": report['created_at'].isoformat()
    }

@router.delete("/{report_id}")
async def delete_report(report_id: str, user: dict = Depends(verify_auth)):
    """Delete a report"""
    
    # Only admin can delete reports
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if report exists
    existing = await db.fetchrow("SELECT id FROM reports WHERE id = $1", report_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Delete report
    await db.execute("DELETE FROM reports WHERE id = $1", report_id)
    
    return {"message": "Report deleted successfully"}

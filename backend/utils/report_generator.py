from typing import Dict, List
import json
from datetime import datetime

def calculate_achievement(actual: float, target: float) -> float:
    """Calculate achievement percentage"""
    if target == 0:
        return 100.0 if actual == 0 else 0.0
    return round((actual / target) * 100, 2)

def calculate_variance(actual: float, target: float) -> float:
    """Calculate variance between actual and target"""
    return round(actual - target, 2)

def generate_report(form_data: dict, submission_data: dict, period: str = "weekly") -> dict:
    """
    Generate a report comparing form targets with submission actuals
    
    Args:
        form_data: The form structure with target values
        submission_data: The submitted data with actual values
        period: Report period ('weekly' or 'monthly')
    
    Returns:
        Dictionary containing the generated report
    """
    
    metrics = []
    total_achievement = 0
    fields_count = 0
    
    # Extract fields from form data
    form_fields = form_data.get('fields', [])
    
    for field in form_fields:
        field_id = field.get('id')
        field_label = field.get('label', field_id)
        field_type = field.get('type', 'text')
        target = field.get('target')
        unit = field.get('unit', '')
        
        # Get actual value from submission
        actual = submission_data.get(field_id)
        
        # Only process numeric fields with targets
        if field_type in ['number', 'integer'] and target is not None and actual is not None:
            try:
                target_val = float(target)
                actual_val = float(actual)
                
                achievement = calculate_achievement(actual_val, target_val)
                variance = calculate_variance(actual_val, target_val)
                
                # Determine status
                if achievement >= 100:
                    status = "Excellent"
                    status_color = "green"
                elif achievement >= 80:
                    status = "Good"
                    status_color = "blue"
                elif achievement >= 60:
                    status = "Fair"
                    status_color = "yellow"
                else:
                    status = "Needs Improvement"
                    status_color = "red"
                
                metrics.append({
                    "field": field_label,
                    "target": target_val,
                    "actual": actual_val,
                    "unit": unit,
                    "achievement": achievement,
                    "variance": variance,
                    "status": status,
                    "status_color": status_color
                })
                
                total_achievement += achievement
                fields_count += 1
                
            except (ValueError, TypeError):
                # Skip fields with invalid numeric values
                continue
    
    # Calculate overall score
    overall_score = round(total_achievement / fields_count, 2) if fields_count > 0 else 0
    
    # Generate summary
    if overall_score >= 90:
        summary = "Outstanding performance! Keep up the excellent work."
    elif overall_score >= 75:
        summary = "Great progress! You're on the right track."
    elif overall_score >= 60:
        summary = "Good effort. Focus on areas that need improvement."
    else:
        summary = "More effort needed. Let's work together to improve your results."
    
    # Count achievements by status
    excellent_count = sum(1 for m in metrics if m['status'] == "Excellent")
    good_count = sum(1 for m in metrics if m['status'] == "Good")
    fair_count = sum(1 for m in metrics if m['status'] == "Fair")
    needs_improvement_count = sum(1 for m in metrics if m['status'] == "Needs Improvement")
    
    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "overall_score": overall_score,
        "summary": summary,
        "metrics": metrics,
        "statistics": {
            "total_metrics": fields_count,
            "excellent": excellent_count,
            "good": good_count,
            "fair": fair_count,
            "needs_improvement": needs_improvement_count
        }
    }

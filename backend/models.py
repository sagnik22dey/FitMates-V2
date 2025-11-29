from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# Authentication Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    email: str
    name: Optional[str] = None

# Client Models
class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    dob: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    mobile: Optional[str] = None
    medical_history: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    mobile: Optional[str] = None
    medical_history: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    dob: Optional[date]
    height: Optional[float]
    weight: Optional[float]
    mobile: Optional[str]
    medical_history: Optional[str]
    created_at: str

# Form Models
class FormCreate(BaseModel):
    client_id: int
    title: str
    data: dict
    status: str = "draft"
    is_template: bool = False

class FormUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[dict] = None
    status: Optional[str] = None

class FormResponse(BaseModel):
    id: str
    client_id: int
    title: str
    data: dict
    status: str
    is_template: bool
    created_at: str
    updated_at: str

# Submission Models
class SubmissionCreate(BaseModel):
    client_id: int
    form_id: str
    data: dict

class SubmissionResponse(BaseModel):
    id: str
    client_id: int
    form_id: str
    data: dict
    submitted_at: str

# Report Models
class ReportCreate(BaseModel):
    client_id: int
    submission_id: str
    period: str  # 'weekly' or 'monthly'

class ReportResponse(BaseModel):
    id: str
    client_id: int
    submission_id: str
    generated_report_data: dict
    period: str
    created_at: str

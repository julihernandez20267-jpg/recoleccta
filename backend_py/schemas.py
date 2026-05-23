from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"
    displayName: Optional[str] = None
    photoURL: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserGoogleLogin(BaseModel):
    idToken: str
    role: str = "user"

class UserOut(UserBase):
    uid: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    success: bool = True
    message: str
    data: dict

class RecoverPassword(BaseModel):
    email: EmailStr

class ResetPasswordWithOTP(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class RouteAssignmentCreate(BaseModel):
    guardianId: int
    routeId: str

class RouteAssignmentOut(BaseModel):
    guardianId: int
    routeId: str
    updatedAt: datetime

    class Config:
        from_attributes = True

class UserUpdateRole(BaseModel):
    userId: int
    role: str

class ProfileUpdate(BaseModel):
    displayName: Optional[str] = None
    photoURL: Optional[str] = None

class GuardianCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    displayName: str

# Route Schemas
class RouteCreate(BaseModel):
    id: str
    name: str
    zone: str
    points: str  # JSON string of coordinates

class RouteOut(BaseModel):
    id: str
    name: str
    zone: str
    points: str
    created_at: datetime

    class Config:
        from_attributes = True

# Report Schemas
class ReportCreate(BaseModel):
    address: str
    neighborhood: Optional[str] = None
    type: str
    latitude: float
    longitude: float
    observations: Optional[str] = None
    reporter_name: Optional[str] = None
    has_evidence: bool = False

class ReportOut(BaseModel):
    id: int
    address: str
    neighborhood: Optional[str] = None
    status: str
    type: str
    latitude: float
    longitude: float
    observations: Optional[str] = None
    reporter_name: Optional[str] = None
    has_evidence: bool
    assigned_guardian_id: Optional[int] = None
    assignedGuardianName: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReportStatusUpdate(BaseModel):
    status: str
    guardian_name: Optional[str] = None


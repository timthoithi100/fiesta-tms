from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.student import Gender


class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    date_of_birth: date
    phone_number: str = Field(..., min_length=10, max_length=20)
    city: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    program: str = Field(..., min_length=1, max_length=100)


class StudentCreate(StudentBase):
    email: EmailStr
    password: str = Field(..., min_length=8)


class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=255)


class StudentResponse(StudentBase):
    id: UUID
    user_id: UUID
    student_id: str
    enrollment_date: date
    is_graduated: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    student_info: StudentResponse
    registered_units_count: int
    attempted_units_count: int
    total_billed: float
    total_paid: float
    fee_balance: float
    
    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.unit import Semester, RegistrationStatus
from decimal import Decimal


class UnitBase(BaseModel):
    unit_code: str = Field(..., min_length=1, max_length=20)
    unit_name: str = Field(..., min_length=1, max_length=200)
    credits: int = Field(..., ge=1, le=6)
    description: Optional[str] = Field(None, max_length=500)


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    unit_name: Optional[str] = Field(None, min_length=1, max_length=200)
    credits: Optional[int] = Field(None, ge=1, le=6)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[str] = None


class UnitResponse(UnitBase):
    id: UUID
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UnitRegistrationCreate(BaseModel):
    unit_id: UUID
    semester: Semester
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")


class UnitRegistrationResponse(BaseModel):
    id: UUID
    student_id: UUID
    unit_id: UUID
    semester: Semester
    academic_year: str
    status: RegistrationStatus
    registration_date: datetime
    unit: UnitResponse
    
    class Config:
        from_attributes = True


class ResultBase(BaseModel):
    marks: Optional[Decimal] = Field(None, ge=0, le=100)
    grade: Optional[str] = Field(None, max_length=2)
    remarks: Optional[str] = Field(None, max_length=200)


class ResultCreate(ResultBase):
    registration_id: UUID


class ResultUpdate(ResultBase):
    is_published: Optional[str] = None


class ResultResponse(ResultBase):
    id: UUID
    registration_id: UUID
    is_published: str
    entered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ResultWithUnit(ResultResponse):
    registration: UnitRegistrationResponse
    
    class Config:
        from_attributes = True
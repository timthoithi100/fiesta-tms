from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.request import RequestType, RequestStatus


class StudentRequestBase(BaseModel):
    request_type: RequestType
    student_remarks: Optional[str] = Field(None, max_length=1000)


class StudentRequestCreate(StudentRequestBase):
    pass


class StudentRequestUpdate(BaseModel):
    status: RequestStatus
    admin_remarks: Optional[str] = Field(None, max_length=1000)


class StudentRequestResponse(StudentRequestBase):
    id: UUID
    student_id: UUID
    status: RequestStatus
    request_date: datetime
    processed_at: Optional[datetime]
    admin_remarks: Optional[str]
    
    class Config:
        from_attributes = True
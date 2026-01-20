from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.fee import FeeType, PaymentMethod


class FeeStructureBase(BaseModel):
    fee_type: FeeType
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    semester: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=200)


class FeeStructureCreate(FeeStructureBase):
    student_id: UUID


class FeeStructureResponse(FeeStructureBase):
    id: UUID
    student_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_method: PaymentMethod
    reference_number: str = Field(..., min_length=1, max_length=100)
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    semester: str = Field(..., min_length=1, max_length=20)
    remarks: Optional[str] = Field(None, max_length=200)


class PaymentCreate(PaymentBase):
    student_id: UUID
    payment_date: Optional[datetime] = None


class PaymentResponse(PaymentBase):
    id: UUID
    student_id: UUID
    payment_date: datetime
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class FeeStatement(BaseModel):
    total_billed: Decimal
    total_paid: Decimal
    balance: Decimal
    fees: list[FeeStructureResponse]
    payments: list[PaymentResponse]
    
    class Config:
        from_attributes = True
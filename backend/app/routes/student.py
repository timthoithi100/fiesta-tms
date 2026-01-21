from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from decimal import Decimal

from app.database import get_db
from app.models import (
    Student, Unit, UnitRegistration, Result, 
    FeeStructure, Payment, StudentRequest, RequestStatus
)
from app.schemas import (
    StudentResponse, StudentUpdate, StudentDashboard,
    UnitResponse, UnitRegistrationCreate, UnitRegistrationResponse,
    ResultWithUnit, FeeStatement,
    StudentRequestCreate, StudentRequestResponse
)
from app.dependencies import get_current_student

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/dashboard", response_model=StudentDashboard)
async def get_dashboard(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Get student dashboard data."""
    # Get registered units count (current semester)
    registered_result = await db.execute(
        select(func.count(UnitRegistration.id))
        .where(UnitRegistration.student_id == student.id)
        .where(UnitRegistration.status == "registered")
    )
    registered_count = registered_result.scalar()
    
    # Get attempted units count (all time)
    attempted_result = await db.execute(
        select(func.count(UnitRegistration.id))
        .where(UnitRegistration.student_id == student.id)
    )
    attempted_count = attempted_result.scalar()
    
    # Get fee information
    fees_result = await db.execute(
        select(func.sum(FeeStructure.amount))
        .where(FeeStructure.student_id == student.id)
    )
    total_billed = fees_result.scalar() or Decimal(0)
    
    payments_result = await db.execute(
        select(func.sum(Payment.amount))
        .where(Payment.student_id == student.id)
    )
    total_paid = payments_result.scalar() or Decimal(0)
    
    return {
        "student_info": student,
        "registered_units_count": registered_count,
        "attempted_units_count": attempted_count,
        "total_billed": float(total_billed),
        "total_paid": float(total_paid),
        "fee_balance": float(total_billed - total_paid)
    }


@router.get("/profile", response_model=StudentResponse)
async def get_profile(student: Student = Depends(get_current_student)):
    """Get student personal information."""
    return student


@router.put("/profile", response_model=StudentResponse)
async def update_profile(
    update_data: StudentUpdate,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Update student personal information."""
    update_dict = update_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(student, field, value)
    
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/units/available", response_model=List[UnitResponse])
async def get_available_units(db: AsyncSession = Depends(get_db)):
    """Get all available units for registration."""
    result = await db.execute(
        select(Unit).where(Unit.is_active == "active")
    )
    units = result.scalars().all()
    return units


@router.get("/units/registered", response_model=List[UnitRegistrationResponse])
async def get_registered_units(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Get student's registered units."""
    result = await db.execute(
        select(UnitRegistration)
        .where(UnitRegistration.student_id == student.id)
        .order_by(UnitRegistration.registration_date.desc())
    )
    registrations = result.scalars().all()
    return registrations


@router.post("/units/register", response_model=UnitRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_unit(
    registration_data: UnitRegistrationCreate,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Register for a unit."""
    # Check if unit exists
    unit_result = await db.execute(
        select(Unit).where(Unit.id == registration_data.unit_id)
    )
    unit = unit_result.scalar_one_or_none()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if already registered
    existing = await db.execute(
        select(UnitRegistration)
        .where(UnitRegistration.student_id == student.id)
        .where(UnitRegistration.unit_id == registration_data.unit_id)
        .where(UnitRegistration.academic_year == registration_data.academic_year)
        .where(UnitRegistration.semester == registration_data.semester)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this unit"
        )
    
    # Create registration
    registration = UnitRegistration(
        student_id=student.id,
        unit_id=registration_data.unit_id,
        semester=registration_data.semester,
        academic_year=registration_data.academic_year
    )
    db.add(registration)
    await db.commit()
    await db.refresh(registration)
    return registration


@router.get("/results", response_model=List[ResultWithUnit])
async def get_results(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Get student's results."""
    result = await db.execute(
        select(Result)
        .join(UnitRegistration)
        .where(UnitRegistration.student_id == student.id)
        .where(Result.is_published == "published")
    )
    results = result.scalars().all()
    return results


@router.get("/fees", response_model=FeeStatement)
async def get_fee_statement(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Get student's fee statement."""
    # Get all fees
    fees_result = await db.execute(
        select(FeeStructure)
        .where(FeeStructure.student_id == student.id)
        .order_by(FeeStructure.created_at.desc())
    )
    fees = fees_result.scalars().all()
    
    # Get all payments
    payments_result = await db.execute(
        select(Payment)
        .where(Payment.student_id == student.id)
        .order_by(Payment.payment_date.desc())
    )
    payments = payments_result.scalars().all()
    
    # Calculate totals
    total_billed = sum(fee.amount for fee in fees)
    total_paid = sum(payment.amount for payment in payments)
    
    return {
        "total_billed": total_billed,
        "total_paid": total_paid,
        "balance": total_billed - total_paid,
        "fees": fees,
        "payments": payments
    }


@router.post("/requests", response_model=StudentRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: StudentRequestCreate,
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Create graduation or clearance request."""
    # Check for pending request of same type
    existing = await db.execute(
        select(StudentRequest)
        .where(StudentRequest.student_id == student.id)
        .where(StudentRequest.request_type == request_data.request_type)
        .where(StudentRequest.status == RequestStatus.PENDING)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a pending {request_data.request_type} request"
        )
    
    request = StudentRequest(
        student_id=student.id,
        request_type=request_data.request_type,
        student_remarks=request_data.student_remarks
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


@router.get("/requests", response_model=List[StudentRequestResponse])
async def get_requests(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Get student's requests."""
    result = await db.execute(
        select(StudentRequest)
        .where(StudentRequest.student_id == student.id)
        .order_by(StudentRequest.request_date.desc())
    )
    requests = result.scalars().all()
    return requests
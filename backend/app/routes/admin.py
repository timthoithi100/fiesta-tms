from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import (
    User, Student, Unit, UnitRegistration, Result,
    FeeStructure, Payment, StudentRequest, RequestStatus
)
from app.schemas import (
    StudentResponse, UnitCreate, UnitUpdate, UnitResponse,
    ResultCreate, ResultUpdate, ResultResponse,
    FeeStructureCreate, FeeStructureResponse,
    PaymentCreate, PaymentResponse,
    StudentRequestResponse, StudentRequestUpdate
)
from app.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ Student Management ============
@router.get("/students", response_model=List[StudentResponse])
async def get_all_students(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all students with optional search."""
    query = select(Student)
    
    if search:
        query = query.where(
            or_(
                Student.student_id.ilike(f"%{search}%"),
                Student.first_name.ilike(f"%{search}%"),
                Student.last_name.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%")
            )
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()
    return students


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get student by ID."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student


# ============ Unit Management ============
@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new unit."""
    # Check if unit code exists
    existing = await db.execute(
        select(Unit).where(Unit.unit_code == unit_data.unit_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit code already exists"
        )
    
    unit = Unit(**unit_data.dict())
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return unit


@router.get("/units", response_model=List[UnitResponse])
async def get_all_units(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all units."""
    result = await db.execute(select(Unit))
    units = result.scalars().all()
    return units


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: UUID,
    update_data: UnitUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a unit."""
    result = await db.execute(select(Unit).where(Unit.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(unit, field, value)
    
    await db.commit()
    await db.refresh(unit)
    return unit


# ============ Results Management ============
@router.post("/results", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
async def enter_result(
    result_data: ResultCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Enter or update student result."""
    # Check if registration exists
    reg_result = await db.execute(
        select(UnitRegistration).where(UnitRegistration.id == result_data.registration_id)
    )
    registration = reg_result.scalar_one_or_none()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    # Check if result already exists
    existing = await db.execute(
        select(Result).where(Result.registration_id == result_data.registration_id)
    )
    existing_result = existing.scalar_one_or_none()
    
    if existing_result:
        # Update existing result
        for field, value in result_data.dict(exclude_unset=True).items():
            if field != "registration_id":
                setattr(existing_result, field, value)
        existing_result.entered_by = admin.id
        existing_result.entered_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_result)
        return existing_result
    else:
        # Create new result
        result = Result(
            **result_data.dict(),
            entered_by=admin.id,
            entered_at=datetime.utcnow()
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result


@router.put("/results/{result_id}", response_model=ResultResponse)
async def update_result(
    result_id: UUID,
    update_data: ResultUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update result status (publish/unpublish)."""
    result = await db.execute(select(Result).where(Result.id == result_id))
    result_obj = result.scalar_one_or_none()
    if not result_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(result_obj, field, value)
    
    await db.commit()
    await db.refresh(result_obj)
    return result_obj


# ============ Fee Management ============
@router.post("/fees", response_model=FeeStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_fee(
    fee_data: FeeStructureCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create fee structure for a student."""
    fee = FeeStructure(**fee_data.dict(), created_by=admin.id)
    db.add(fee)
    await db.commit()
    await db.refresh(fee)
    return fee


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def record_payment(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Record a payment."""
    # Check if reference number exists
    existing = await db.execute(
        select(Payment).where(Payment.reference_number == payment_data.reference_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment reference number already exists"
        )
    
    payment = Payment(**payment_data.dict(), recorded_by=admin.id)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


# ============ Clearance Processing ============
@router.get("/requests", response_model=List[StudentRequestResponse])
async def get_all_requests(
    request_type: Optional[str] = Query(None),
    status_filter: Optional[RequestStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all student requests."""
    query = select(StudentRequest)
    
    if request_type:
        query = query.where(StudentRequest.request_type == request_type)
    if status_filter:
        query = query.where(StudentRequest.status == status_filter)
    
    query = query.order_by(StudentRequest.request_date.desc())
    result = await db.execute(query)
    requests = result.scalars().all()
    return requests


@router.put("/requests/{request_id}", response_model=StudentRequestResponse)
async def process_request(
    request_id: UUID,
    update_data: StudentRequestUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Process student request (approve/reject)."""
    result = await db.execute(
        select(StudentRequest).where(StudentRequest.id == request_id)
    )
    request_obj = result.scalar_one_or_none()
    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    request_obj.status = update_data.status
    request_obj.admin_remarks = update_data.admin_remarks
    request_obj.processed_by = admin.id
    request_obj.processed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(request_obj)
    return request_obj


# ============ Reports & Analytics ============
@router.get("/reports/summary")
async def get_summary_report(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get system summary statistics."""
    # Total students
    total_students = await db.execute(select(func.count(Student.id)))
    
    # Active students
    active_students = await db.execute(
        select(func.count(Student.id)).where(Student.is_graduated == "active")
    )
    
    # Total units
    total_units = await db.execute(select(func.count(Unit.id)))
    
    # Pending requests
    pending_requests = await db.execute(
        select(func.count(StudentRequest.id))
        .where(StudentRequest.status == RequestStatus.PENDING)
    )
    
    # Total fees collected
    total_collected = await db.execute(select(func.sum(Payment.amount)))
    
    return {
        "total_students": total_students.scalar(),
        "active_students": active_students.scalar(),
        "total_units": total_units.scalar(),
        "pending_requests": pending_requests.scalar(),
        "total_fees_collected": float(total_collected.scalar() or 0)
    }
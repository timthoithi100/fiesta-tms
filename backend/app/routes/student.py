from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models import User, Student, Unit, UnitRegistration, Result, Payment, FeeStructure, StudentRequest
from app.dependencies import get_current_user

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(Student).where(Student.user_id == user.id))
    student = res.scalar_one()
    
    reg_count = await db.execute(select(func.count(UnitRegistration.id)).where(UnitRegistration.student_id == student.id))
    billed = await db.execute(select(func.sum(FeeStructure.amount)).where(FeeStructure.student_id == student.id))
    paid = await db.execute(select(func.sum(Payment.amount)).where(Payment.student_id == student.id))
    
    total_billed = float(billed.scalar() or 0)
    total_paid = float(paid.scalar() or 0)
    
    return {
        "registered_units_count": reg_count.scalar(),
        "fee_balance": total_billed - total_paid,
        "student_info": student
    }

@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(Student).where(Student.user_id == user.id))
    return res.scalar_one()

@router.put("/profile")
async def update_profile(data: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(Student).where(Student.user_id == user.id))
    student = res.scalar_one()
    for key, value in data.items():
        setattr(student, key, value)
    await db.commit()
    return {"message": "Updated"}

@router.get("/units/available")
async def available_units(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Unit).where(Unit.is_active == True))
    return res.scalars().all()

@router.post("/units/register")
async def register_unit(data: dict, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(Student).where(Student.user_id == user.id))
    student = res.scalar_one()
    new_reg = UnitRegistration(student_id=student.id, unit_id=data['unit_id'], academic_year="2025/2026", semester="1")
    db.add(new_reg)
    await db.commit()
    return {"message": "Registered"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import secrets

from app.database import get_db
from app.models import User, Student, UserRole
from app.schemas import (
    UserLogin, Token, StudentCreate, UserResponse, PasswordChange
)
from app.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(student_data: StudentCreate, db: AsyncSession = Depends(get_db)):
    """Register a new student."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == student_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=student_data.email,
        hashed_password=get_password_hash(student_data.password),
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    await db.flush()
    
    # Generate student ID
    student_id = f"FT{datetime.now().year}{secrets.token_hex(3).upper()}"
    
    # Create student profile
    student = Student(
        user_id=user.id,
        student_id=student_id,
        first_name=student_data.first_name,
        middle_name=student_data.middle_name,
        last_name=student_data.last_name,
        gender=student_data.gender,
        date_of_birth=student_data.date_of_birth,
        phone_number=student_data.phone_number,
        city=student_data.city,
        address=student_data.address,
        program=student_data.program,
        enrollment_date=datetime.now().date()
    )
    db.add(student)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    token_data = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}
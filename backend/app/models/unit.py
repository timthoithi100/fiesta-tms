from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class Semester(str, enum.Enum):
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"


class RegistrationStatus(str, enum.Enum):
    REGISTERED = "registered"
    DROPPED = "dropped"
    COMPLETED = "completed"


class Unit(Base):
    __tablename__ = "units"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    unit_code = Column(String(20), unique=True, nullable=False, index=True)
    unit_name = Column(String(200), nullable=False)
    credits = Column(Integer, nullable=False, default=3)
    description = Column(String(500), nullable=True)
    is_active = Column(String(20), default="active")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Unit {self.unit_code} - {self.unit_name}>"


class UnitRegistration(Base):
    __tablename__ = "unit_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    
    semester = Column(SQLEnum(Semester), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    status = Column(SQLEnum(RegistrationStatus), default=RegistrationStatus.REGISTERED, nullable=False)
    
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student = relationship("Student", backref="unit_registrations", lazy="joined")
    unit = relationship("Unit", backref="registrations", lazy="joined")
    
    def __repr__(self):
        return f"<UnitRegistration {self.student_id} - {self.unit_id}>"


class Result(Base):
    __tablename__ = "results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    registration_id = Column(UUID(as_uuid=True), ForeignKey("unit_registrations.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    marks = Column(Numeric(5, 2), nullable=True)  # Out of 100
    grade = Column(String(2), nullable=True)  # A, B+, B, C+, C, D+, D, E, F
    remarks = Column(String(200), nullable=True)
    
    is_published = Column(String(20), default="provisional")  # provisional, published
    
    entered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    entered_at = Column(DateTime, nullable=True)
    
    # Relationships
    registration = relationship("UnitRegistration", backref="result", lazy="joined")
    
    def __repr__(self):
        return f"<Result {self.registration_id} - Grade: {self.grade}>"
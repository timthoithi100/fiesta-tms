from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class FeeType(str, enum.Enum):
    TUITION = "tuition"
    REGISTRATION = "registration"
    LIBRARY = "library"
    EXAM = "exam"
    OTHER = "other"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    MPESA = "mpesa"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"


class FeeStructure(Base):
    __tablename__ = "fee_structures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    
    fee_type = Column(SQLEnum(FeeType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    semester = Column(String(20), nullable=False)
    
    description = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    student = relationship("Student", backref="fee_structures", lazy="joined")
    
    def __repr__(self):
        return f"<FeeStructure {self.fee_type} - {self.amount}>"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference_number = Column(String(100), unique=True, nullable=False, index=True)
    
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    academic_year = Column(String(9), nullable=False)
    semester = Column(String(20), nullable=False)
    
    remarks = Column(String(200), nullable=True)
    
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student = relationship("Student", backref="payments", lazy="joined")
    
    def __repr__(self):
        return f"<Payment {self.reference_number} - {self.amount}>"
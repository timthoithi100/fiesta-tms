from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Student(Base):
    __tablename__ = "students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    
    # Contact Information
    phone_number = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    
    # Academic Information
    enrollment_date = Column(Date, default=datetime.utcnow, nullable=False)
    program = Column(String(100), nullable=False)  # e.g., "Professional Chef Training", "Catering Management"
    
    # Status
    is_graduated = Column(String(20), default="active")  # active, graduated, suspended
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="student_profile", lazy="joined")
    
    def __repr__(self):
        return f"<Student {self.student_id} - {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
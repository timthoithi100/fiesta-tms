from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class RequestType(str, enum.Enum):
    GRADUATION = "graduation"
    CLEARANCE = "clearance"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"


class StudentRequest(Base):
    __tablename__ = "student_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    
    request_type = Column(SQLEnum(RequestType), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    
    request_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    student_remarks = Column(Text, nullable=True)
    
    # Admin response
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    admin_remarks = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", backref="requests", lazy="joined")
    processor = relationship("User", foreign_keys=[processed_by], lazy="joined")
    
    def __repr__(self):
        return f"<StudentRequest {self.request_type} - {self.status}>"
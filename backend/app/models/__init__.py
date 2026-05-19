from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMPANY_SECRETARY = "company_secretary"
    CFO = "cfo"
    DIRECTOR = "director"
    AUDITOR = "auditor"
    TAX_ADVISOR = "tax_advisor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.COMPANY_SECRETARY)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    companies = relationship("CompanyUser", back_populates="user")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(50), unique=True, index=True)  # RJSC number
    tin = Column(String(50))  # Tax Identification Number
    bin = Column(String(50))  # Business Identification Number (VAT)
    trade_license_number = Column(String(100))
    trade_license_expiry = Column(DateTime(timezone=True))
    company_type = Column(String(50), default="private_limited")  # private_limited, public_limited, branch, liaison, opc
    industry = Column(String(100))
    fiscal_year_end = Column(String(5), default="06-30")  # MM-DD format
    incorporation_date = Column(DateTime(timezone=True))
    registered_address = Column(String(500))
    authorized_capital = Column(Integer, default=0)
    paid_up_capital = Column(Integer, default=0)
    is_listed = Column(Boolean, default=False)  # BSEC compliance required
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("CompanyUser", back_populates="company")
    directors = relationship("Director", back_populates="company")
    shareholders = relationship("Shareholder", back_populates="company")
    compliance_events = relationship("ComplianceEvent", back_populates="company")
    filings = relationship("Filing", back_populates="company")
    documents = relationship("Document", back_populates="company")

class CompanyUser(Base):
    __tablename__ = "company_users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(UserRole), default=UserRole.COMPANY_SECRETARY)
    is_primary = Column(Boolean, default=False)

    company = relationship("Company", back_populates="users")
    user = relationship("User", back_populates="companies")

class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    full_name = Column(String(255), nullable=False)
    nid = Column(String(50))  # National ID
    address = Column(String(500))
    appointment_date = Column(DateTime(timezone=True))
    resignation_date = Column(DateTime(timezone=True))
    is_independent = Column(Boolean, default=False)  # BSEC requirement
    designation = Column(String(100), default="director")  # chairman, md, director

    company = relationship("Company", back_populates="directors")

class Shareholder(Base):
    __tablename__ = "shareholders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    full_name = Column(String(255), nullable=False)
    nid = Column(String(50))
    shares = Column(Integer, default=0)
    share_class = Column(String(50), default="ordinary")
    acquisition_date = Column(DateTime(timezone=True))

    company = relationship("Company", back_populates="shareholders")

class ComplianceEventStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    WAIVED = "waived"

class ComplianceEventPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ComplianceEvent(Base):
    __tablename__ = "compliance_events"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    event_type = Column(String(100), nullable=False)  # AGM, Schedule_X, Tax_Return, VAT_Return, etc.
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    due_date = Column(DateTime(timezone=True), nullable=False)
    fiscal_year = Column(String(10))  # e.g., "2025-26"
    status = Column(Enum(ComplianceEventStatus), default=ComplianceEventStatus.NOT_STARTED)
    priority = Column(Enum(ComplianceEventPriority), default=ComplianceEventPriority.MEDIUM)
    responsible_user_id = Column(Integer, ForeignKey("users.id"))
    penalty_amount = Column(Integer, default=0)  # Calculated if overdue
    reminder_sent_60 = Column(Boolean, default=False)
    reminder_sent_30 = Column(Boolean, default=False)
    reminder_sent_14 = Column(Boolean, default=False)
    reminder_sent_7 = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    notes = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="compliance_events")

class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    compliance_event_id = Column(Integer, ForeignKey("compliance_events.id"))
    form_type = Column(String(50), nullable=False)  # Form_XII, Form_III, Schedule_X, etc.
    filing_date = Column(DateTime(timezone=True))
    acknowledgment_number = Column(String(100))
    status = Column(String(50), default="draft")  # draft, filed, approved, rejected
    documents = relationship("Document", back_populates="filing")

    company = relationship("Company", back_populates="filings")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    filing_id = Column(Integer, ForeignKey("filings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, xlsx, etc.
    file_size = Column(Integer)
    category = Column(String(100))  # board_resolution, financial_statement, tax_return, etc.
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="documents")
    filing = relationship("Filing", back_populates="documents")

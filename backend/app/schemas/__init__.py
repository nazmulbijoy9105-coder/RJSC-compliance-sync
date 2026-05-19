from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    COMPANY_SECRETARY = "company_secretary"
    CFO = "cfo"
    DIRECTOR = "director"
    AUDITOR = "auditor"
    TAX_ADVISOR = "tax_advisor"

class CompanyType(str, Enum):
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    BRANCH = "branch"
    LIAISON = "liaison"
    OPC = "opc"  # One Person Company

class EventStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    WAIVED = "waived"

class EventPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# User Schemas
class UserBase(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.COMPANY_SECRETARY
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    registration_number: str = Field(..., min_length=5, max_length=50)
    company_type: CompanyType = CompanyType.PRIVATE_LIMITED
    industry: Optional[str] = None
    fiscal_year_end: str = Field(default="06-30", pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
    incorporation_date: Optional[date] = None
    registered_address: Optional[str] = None
    authorized_capital: int = 0
    paid_up_capital: int = 0
    is_listed: bool = False
    tin: Optional[str] = None
    bin: Optional[str] = None
    trade_license_number: Optional[str] = None
    trade_license_expiry: Optional[date] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    compliance_score: Optional[int] = None

class CompanyDetail(CompanyResponse):
    directors: List['DirectorResponse'] = []
    shareholders: List['ShareholderResponse'] = []
    compliance_events: List['ComplianceEventResponse'] = []

# Director Schemas
class DirectorBase(BaseModel):
    full_name: str
    nid: Optional[str] = None
    address: Optional[str] = None
    appointment_date: Optional[date] = None
    resignation_date: Optional[date] = None
    is_independent: bool = False
    designation: str = "director"

class DirectorCreate(DirectorBase):
    pass

class DirectorResponse(DirectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int

# Shareholder Schemas
class ShareholderBase(BaseModel):
    full_name: str
    nid: Optional[str] = None
    shares: int = 0
    share_class: str = "ordinary"
    acquisition_date: Optional[date] = None

class ShareholderCreate(ShareholderBase):
    pass

class ShareholderResponse(ShareholderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int

# Compliance Event Schemas
class ComplianceEventBase(BaseModel):
    event_type: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    fiscal_year: Optional[str] = None
    status: EventStatus = EventStatus.NOT_STARTED
    priority: EventPriority = EventPriority.MEDIUM
    responsible_user_id: Optional[int] = None
    notes: Optional[str] = None

class ComplianceEventCreate(ComplianceEventBase):
    company_id: int

class ComplianceEventResponse(ComplianceEventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    penalty_amount: int = 0
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    days_remaining: Optional[int] = None

class ComplianceEventUpdate(BaseModel):
    status: Optional[EventStatus] = None
    priority: Optional[EventPriority] = None
    responsible_user_id: Optional[int] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_companies: int
    total_events: int
    upcoming_events: int
    overdue_events: int
    completed_this_month: int
    average_compliance_score: float

class ComplianceCalendarEntry(BaseModel):
    date: date
    events: List[ComplianceEventResponse]

class RiskHeatmap(BaseModel):
    green: int  # On track
    yellow: int  # Approaching
    red: int     # Overdue/Urgent
    total: int

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    category: Optional[str] = None

class DocumentCreate(DocumentBase):
    company_id: int
    filing_id: Optional[int] = None

class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None

# Filing Schemas
class FilingBase(BaseModel):
    form_type: str
    status: str = "draft"
    acknowledgment_number: Optional[str] = None

class FilingCreate(FilingBase):
    company_id: int
    compliance_event_id: Optional[int] = None

class FilingResponse(FilingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filing_date: Optional[datetime] = None
    company_id: int
    compliance_event_id: Optional[int] = None

# Compliance Score
class ComplianceScoreDetail(BaseModel):
    company_id: int
    company_name: str
    score: int  # 0-100
    total_events: int
    on_time: int
    late: int
    overdue: int
    penalties_incurred: int
    benchmark_vs_industry: Optional[float] = None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Company, Director, Shareholder, ComplianceEvent, CompanyUser, User
from app.schemas import CompanyCreate, CompanyResponse, CompanyDetail, DirectorCreate, DirectorResponse, ShareholderCreate, ShareholderResponse
from app.services.compliance_engine import BangladeshComplianceRules

router = APIRouter()

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Company).where(Company.registration_number == company_data.registration_number))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Registration number already exists")

    db_company = Company(**company_data.model_dump())
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)

    company_user = CompanyUser(
        company_id=db_company.id,
        user_id=current_user.id,
        role=current_user.role,
        is_primary=True
    )
    db.add(company_user)
    await db.commit()

    events = BangladeshComplianceRules.generate_full_compliance_calendar(db_company)
    for event_data in events:
        event = ComplianceEvent(company_id=db_company.id, **event_data)
        db.add(event)
    await db.commit()

    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(Company.is_active == True)
    )
    companies = result.scalars().all()
    return companies

@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    access = await db.execute(
        select(CompanyUser)
        .where(and_(CompanyUser.company_id == company_id, CompanyUser.user_id == current_user.id))
    )
    if not access.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company

@router.post("/{company_id}/directors", response_model=DirectorResponse)
async def add_director(
    company_id: int,
    director_data: DirectorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    director = Director(company_id=company_id, **director_data.model_dump())
    db.add(director)
    await db.commit()
    await db.refresh(director)
    return director

@router.post("/{company_id}/shareholders", response_model=ShareholderResponse)
async def add_shareholder(
    company_id: int,
    shareholder_data: ShareholderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    shareholder = Shareholder(company_id=company_id, **shareholder_data.model_dump())
    db.add(shareholder)
    await db.commit()
    await db.refresh(shareholder)
    return shareholder

@router.post("/{company_id}/regenerate-calendar")
async def regenerate_calendar(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    access = await db.execute(
        select(CompanyUser)
        .where(and_(CompanyUser.company_id == company_id, CompanyUser.user_id == current_user.id))
    )
    if not access.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from sqlalchemy import delete
    await db.execute(
        delete(ComplianceEvent)
        .where(ComplianceEvent.company_id == company_id)
        .where(ComplianceEvent.due_date >= datetime.utcnow())
    )

    events = BangladeshComplianceRules.generate_full_compliance_calendar(company)
    for event_data in events:
        event = ComplianceEvent(company_id=company_id, **event_data)
        db.add(event)
    await db.commit()

    return {"message": "Compliance calendar regenerated", "events_created": len(events)}

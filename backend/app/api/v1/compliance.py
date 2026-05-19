from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import ComplianceEvent, Company, CompanyUser, User
from app.schemas import ComplianceEventResponse, ComplianceEventUpdate, RiskHeatmap
from app.services.compliance_engine import BangladeshComplianceRules

router = APIRouter()

@router.get("/events", response_model=List[ComplianceEventResponse])
async def get_events(
    company_id: int = None,
    status: str = None,
    priority: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(ComplianceEvent).join(Company).join(CompanyUser).where(CompanyUser.user_id == current_user.id)

    if company_id:
        query = query.where(ComplianceEvent.company_id == company_id)
    if status:
        query = query.where(ComplianceEvent.status == status)
    if priority:
        query = query.where(ComplianceEvent.priority == priority)

    query = query.order_by(ComplianceEvent.due_date)
    result = await db.execute(query)
    events = result.scalars().all()

    response_events = []
    for event in events:
        event_dict = {
            "id": event.id,
            "company_id": event.company_id,
            "event_type": event.event_type,
            "title": event.title,
            "description": event.description,
            "due_date": event.due_date,
            "fiscal_year": event.fiscal_year,
            "status": event.status,
            "priority": event.priority,
            "responsible_user_id": event.responsible_user_id,
            "penalty_amount": event.penalty_amount,
            "completed_at": event.completed_at,
            "created_at": event.created_at,
            "days_remaining": (event.due_date - datetime.utcnow()).days if event.due_date else None
        }
        response_events.append(event_dict)

    return response_events

@router.get("/events/{event_id}")
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ComplianceEvent)
        .join(Company)
        .join(CompanyUser)
        .where(and_(ComplianceEvent.id == event_id, CompanyUser.user_id == current_user.id))
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.patch("/events/{event_id}", response_model=ComplianceEventResponse)
async def update_event(
    event_id: int,
    update_data: ComplianceEventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ComplianceEvent)
        .join(Company)
        .join(CompanyUser)
        .where(and_(ComplianceEvent.id == event_id, CompanyUser.user_id == current_user.id))
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    if event.status == "overdue" or (event.status == "completed" and event.due_date < datetime.utcnow()):
        days_overdue = (datetime.utcnow() - event.due_date).days
        result_company = await db.execute(select(Company).where(Company.id == event.company_id))
        company = result_company.scalar_one_or_none()
        event.penalty_amount = BangladeshComplianceRules.calculate_penalty(
            event.event_type, days_overdue, 
            "public" if company and company.is_listed else "private"
        )

    await db.commit()
    await db.refresh(event)
    return event

@router.get("/risk-heatmap")
async def get_risk_heatmap(
    company_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(ComplianceEvent).join(Company).join(CompanyUser).where(CompanyUser.user_id == current_user.id)
    if company_id:
        query = query.where(ComplianceEvent.company_id == company_id)

    result = await db.execute(query)
    events = result.scalars().all()

    green = yellow = red = 0
    for event in events:
        days = (event.due_date - datetime.utcnow()).days if event.due_date else 0
        if event.status == "completed":
            green += 1
        elif days > 30:
            green += 1
        elif days > 7:
            yellow += 1
        else:
            red += 1

    return RiskHeatmap(green=green, yellow=yellow, red=red, total=green+yellow+red)

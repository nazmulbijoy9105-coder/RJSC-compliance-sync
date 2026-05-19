from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import ComplianceEvent, Company, CompanyUser, User
from app.schemas import DashboardStats, ComplianceScoreDetail

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(func.count(Company.id))
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(Company.is_active == True)
    )
    total_companies = result.scalar() or 0

    result = await db.execute(
        select(func.count(ComplianceEvent.id))
        .join(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
    )
    total_events = result.scalar() or 0

    upcoming = datetime.utcnow() + timedelta(days=30)
    result = await db.execute(
        select(func.count(ComplianceEvent.id))
        .join(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(ComplianceEvent.due_date <= upcoming)
        .where(ComplianceEvent.due_date >= datetime.utcnow())
        .where(ComplianceEvent.status != "completed")
    )
    upcoming_events = result.scalar() or 0

    result = await db.execute(
        select(func.count(ComplianceEvent.id))
        .join(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(ComplianceEvent.due_date < datetime.utcnow())
        .where(ComplianceEvent.status != "completed")
    )
    overdue_events = result.scalar() or 0

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    result = await db.execute(
        select(func.count(ComplianceEvent.id))
        .join(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(ComplianceEvent.status == "completed")
        .where(ComplianceEvent.completed_at >= month_start)
    )
    completed_this_month = result.scalar() or 0

    result = await db.execute(
        select(Company)
        .join(CompanyUser)
        .where(CompanyUser.user_id == current_user.id)
        .where(Company.is_active == True)
    )
    companies = result.scalars().all()

    total_score = 0
    for company in companies:
        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
            .where(ComplianceEvent.status == "completed")
        )
        completed = result.scalar() or 0
        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
        )
        total = result.scalar() or 1
        total_score += (completed / total) * 100

    avg_score = total_score / len(companies) if companies else 0

    return DashboardStats(
        total_companies=total_companies,
        total_events=total_events,
        upcoming_events=upcoming_events,
        overdue_events=overdue_events,
        completed_this_month=completed_this_month,
        average_compliance_score=round(avg_score, 1)
    )

@router.get("/compliance-scores")
async def get_compliance_scores(
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

    scores = []
    for company in companies:
        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
            .where(ComplianceEvent.status == "completed")
        )
        on_time = result.scalar() or 0

        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
            .where(ComplianceEvent.status == "overdue")
        )
        overdue = result.scalar() or 0

        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
            .where(ComplianceEvent.due_date < datetime.utcnow())
            .where(ComplianceEvent.status != "completed")
        )
        late = result.scalar() or 0

        result = await db.execute(
            select(func.count(ComplianceEvent.id))
            .where(ComplianceEvent.company_id == company.id)
        )
        total = result.scalar() or 1

        score = int(((on_time + (total - late - overdue) * 0.5) / total) * 100)

        scores.append(ComplianceScoreDetail(
            company_id=company.id,
            company_name=company.name,
            score=score,
            total_events=total,
            on_time=on_time,
            late=late,
            overdue=overdue,
            penalties_incurred=0
        ))

    return sorted(scores, key=lambda x: x.score, reverse=True)

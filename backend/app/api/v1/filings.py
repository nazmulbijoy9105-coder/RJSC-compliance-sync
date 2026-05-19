from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Filing, Company, CompanyUser, User
from app.schemas import FilingCreate, FilingResponse

router = APIRouter()

@router.post("/", response_model=FilingResponse)
async def create_filing(
    filing_data: FilingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    access = await db.execute(
        select(CompanyUser)
        .where(and_(CompanyUser.company_id == filing_data.company_id, CompanyUser.user_id == current_user.id))
    )
    if not access.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    filing = Filing(**filing_data.model_dump())
    db.add(filing)
    await db.commit()
    await db.refresh(filing)
    return filing

@router.get("/", response_model=List[FilingResponse])
async def list_filings(
    company_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Filing).join(Company).join(CompanyUser).where(CompanyUser.user_id == current_user.id)
    if company_id:
        query = query.where(Filing.company_id == company_id)

    result = await db.execute(query)
    return result.scalars().all()

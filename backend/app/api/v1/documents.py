from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
import os
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models import Document, Company, CompanyUser, User
from app.schemas import DocumentCreate, DocumentResponse
from app.services.storage import upload_file_to_storage

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    company_id: int = Form(...),
    title: str = Form(...),
    category: str = Form(...),
    filing_id: int = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    access = await db.execute(
        select(CompanyUser)
        .where(and_(CompanyUser.company_id == company_id, CompanyUser.user_id == current_user.id))
    )
    if not access.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Create a safe, unique filename
    file_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{company_id}_{timestamp}_{file.filename}"

    try:
        # Upload to Cloudflare R2 instead of local disk
        file_url = upload_file_to_storage(
            file_bytes=file_bytes,
            file_name=safe_filename,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cloud storage upload failed")

    # Save the R2 URL to your database
    db_doc = Document(
        company_id=company_id,
        filing_id=filing_id,
        title=title,
        file_path=file_url,
        file_type=file_ext.replace(".", ""),
        file_size=len(file_bytes),
        category=category,
        uploaded_by=current_user.id
    )
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)

    return db_doc

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    company_id: int = None,
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Document).join(Company).join(CompanyUser).where(CompanyUser.user_id == current_user.id)
    if company_id:
        query = query.where(Document.company_id == company_id)
    if category:
        query = query.where(Document.category == category)

    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
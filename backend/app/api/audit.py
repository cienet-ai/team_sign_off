from datetime import datetime

from fastapi import APIRouter, Depends, Query

from backend.app.database import get_db
from backend.app.middleware import get_current_user
from backend.app.models import User
from backend.app.schemas import AuditLogOut, PaginatedResponse
from backend.app.services import list_audit_logs
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=PaginatedResponse)
async def get_audit_logs(
    status: str | None = Query(None),
    action: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    applicant_id: int | None = Query(None),
    approver_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_audit_logs(
        db,
        status=status,
        action=action,
        start_date=start_date.isoformat() if start_date else None,
        end_date=end_date.isoformat() if end_date else None,
        applicant_id=applicant_id,
        approver_id=approver_id,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        items=[AuditLogOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )
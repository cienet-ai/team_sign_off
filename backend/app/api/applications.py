from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.middleware import get_current_user
from backend.app.models import ApplicationStatus, User
from backend.app.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    PaginatedResponse,
    RejectRequest,
)
from backend.app.services import (
    approve_application,
    create_application,
    get_application,
    list_my_applications,
    list_pending_approvals,
    reject_application,
    resubmit_application,
    void_application,
)
from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create(
    body: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_application(
        db, current_user, body.title, body.reason, body.content, body.approver_id
    )


@router.get("", response_model=PaginatedResponse)
async def list_my(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_my_applications(
        db, current_user.id, status_filter, limit, offset
    )
    return PaginatedResponse(
        items=[ApplicationOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/pending", response_model=PaginatedResponse)
async def list_pending(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_pending_approvals(db, current_user.id, limit, offset)
    return PaginatedResponse(
        items=[ApplicationOut.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_one(
    application_id: int,
    db: AsyncSession = Depends(get_db),
):
    app = await get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.put("/{application_id}", response_model=ApplicationOut)
async def update(
    application_id: int,
    body: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your application")
    if app.status != ApplicationStatus.rejected:
        raise HTTPException(status_code=400, detail="Can only update rejected applications")
    return await resubmit_application(
        db, app, current_user, body.title, body.reason, body.content, body.approver_id
    )


@router.post("/{application_id}/approve", response_model=ApplicationOut)
async def approve(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the assigned approver")
    if app.status != ApplicationStatus.pending:
        raise HTTPException(status_code=400, detail="Can only approve pending applications")
    return await approve_application(db, app, current_user)


@router.post("/{application_id}/reject", response_model=ApplicationOut)
async def reject(
    application_id: int,
    body: RejectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the assigned approver")
    if app.status != ApplicationStatus.pending:
        raise HTTPException(status_code=400, detail="Can only reject pending applications")
    return await reject_application(db, app, current_user, body.reason)


@router.post("/{application_id}/void", response_model=ApplicationOut)
async def void(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your application")
    if app.status not in (ApplicationStatus.pending, ApplicationStatus.rejected):
        raise HTTPException(status_code=400, detail="Can only void pending or rejected applications")
    return await void_application(db, app, current_user)
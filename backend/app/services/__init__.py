from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models import (
    Application,
    ApplicationStatus,
    AuditAction,
    AuditLog,
    User,
)


async def create_application(
    db: AsyncSession,
    applicant: User,
    title: str,
    reason: str,
    content: str,
    approver_id: int,
) -> Application:
    application = Application(
        title=title,
        reason=reason,
        content=content,
        status=ApplicationStatus.pending,
        applicant_id=applicant.id,
        approver_id=approver_id,
    )
    db.add(application)
    await db.flush()

    audit = AuditLog(
        application_id=application.id,
        action=AuditAction.created,
        performed_by_id=applicant.id,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(application)
    return application


async def get_application(db: AsyncSession, application_id: int) -> Application | None:
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.applicant), selectinload(Application.approver))
        .where(Application.id == application_id)
    )
    return result.scalar_one_or_none()


async def list_my_applications(
    db: AsyncSession,
    user_id: int,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Application], int]:
    query = select(Application).where(Application.applicant_id == user_id)
    count_query = select(func.count(Application.id)).where(
        Application.applicant_id == user_id
    )
    if status:
        query = query.where(Application.status == status)
        count_query = count_query.where(Application.status == status)

    query = (
        query.options(selectinload(Application.applicant), selectinload(Application.approver))
        .order_by(Application.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    total = (await db.execute(count_query)).scalar() or 0
    return items, total


async def list_pending_approvals(
    db: AsyncSession,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Application], int]:
    query = (
        select(Application)
        .options(selectinload(Application.applicant), selectinload(Application.approver))
        .where(
            Application.approver_id == user_id,
            Application.status == ApplicationStatus.pending,
        )
        .order_by(Application.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    count_query = select(func.count(Application.id)).where(
        Application.approver_id == user_id,
        Application.status == ApplicationStatus.pending,
    )
    result = await db.execute(query)
    items = list(result.scalars().all())
    total = (await db.execute(count_query)).scalar() or 0
    return items, total


async def approve_application(
    db: AsyncSession, application: Application, user: User
) -> Application:
    application.status = ApplicationStatus.approved
    audit = AuditLog(
        application_id=application.id,
        action=AuditAction.approved,
        performed_by_id=user.id,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(application)
    return application


async def reject_application(
    db: AsyncSession, application: Application, user: User, reason: str
) -> Application:
    application.status = ApplicationStatus.rejected
    application.reject_reason = reason
    audit = AuditLog(
        application_id=application.id,
        action=AuditAction.rejected,
        performed_by_id=user.id,
        comment=reason,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(application)
    return application


async def resubmit_application(
    db: AsyncSession,
    application: Application,
    user: User,
    title: str | None,
    reason: str | None,
    content: str | None,
    approver_id: int | None,
) -> Application:
    new_app = Application(
        title=title or application.title,
        reason=reason or application.reason,
        content=content or application.content,
        status=ApplicationStatus.pending,
        applicant_id=user.id,
        approver_id=approver_id or application.approver_id,
        previous_id=application.id,
    )
    application.status = ApplicationStatus.voided
    db.add(new_app)
    await db.flush()

    audit = AuditLog(
        application_id=new_app.id,
        action=AuditAction.resubmitted,
        performed_by_id=user.id,
    )
    db.add(audit)

    audit_void = AuditLog(
        application_id=application.id,
        action=AuditAction.voided,
        performed_by_id=user.id,
        comment="resubmitted",
    )
    db.add(audit_void)
    await db.commit()
    await db.refresh(new_app)
    return new_app


async def void_application(
    db: AsyncSession, application: Application, user: User
) -> Application:
    application.status = ApplicationStatus.voided
    audit = AuditLog(
        application_id=application.id,
        action=AuditAction.voided,
        performed_by_id=user.id,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(application)
    return application


async def list_audit_logs(
    db: AsyncSession,
    status: str | None = None,
    action: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    applicant_id: int | None = None,
    approver_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    query = (
        select(AuditLog)
        .options(
            selectinload(AuditLog.performed_by),
            selectinload(AuditLog.application).selectinload(Application.applicant),
            selectinload(AuditLog.application).selectinload(Application.approver),
        )
    )
    count_query = select(func.count(AuditLog.id))

    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)

    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
        count_query = count_query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
        count_query = count_query.where(AuditLog.created_at <= end_date)

    if status or applicant_id or approver_id:
        subq = select(Application.id)
        if status:
            subq = subq.where(Application.status == status)
        if applicant_id:
            subq = subq.where(Application.applicant_id == applicant_id)
        if approver_id:
            subq = subq.where(Application.approver_id == approver_id)
        query = query.where(AuditLog.application_id.in_(subq))
        count_query = count_query.where(AuditLog.application_id.in_(subq))

    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    items = list(result.scalars().all())
    total = (await db.execute(count_query)).scalar() or 0
    return items, total


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).where(User.is_active == True).order_by(User.display_name)
    )
    return list(result.scalars().all())
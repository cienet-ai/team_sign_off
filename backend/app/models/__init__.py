import enum
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    oidc_sub: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(128), unique=True)
    email: Mapped[str | None] = mapped_column(String(256))
    display_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    voided = "voided"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    reason: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.pending
    )
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reject_reason: Mapped[str | None] = mapped_column(Text)
    previous_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    applicant: Mapped[User] = relationship("User", foreign_keys=[applicant_id])
    approver: Mapped[User] = relationship("User", foreign_keys=[approver_id])


class AuditAction(str, enum.Enum):
    created = "created"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    resubmitted = "resubmitted"
    voided = "voided"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    performed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    application: Mapped[Application] = relationship("Application")
    performed_by: Mapped[User] = relationship("User")
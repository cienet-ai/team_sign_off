from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None
    display_name: str
    role: str
    is_active: bool
    created_at: datetime


class ApplicationCreate(BaseModel):
    title: str
    reason: str
    content: str
    approver_id: int


class ApplicationUpdate(BaseModel):
    title: str | None = None
    reason: str | None = None
    content: str | None = None
    approver_id: int | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    reason: str
    content: str
    status: str
    applicant_id: int
    approver_id: int
    reject_reason: str | None
    previous_id: int | None
    created_at: datetime
    updated_at: datetime
    applicant: UserOut | None = None
    approver: UserOut | None = None


class RejectRequest(BaseModel):
    reason: str


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    action: str
    performed_by_id: int
    comment: str | None
    created_at: datetime
    performed_by: UserOut | None = None
    application: ApplicationOut | None = None


class AuditFilter(BaseModel):
    status: str | None = None
    action: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    applicant_id: int | None = None
    approver_id: int | None = None
    limit: int = 50
    offset: int = 0


class PaginatedResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
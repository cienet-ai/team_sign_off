from fastapi import APIRouter, Depends

from backend.app.database import get_db
from backend.app.middleware import get_current_user
from backend.app.models import User
from backend.app.schemas import UserOut
from backend.app.services import list_users
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_users(db)
from fastapi import APIRouter, Depends
from backend.app.middleware import get_current_user
from backend.app.models import User
from backend.app.schemas import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
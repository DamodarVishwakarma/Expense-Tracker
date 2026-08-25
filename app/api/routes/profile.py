# ruff: noqa: B008 - FastAPI uses dependency calls as parameter markers.

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.routes.auth import public_user
from app.models.user import UserInDB, UserPublic

router = APIRouter(tags=["profile"])


@router.get("/api/profile", response_model=UserPublic)
@router.get("/profile", response_model=UserPublic, include_in_schema=False)
def read_profile(current_user: UserInDB = Depends(get_current_user)) -> UserPublic:
    return public_user(current_user)

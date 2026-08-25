from app.core.security import verify_password
from app.models.user import UserInDB
from app.repositories.user_repository import get_user_by_email


def authenticate_user(email: str, password: str) -> UserInDB | None:
    user = get_user_by_email(email)
    if (
        user is None
        or user.disabled
        or not verify_password(password, user.hashed_password)
    ):
        return None
    return user

from sqlalchemy.exc import IntegrityError

from app.models.user import UserCreate, UserInDB
from app.repositories.user_repository import create_user as repository_create_user


def create_user(data: UserCreate) -> UserInDB | None:
    try:
        return repository_create_user(data)
    except IntegrityError:
        return None

from uuid import uuid4

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.database import session_scope
from app.db.models import UserRecord
from app.models.user import UserCreate, UserInDB


def _to_user(record: UserRecord | None) -> UserInDB | None:
    if record is None:
        return None
    return UserInDB.model_validate(record, from_attributes=True)


def get_user(username: str) -> UserInDB | None:
    with session_scope() as session:
        return _to_user(session.get(UserRecord, username))


def get_user_by_email(email: str) -> UserInDB | None:
    with session_scope() as session:
        record = session.scalar(
            select(UserRecord).where(UserRecord.email == email.strip().lower())
        )
        return _to_user(record)


def create_user(data: UserCreate) -> UserInDB:
    record = UserRecord(
        username=uuid4().hex,
        full_name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        disabled=False,
    )
    with session_scope() as session:
        session.add(record)
        session.flush()
        return _to_user(record)

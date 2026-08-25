from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import delete, extract, select

from app.db.database import session_scope
from app.db.models import ExpenseRecord
from app.models.expense import ExpenseCreate, ExpensePublic, ExpenseUpdate


def _to_cents(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _to_expense(record: ExpenseRecord) -> ExpensePublic:
    return ExpensePublic(
        id=record.id,
        title=record.title,
        amount=Decimal(record.amount_cents) / 100,
        date=record.expense_date,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def list_expenses(username: str, year: int | None = None) -> list[ExpensePublic]:
    statement = select(ExpenseRecord).where(ExpenseRecord.user_username == username)
    if year is not None:
        statement = statement.where(extract("year", ExpenseRecord.expense_date) == year)
    statement = statement.order_by(
        ExpenseRecord.expense_date.desc(), ExpenseRecord.id.desc()
    )
    with session_scope() as session:
        return [_to_expense(record) for record in session.scalars(statement).all()]


def get_expense(expense_id: int, username: str) -> ExpensePublic | None:
    with session_scope() as session:
        record = session.scalar(
            select(ExpenseRecord).where(
                ExpenseRecord.id == expense_id,
                ExpenseRecord.user_username == username,
            )
        )
        return _to_expense(record) if record else None


def create_expense(username: str, data: ExpenseCreate) -> ExpensePublic:
    record = ExpenseRecord(
        user_username=username,
        title=data.title,
        amount_cents=_to_cents(data.amount),
        expense_date=data.date,
    )
    with session_scope() as session:
        session.add(record)
        session.flush()
        return _to_expense(record)


def update_expense(
    expense_id: int, username: str, data: ExpenseUpdate
) -> ExpensePublic | None:
    with session_scope() as session:
        record = session.scalar(
            select(ExpenseRecord).where(
                ExpenseRecord.id == expense_id,
                ExpenseRecord.user_username == username,
            )
        )
        if record is None:
            return None
        values = data.model_dump(exclude_unset=True)
        if "title" in values:
            record.title = values["title"]
        if "amount" in values:
            record.amount_cents = _to_cents(values["amount"])
        if "date" in values:
            record.expense_date = values["date"]
        session.flush()
        return _to_expense(record)


def delete_expense(expense_id: int, username: str) -> bool:
    with session_scope() as session:
        result = session.execute(
            delete(ExpenseRecord).where(
                ExpenseRecord.id == expense_id,
                ExpenseRecord.user_username == username,
            )
        )
        return result.rowcount == 1

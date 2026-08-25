# ruff: noqa: B008 - FastAPI uses dependency calls as parameter markers.

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_current_user
from app.models.expense import ExpenseCreate, ExpensePublic, ExpenseUpdate
from app.models.user import UserInDB
from app.repositories import expense_repository

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpensePublic])
def list_expenses(
    year: int | None = Query(default=None, ge=1900, le=9999),
    user: UserInDB = Depends(get_current_user),
) -> list[ExpensePublic]:
    return expense_repository.list_expenses(user.username, year)


@router.post("", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate, user: UserInDB = Depends(get_current_user)
) -> ExpensePublic:
    return expense_repository.create_expense(user.username, data)


@router.get("/{expense_id}", response_model=ExpensePublic)
def get_expense(
    expense_id: int, user: UserInDB = Depends(get_current_user)
) -> ExpensePublic:
    expense = expense_repository.get_expense(expense_id, user.username)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpensePublic)
def update_expense(
    expense_id: int, data: ExpenseUpdate, user: UserInDB = Depends(get_current_user)
) -> ExpensePublic:
    expense = expense_repository.update_expense(expense_id, user.username, data)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int, user: UserInDB = Depends(get_current_user)
) -> Response:
    if not expense_repository.delete_expense(expense_id, user.username):
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

import asyncio
import json
import os
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode

from app.core.config import get_settings
from app.db.database import init_db
from app.main import app
from app.models.expense import ExpenseCreate, ExpenseUpdate
from app.models.user import UserCreate
from app.repositories import expense_repository
from app.repositories.user_repository import create_user, get_user_by_email
from app.services.auth_service import authenticate_user


async def request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    form: bool = False,
) -> tuple[int, object]:
    sent: list[dict] = []
    if form:
        raw_body = urlencode(body or {}).encode()
        content_type = b"application/x-www-form-urlencoded"
    else:
        raw_body = json.dumps(body).encode() if body is not None else b""
        content_type = b"application/json"
    headers = [(b"content-type", content_type)]
    if token:
        headers.append((b"authorization", f"Bearer {token}".encode()))
    received = False

    async def receive() -> dict:
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": raw_body, "more_body": False}

    async def send(message: dict) -> None:
        sent.append(message)

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": headers,
            "client": ("test", 50000),
            "server": ("test", 80),
        },
        receive,
        send,
    )
    status = next(
        message["status"]
        for message in sent
        if message["type"] == "http.response.start"
    )
    content = b"".join(
        message.get("body", b"")
        for message in sent
        if message["type"] == "http.response.body"
    )
    return status, json.loads(content) if content else None


class BackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["DATABASE_URL"] = (
            Path(self.temp_dir.name).joinpath("test.db").as_uri()
        ).replace("file:///", "sqlite:///")
        get_settings.cache_clear()
        init_db()

    def tearDown(self) -> None:
        get_settings.cache_clear()
        os.environ.pop("DATABASE_URL", None)
        self.temp_dir.cleanup()

    def create_test_user(self, email: str):
        return create_user(
            UserCreate(name="Test User", email=email, password="correct-horse")
        )

    def test_user_is_persisted_and_password_is_hashed(self) -> None:
        user = self.create_test_user("Owner@Example.com")
        stored = get_user_by_email("owner@example.com")

        self.assertIsNotNone(stored)
        self.assertNotEqual(stored.hashed_password, "correct-horse")
        self.assertEqual(user.email, "owner@example.com")
        self.assertEqual(authenticate_user("OWNER@example.com", "correct-horse"), user)
        self.assertIsNone(authenticate_user("owner@example.com", "wrong-password"))

    def test_expense_crud_and_user_isolation(self) -> None:
        owner = self.create_test_user("owner@example.com")
        other = self.create_test_user("other@example.com")
        created = expense_repository.create_expense(
            owner.username,
            ExpenseCreate(
                title="Lunch", amount=Decimal("12.34"), date=date(2026, 8, 25)
            ),
        )

        self.assertEqual(created.amount, Decimal("12.34"))
        self.assertEqual(len(expense_repository.list_expenses(owner.username, 2026)), 1)
        self.assertEqual(expense_repository.list_expenses(owner.username, 2025), [])
        self.assertIsNone(expense_repository.get_expense(created.id, other.username))
        self.assertIsNone(
            expense_repository.update_expense(
                created.id, other.username, ExpenseUpdate(title="Stolen")
            )
        )
        self.assertFalse(expense_repository.delete_expense(created.id, other.username))

        updated = expense_repository.update_expense(
            created.id, owner.username, ExpenseUpdate(amount=Decimal("14.50"))
        )
        self.assertEqual(updated.amount, Decimal("14.50"))
        self.assertTrue(expense_repository.delete_expense(created.id, owner.username))
        self.assertEqual(expense_repository.list_expenses(owner.username), [])

    def test_authenticated_api_flow(self) -> None:
        status, signup = asyncio.run(
            request(
                "POST",
                "/api/auth/signup",
                {
                    "name": "API User",
                    "email": "api@example.com",
                    "password": "safe-password",
                },
            )
        )
        self.assertEqual(status, 201)
        self.assertNotIn("password", signup["user"])

        status, swagger_token = asyncio.run(
            request(
                "POST",
                "/api/auth/token",
                {"username": "api@example.com", "password": "safe-password"},
                form=True,
            )
        )
        self.assertEqual(status, 200)
        self.assertIn("access_token", swagger_token)

        status, expense = asyncio.run(
            request(
                "POST",
                "/api/expenses",
                {"title": "Train", "amount": 125.75, "date": "2026-08-25"},
                signup["access_token"],
            )
        )
        self.assertEqual(status, 201)
        self.assertEqual(expense["amount"], 125.75)

        status, expenses = asyncio.run(
            request("GET", "/api/expenses", token=signup["access_token"])
        )
        self.assertEqual(status, 200)
        self.assertEqual([item["title"] for item in expenses], ["Train"])


if __name__ == "__main__":
    unittest.main()

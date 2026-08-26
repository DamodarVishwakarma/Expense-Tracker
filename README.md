# Expense Manager API

FastAPI backend using SQLAlchemy 2.x with SQLite for local development and
PostgreSQL for AWS RDS. Users are stored with bcrypt password hashes, and every
expense is owned by its authenticated user. Money is stored as integer cents to
avoid floating-point rounding errors.

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a && source .env && set +a
uvicorn app.main:app --reload
```

Set a strong `JWT_SECRET_KEY` in your environment before any non-local deployment.
The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Database configuration

Set `DATABASE_URL` to the SQLAlchemy connection URL. The default is local SQLite:

```env
DATABASE_URL=sqlite:///app/db/app.db
```

For AWS RDS PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@RDS_ENDPOINT:5432/DATABASE
```

Configure the RDS security group to allow port `5432` only from the backend's
security group. Store the production URL in your deployment secret manager and do
not commit it to the repository.

## API

- `POST /api/auth/signup` — JSON: `name`, `email`, `password`
- `POST /api/auth/login` — JSON: `email`, `password`
- `POST /api/auth/token` — OAuth2 form login used by Swagger UI
- `GET /api/profile` — current user
- `GET /api/expenses?year=2026` — current user's expenses
- `POST /api/expenses` — JSON: `title`, `amount`, `date` (`YYYY-MM-DD`)
- `GET /api/expenses/{id}`
- `PATCH /api/expenses/{id}`
- `DELETE /api/expenses/{id}`

Except for signup and login, send `Authorization: Bearer <access_token>`.

## Verify

```bash
python -m unittest discover -v
ruff check app tests
```

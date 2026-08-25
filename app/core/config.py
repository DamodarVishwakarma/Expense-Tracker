import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_path: Path
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    default_db = Path(__file__).resolve().parents[1] / "db" / "app.db"
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return Settings(
        app_name=os.getenv("APP_NAME", "Expense Manager API"),
        database_path=Path(os.getenv("DATABASE_PATH", str(default_db))).expanduser(),
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY", "change-this-to-a-random-64-char-hex-string"
        ),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        cors_origins=tuple(
            origin.strip() for origin in origins.split(",") if origin.strip()
        ),
    )

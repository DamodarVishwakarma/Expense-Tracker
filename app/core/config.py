import os
from dataclasses import dataclass
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return Settings(
        app_name=os.getenv("APP_NAME", "Expense Manager API"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///app/db/app.db"),
        jwt_secret_key=os.getenv(
            "JWT_SECRET_KEY", "change-this-to-a-random-64-char-hex-string"
        ),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        cors_origins=tuple(
            origin.strip() for origin in origins.split(",") if origin.strip()
        ),
    )

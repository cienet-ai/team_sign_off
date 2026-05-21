from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "APP_", "env_file": ".env", "extra": "ignore"}

    database_url: str = "sqlite+aiosqlite:///./data.db"
    debug: bool = False

    oidc_issuer: str = "http://localhost:8080/realms/team-sign-off"
    oidc_client_id: str = "team-sign-off-frontend"
    oidc_client_secret: str = ""

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "hsm.db"
    dns_lifetime: int = 5
    http_timeout: int = 8
    wiki_timeout: int = 10
    cors_origins: list[str] = ["http://localhost:5173"]
    import_rate_limit: str = "3/hour"


settings = Settings()

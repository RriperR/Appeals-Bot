from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class Settings(BaseSettings):
    database_url: str | None = None

    # Вариант B: собираем из POSTGRES_*
    postgres_db: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str = "db"
    postgres_port: int = 5432

    bot_token: str
    admin_ids: list[int] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def assemble_url(self):
        if not self.database_url:
            if self.postgres_db and self.postgres_user and self.postgres_password:
                self.database_url = (
                    f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                    f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
                )
        return self

settings = Settings()

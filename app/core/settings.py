from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    bot_token: str
    admin_ids: list[int] = []

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()

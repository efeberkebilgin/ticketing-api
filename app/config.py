from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ticketing API"
    database_url: str = "mysql+pymysql://ticketing:ticketing@localhost:3307/ticketing"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 15

    model_config = SettingsConfigDict(env_file=".env")

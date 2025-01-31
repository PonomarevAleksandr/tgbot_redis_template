from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_HOST_EXTERNAL: str
    MONGO_PORT: int
    MONGO_PORT_EXTERNAL: int
    MONGO_DB_NAME: str
    MONGO_DB_ROOT_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    model_config =  SettingsConfigDict(env_file="/app/.env")

settings = Settings()
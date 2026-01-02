from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    INGESTION_ENDPOINT: str
    DEVICE_ID: str


GlobalSetting = AppConfig()

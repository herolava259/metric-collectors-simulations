from pydantic import BaseSettings, Field, SecretStr



class AppConfig(BaseSettings):
    INGESTION_ENDPOINT: str
    DEVICE_ID: str
    REDIS_URL: str
    INGESTION_API_KEY: SecretStr = Field(default=None, env="INGESTION_API_KEY")
    DEBUG_MODE: bool = False
    EXCLUSIVE_LOCK_KEY: str = Field(default="package-exclusive-key")
    ACQUIRE_LOCK_TIMEOUT: float = Field(default=60)


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"




GlobalSetting = AppConfig()

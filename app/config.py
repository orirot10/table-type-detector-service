import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "table-type-detector-service"
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model/table_type_identification.pt")
    LABELS: str = os.getenv("TABLE_LABELS", "balance,activity")
    API_KEY: str | None = None  # If you want to require it - set default or env here

    class Config:
        env_file = ".env"


settings = Settings()




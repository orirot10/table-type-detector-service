from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "table-type-detector-service"
    MODEL_PATH: str = "model/table_type_identification.pt"
    LABELS: str = "balance,activity"
    API_KEY: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # לא לזרוק שגיאה על env שלא מוגדרים כ־fields


settings = Settings()

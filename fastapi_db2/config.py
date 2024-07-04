from pydantic_settings import BaseSettings
from pydantic import Extra
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    DB2_URL: str
    DB2_USER: str
    DB2_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    class Config:
        env_file = ".env"
        extra = Extra.forbid  # To ensure no extra fields are allowed

settings = Settings()

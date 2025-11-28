import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Research Integrity Project"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY" # In prod, read from env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./ria.db"

    # External Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    class Config:
        case_sensitive = True

settings = Settings()

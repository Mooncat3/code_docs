import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = "Code Documentation API"
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@codedocs.example")
    secret_key: str = os.environ["SECRET_KEY"]
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_hours: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 3000))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./code_docs.db")

settings = Settings()

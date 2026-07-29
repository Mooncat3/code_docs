class Settings:
    app_name: str = "Code Documentation API"
    admin_email: str = "admin@codedocs.example"
    secret_key: str = "84Z6hEaY7CoWEE1XhClGkwynEpMh88MzPmjYWiMR"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 3000
    database_url: str = "sqlite:///./code_docs.db"

    class Config:
        env_file = ".env"


settings = Settings()

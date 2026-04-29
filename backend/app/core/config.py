import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    JWT_SECRET: str = os.getenv("JWT_SECRET")

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

settings = Settings()

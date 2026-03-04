import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GETSONGKEY_API_URL: str | None = os.getenv("GETSONGKEY_API_URL")
    GETSONGKEY_API_KEY: str | None = os.getenv("GETSONGKEY_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

settings = Settings()

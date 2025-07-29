import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:
    """
    A class to hold all application settings, loaded from environment variables.
    """
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME")

# Create a single, importable instance of the settings
settings = Settings()
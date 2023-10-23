from os import getenv

from dotenv import load_dotenv

from app.core.config import settings, Settings

# load_dotenv(getenv("ENV_FILE"))
load_dotenv()

# settings: Settings = Settings()  # type: ignore
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
GUILD_ID = os.getenv("GUILD")

BASE_DIR = pathlib.Path(__file__).parent
SERVICE_ACCOUNT_DIR = BASE_DIR / "service_account.json"
GRAPHIC_RESOURCES_DIR = BASE_DIR / "graphic_resources"
JUNK_DIR = BASE_DIR / "junk_storage"
SURVEYS_DIR = BASE_DIR / "surveys"

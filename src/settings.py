from decouple import Csv, config
from dotenv import load_dotenv

load_dotenv()


FLAGSMITH_API_URL = config("FLAGSMITH_API_URL")
SERVER_SIDE_ENVIRONMENT_KEYS = config("SERVER_SIDE_ENVIRONMENT_KEYS", cast=Csv())
ENVIRONMENT_API_KEYS = config("ENVIRONMENT_API_KEYS", cast=Csv())
API_POLL_FREQUENCY = config("API_POLL_FREQUENCY", cast=int, default=10)

from decouple import Csv, config

FLAGSMITH_API_URL = config("FLAGSMITH_API_URL")
FLAGSMITH_API_TOKEN = config("FLAGSMITH_API_TOKEN")
ENVIRONMENT_API_KEYS = config("ENVIRONMENT_API_KEYS", cast=Csv())
API_POLL_FREQUENCY = config("API_POLL_FREQUENCY", cast=int, default=10)

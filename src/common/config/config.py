import os
from dotenv import load_dotenv

load_dotenv()


class LLMProviders:
    class Anthropic:
        API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    class Google:
        API_KEY = os.getenv("GOOGLE_API_KEY", "")


class Auth:
    class Descope:
        DESCOPE_PROJECT_KEY = os.getenv("DESCOPE_PROJECT_KEY", "")
        DESCOPE_TOKEN_URL = os.getenv(
            "DESCOPE_TOKEN_URL", "https://api.descope.com/oauth2/v1/apps/token"
        )
        DESCOPE_CLIENT_ID = os.getenv("DESCOPE_CLIENT_ID", "")
        DESCOPE_CLIENT_SECRET = os.getenv("DESCOPE_CLIENT_SECRET", "")

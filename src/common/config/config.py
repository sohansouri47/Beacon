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

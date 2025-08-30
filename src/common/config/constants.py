import geocoder

g = geocoder.ip("me")
print(g.latlng)


class LlmConfig:
    class Anthropic:
        HAIKU_3_MODEL = "anthropic/claude-3-haiku-20240307"

    class Google:
        GOOGLE_1_5_MODEL = "gemini/gemini-1.5-pro-latest"

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    openrouter_api_key: str = ""
    pocketbase_url: str = "http://pocketbase:8090"
    pocketbase_superuser_email: str = "admin@manaforge.local"
    pocketbase_superuser_password: str = "changeme"

    model_config = {"env_file": ".env"}


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    openrouter_api_key: str = ""
    replicate_api_token: str = ""
    # Model-scoped endpoint (no version hash) so Replicate serves the latest
    # version automatically. To pin a specific version, append the hash, e.g.
    # "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedc9b".
    replicate_music_model: str = "meta/musicgen"
    pocketbase_url: str = "http://pocketbase:8090"
    pocketbase_superuser_email: str = "admin@manaforge.local"
    pocketbase_superuser_password: str = "changeme"

    model_config = {"env_file": ".env"}


settings = Settings()

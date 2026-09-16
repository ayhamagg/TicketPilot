from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Anthropic AI
    ANTHROPIC_API_KEY: str = ""

    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPOSITORY: str = ""

    # App
    APP_NAME: str = "TicketPilot"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
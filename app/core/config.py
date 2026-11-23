
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI QA Agent"

    app_env: Literal[
        "development",
        "test",
        "stage",
        "production",
    ] = "development"

    database_url: str = "sqlite:///./qa_agent.db"

    # Jira configuration
    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = Field(
        default=None,
        repr=False,
    )

    qa_webhook_token: str | None = Field(
        default=None,
        repr=False,
    )

    # LLM configuration
    llm_base_url: str = "http://localhost:4000/v1"
    llm_api_key: str | None = Field(
        default=None,
        repr=False,
    )
    llm_model: str = "medium_llm"

    # Agent execution limits
    agent_max_steps: int = Field(
        default=4,
        ge=1,
        le=20,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

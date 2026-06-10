from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend Learn"
    database_url: str = Field(
        default="mysql+pymysql://app_user:app_password@127.0.0.1:3306/backend_learn",
        validation_alias="DATABASE_URL",
    )
    auto_create_tables: bool = Field(default=True, validation_alias="AUTO_CREATE_TABLES")

    agent_mode: str = Field(default="mock", validation_alias="AGENT_MODE")
    litellm_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LITELLM_API_KEY", "MOONSHOT_API_KEY"),
    )
    litellm_base_url: str = Field(
        default="https://llm-developer.fzzixun.com/v1",
        validation_alias=AliasChoices("LITELLM_BASE_URL", "KIMI_BASE_URL"),
    )
    litellm_model_name: str = Field(
        default="claude-sonnet-4-6",
        validation_alias=AliasChoices("LITELLM_MODEL_NAME", "KIMI_MODEL"),
    )
    litellm_thinking: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LITELLM_THINKING", "KIMI_THINKING"),
    )
    litellm_timeout_seconds: float = Field(
        default=20.0,
        validation_alias=AliasChoices("LITELLM_TIMEOUT_SECONDS", "KIMI_TIMEOUT_SECONDS"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def use_mock_agent(self) -> bool:
        return self.agent_mode.lower() not in {"litellm", "kimi"} or not self.litellm_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()

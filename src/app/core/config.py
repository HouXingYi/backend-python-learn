from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend Learn"
    database_url: str = Field(
        default="mysql+pymysql://app_user:app_password@127.0.0.1:3306/backend_learn",
        validation_alias="DATABASE_URL",
    )
    auto_create_tables: bool = Field(default=True, validation_alias="AUTO_CREATE_TABLES")

    agent_mode: str = Field(default="mock", validation_alias="AGENT_MODE")
    moonshot_api_key: str | None = Field(default=None, validation_alias="MOONSHOT_API_KEY")
    kimi_base_url: str = Field(
        default="https://api.moonshot.ai/v1",
        validation_alias="KIMI_BASE_URL",
    )
    kimi_model: str = Field(default="kimi-k2.6", validation_alias="KIMI_MODEL")
    kimi_thinking: str = Field(default="disabled", validation_alias="KIMI_THINKING")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def use_mock_agent(self) -> bool:
        return self.agent_mode.lower() != "kimi" or not self.moonshot_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from task_plan_server.my_logging import LogFormat


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    env: Literal["local", "test", "prod"] = "local"
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/task_plan_server"
    db_pool_size: int = 20
    db_max_overflow: int = 20
    db_echo: bool = False
    log_level: str = "INFO"
    log_format: LogFormat | None = None  # None 이면 env 로 결정

    @property
    def effective_log_format(self) -> LogFormat:
        if self.log_format is not None:
            return self.log_format
        return "json-color" if self.env == "local" else "json"

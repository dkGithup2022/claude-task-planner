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
    # 지식 검색에 벡터 검색을 더할지. 끄면 전문 검색만 쓰고 임베딩 모델을 띄우지 않는다
    memory_search_vector: bool = False  # APP_MEMORY_SEARCH_VECTOR
    memory_search_vector_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    # 모델이 내는 벡터 길이. 모델을 바꾸면 같이 바꾼다. 다르면 서버가 뜨지 않는다
    memory_search_vector_dimension: int = 384

    @property
    def effective_log_format(self) -> LogFormat:
        if self.log_format is not None:
            return self.log_format
        return "json-color" if self.env == "local" else "json"

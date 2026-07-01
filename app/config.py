from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    catalog_path: str = "data/shl_product_catalog.json"
    chroma_path: str = "data/chroma"
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_fallback_model: str = "BAAI/bge-small-en-v1.5"
    use_reranker: bool = True
    reranker_model: str = "BAAI/bge-reranker-base"

    max_recommendations: int = 10
    log_level: str = "INFO"
    cors_origins: str = Field(default="http://localhost:5173")
    retrieval_mode: str = Field(default="keyword")  # keyword | embedding
    lazy_init: bool = Field(default=True)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CIDWeb Skin Analytics API"
    app_env: str = Field(default="demo", alias="APP_ENV")
    api_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql://cidweb:cidweb@postgres:5432/cidweb",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    jwt_secret: str = Field(default="change-me-in-demo", alias="JWT_SECRET")
    timezone: str = Field(default="Asia/Shanghai", alias="TZ")
    file_storage_root: str = Field(default="/storage", alias="FILE_STORAGE_ROOT")
    raw_storage_root: str = Field(default="/storage/raw", alias="RAW_STORAGE_ROOT")
    intermediate_storage_root: str = Field(default="/storage/intermediate", alias="INTERMEDIATE_STORAGE_ROOT")
    export_storage_root: str = Field(default="/storage/exports", alias="EXPORT_STORAGE_ROOT")
    chart_storage_root: str = Field(default="/storage/charts", alias="CHART_STORAGE_ROOT")
    manifest_storage_root: str = Field(default="/storage/manifests", alias="MANIFEST_STORAGE_ROOT")

    model_config = SettingsConfigDict(
        env_file=".env.demo",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

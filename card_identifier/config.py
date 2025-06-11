__version__ = "0.1.0"
__pypi_packagename__ = "collectable-card-identifier"

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from card_identifier.storage import StorageConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CARD_IDENTIFIER_")
    debug: bool = Field(default=False, env="APP_DEBUG")
    storage: StorageConfig

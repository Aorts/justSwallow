import os
from typing import List, Type

from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(__file__))


class Settings(BaseSettings):
    CONFIG_NAME: str = "base"
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hermes secret key")

    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT: int = os.getenv("MONGODB_PORT", 27017)
    MONGODB_DB: str = os.getenv("MONGODB_DB", "hermesdb")
    MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME", "")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    JWT_SECRET_KEY: str = "JWT_SECRET"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS: int = 24 * 60 * 60

    HERMES_DATA_DIR: str = os.getenv("HERMES_DATA_DIR", "/tmp/hermes")


class DevelopmentConfig(Settings):
    CONFIG_NAME: str = "development"
    DEBUG: bool = True


class TestingConfig(Settings):
    CONFIG_NAME: str = "test"
    DEBUG: bool = True
    TESTING: bool = True


class ProductionConfig(Settings):
    CONFIG_NAME: str = "production"
    DEBUG: bool = False
    TESTING: bool = False


def get_config(environment="development"):
    global settings
    EXPORT_CONFIGS: List[Type[Settings]] = [
        DevelopmentConfig,
        TestingConfig,
        ProductionConfig,
    ]
    config_by_environment = {cfg().CONFIG_NAME: cfg() for cfg in EXPORT_CONFIGS}
    settings = config_by_environment[environment]

    return settings


settings = get_config()

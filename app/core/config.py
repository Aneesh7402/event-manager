from pydantic_settings import BaseSettings
from pydantic import Field
import redis
from dotenv import load_dotenv
import os

class DBSettings(BaseSettings):
    driver: str = Field(..., alias="DATABASE_DRIVER")
    server: str = Field(..., alias="DATABASE_SERVER")
    database: str = Field(..., alias="DATABASE_NAME")
    username: str = Field(..., alias="DATABASE_USERNAME")
    password: str = Field(..., alias="DATABASE_PASSWORD")
    port: str = Field(..., alias="DATABASE_PORT")

    @property
    def database_url(self):
        return (
        f"{self.driver}://{self.username}:{self.password}"
        f"@{self.server}:{self.port}/{self.database}"
    )

    class Config:
        env_file = "app/.env"
        extra = "ignore"

load_dotenv(dotenv_path='app/.env')

# Get Redis configuration from environment variables
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

REDIS_EVENTS_ZSET="events_cache"
# Instantiate DBSettings
db_settings = DBSettings()


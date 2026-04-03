from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MAX_API_TOKEN: str
    # MAX_CHAT_ID: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def database_url(self):
        user = f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        database = f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        return f"postgresql+asyncpg://{user}@{database}"

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:{quote(self.RABBITMQ_DEFAULT_PASS)}@" f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"
        )
    
    QUEUE_NAME: str = "cctv_scr_save"
    EXCHANGE_NAME_INPUT: str = "cctv_inc_send"
    EXCHANGE_NAME_OUTPUT: str = "cctv_msg_send"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Объект с переменными окружения
settings = Settings()


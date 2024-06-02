import os
from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    """Dataclass to store Telegram Bot specified data."""
    token: str
    openai_api: str
    admin_ids: list[int]


@dataclass
class DataBase:
    """Dataclass to store Telegram Bot database specified data."""
    host: str
    database: str
    port: str
    user: str
    password: str


@dataclass
class Config:
    """Dataclass to store configuration data for a Telegram Bot."""
    tg_bot: TgBot
    db: DataBase


def load_config(path: str | None = None) -> Config:
    """Load configuration data from .env file and create a dataclass."""
    if path:
        env = Env()
        env.read_env(path)
        return Config(
            tg_bot=TgBot(
                token=env('BOT_TOKEN'),
                openai_api=env('API_KEY'),
                admin_ids=list(map(int, env.list('ADMIN_IDS')))
            ),
            db=DataBase(
                host=env('HOST'),
                database=env('DATABASE'),
                port=env('PORT'),
                user=env('DB_USER'),
                password=env('PASSWORD'),
            )
        )
    else:
        return Config(
            tg_bot=TgBot(
                token=os.getenv('BOT_TOKEN'),
                openai_api=os.getenv('API_KEY'),
                admin_ids=[int(os.getenv('ADMIN_IDS'))]
            ),
            db=DataBase(
                host=os.getenv('HOST'),
                database=os.getenv('DATABASE'),
                port=os.getenv('PORT'),
                user=os.getenv('DB_USER'),
                password=os.getenv('PASSWORD'),
            )
        )

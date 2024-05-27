import asyncio
import logging

from openai import OpenAI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fluentogram import TranslatorHub
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.handlers import admin_handlers, user_command_handlers, user_callback_handlers, other_handlers
from bot.keyboards.main_menu import set_main_menu
from bot.database.connection_pool import ConnectionPool
from bot.middleware.outer import (DatabaseConnectionMiddleware, MessageTypeMiddleware,
                                  TranslatorRunnerMiddleware)
from bot.config_data.config import Config, load_config
from bot.services.i18n import create_translator_hub
from bot.scheduler.scheduler import send_new_words_idioms


logger = logging.getLogger(__name__)


async def main(env_file: str = None):
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config(env_file)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    openai_client = OpenAI(api_key=config.tg_bot.openai_api)

    translator_hub: TranslatorHub = create_translator_hub()

    db_params = {
        'host': config.db.host,
        'port': config.db.port,
        'database': config.db.database,
        'user': config.db.user,
        'password': config.db.password
    }

    pool = ConnectionPool(10, **db_params)

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.start()
    scheduler.add_job(send_new_words_idioms, 'cron',
                      hour=9,
                      minute=00,
                      kwargs={'bot': bot,
                              'pool': pool,
                              'translator_hub': translator_hub,
                              'openai_client': openai_client})

    dp.workflow_data.update({'pool': pool,
                             'admins': config.tg_bot.admin_ids,
                             'translator_hub': translator_hub,
                             'openai_client': openai_client})

    await set_main_menu(bot)

    dp.include_router(user_callback_handlers.router)
    dp.include_router(user_command_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(other_handlers.router)

    dp.update.outer_middleware(DatabaseConnectionMiddleware())
    dp.update.outer_middleware(TranslatorRunnerMiddleware())

    user_command_handlers.router.message.outer_middleware(MessageTypeMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    import sys
    filepath = None

    if len(sys.argv) == 2:
        filepath = sys.argv[1]

        try:
            asyncio.run(main(filepath))
        except (KeyboardInterrupt, SystemExit):
            logger.error("Bot stopped!")


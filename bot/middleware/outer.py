from typing import Any, Awaitable, Callable, Dict
import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, ContentType, User
from fluentogram import TranslatorHub

from bot.database.database_handler import DatabaseHandler


logger = logging.getLogger(__name__)


class DatabaseConnectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Acquire a database connection from the pool and put it into 'data' to be passed further to handlers."""

        user: User = data.get('event_from_user')
        if user is None:
            return

        pool = data.get('pool')
        try:
            connection = pool.acquire()
            db = DatabaseHandler(connection)
            data['db'] = db
            result = await handler(event, data)

            pool.release(connection)

            return result

        except TimeoutError:
            message: Message = event.message
            await message.answer(text="🚫 There is no database connection. Please, try again later. \n"
                                      "🚫 Отсутствует соединение с базой данных. Пожалуйста, попробуйте еще раз позже.")

            return


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Query user's language, create an instance of translator by locale and pass it further to handlers."""
        user: User = data.get('event_from_user')

        if user is None:
            return

        db = data.get('db')
        user_language = db.get_user_column_data(user.id, 'language')
        if user_language is None:
            user_language = 'ru'

        hub: TranslatorHub = data.get('translator_hub')
        data['i18n'] = hub.get_translator_by_locale(locale=user_language)

        return await handler(event, data)


class MessageTypeMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Filter out all messages that are not text (photo, document, sticker etc.)"""

        message: Message = data.get('event_update').message

        if message.content_type == ContentType.TEXT:
            result = await handler(event, data)
            return result

        else:
            text = data.get('i18n').get('not-text-message')
            await message.answer(text=text)

            return



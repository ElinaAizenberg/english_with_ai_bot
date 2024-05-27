from aiogram.filters import BaseFilter
from aiogram.types import Message
from openai import OpenAI
import logging

from bot.services.openai import check_sentence_for_new_words
from bot.services.utils import notify_admin
from bot.database.database_handler import DatabaseHandler


logger = logging.getLogger(__name__)


class UserExists(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler) -> bool:
        """Check if a user exists in the database."""
        return db.check_user_exists(user_id=message.from_user.id)


class UserNonActivated(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler) -> bool:
        """Check if user's status is 'non-activated'."""
        status = db.get_user_column_data(user_id=message.from_user.id, column_name='status')
        return status == 0


class UserActivated(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler) -> bool:
        """Check if user's status is 'activated'."""
        status = db.get_user_column_data(user_id=message.from_user.id, column_name='status')
        return status == 1


class UserFrozen(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler) -> bool:
        """Check if user's status is 'frozen'."""
        status = db.get_user_column_data(user_id=message.from_user.id, column_name='status')
        return status == 2


class UserAvailableChecks(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler) -> bool:
        """Check if a user has daily available checks (less than 2)."""
        current_checks: int = int(db.get_user_column_data(message.from_user.id, 'checks'))
        return current_checks < 2


class NewWordIdiomUsed(BaseFilter):
    async def __call__(self, message: Message, db: DatabaseHandler, openai_client: OpenAI) -> dict[str, int]:
        """Check if a user has used any of the new vocabulary items in the message for checking."""
        last_word_idiom = db.get_last_word_idiom(message.from_user.id)

        if not last_word_idiom:
            return {'words_used': 0}

        words_used = check_sentence_for_new_words(openai_client, message.text, last_word_idiom)
        boolean_list = [True if value_str.lower() == 'true' else False for value_str in words_used]
        total_sum = sum(boolean_list)

        return {'words_used': total_sum}


class AdminUserFilter(BaseFilter):
    async def __call__(self, message: Message, admins: list[int]) -> bool:
        """Check if user is an admin."""
        if int(message.from_user.id) in admins:
            return True

        await notify_admin(message.bot, admins, message.from_user.full_name, 'admin_command')
        return False



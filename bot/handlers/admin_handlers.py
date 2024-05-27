from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.filters.filters import AdminUserFilter


router = Router()


@router.message(Command(commands="users"), AdminUserFilter())
async def process_users_command(message: Message, db):
    """Handler for an admin command that queries how many users installed the bot.."""
    text: str = f"There are {db.get_total_rows()} users in the database."
    await message.answer(text=text)


@router.message(Command(commands="zero_checks"), AdminUserFilter())
async def process_zero_checks_command(message: Message, db):
    """Handler for an admin command that sets amount of checks to zero."""
    user_checks = db.get_user_column_data(message.from_user.id, 'checks')
    if user_checks != 0:
        db.change_column_value(message.from_user.id, 'users', 'checks', 0)

from aiogram import Bot
from aiogram.types import BotCommand

from bot.lexicon.lexicon import MENU_COMMANDS_EN


async def set_main_menu(bot: Bot):
    """Define main menu commands."""
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in MENU_COMMANDS_EN.items()
    ]
    await bot.set_my_commands(main_menu_commands)

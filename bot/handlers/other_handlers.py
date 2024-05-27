from aiogram import Router
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from fluentogram import TranslatorRunner

from bot.services.utils import notify_admin


router = Router()


@router.message()
async def process_general_message(message: Message, i18n: TranslatorRunner):
    """Handler that responds with general answer and link to ChatGPT bot to non-command messages."""
    text: str = i18n.get('chat-gpt-message')
    await message.answer(text=text)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, admins):
    """Handler to inform the admin when a user blocked the bot."""
    await notify_admin(event.bot, admins, event.from_user.full_name, 'user_blocked')

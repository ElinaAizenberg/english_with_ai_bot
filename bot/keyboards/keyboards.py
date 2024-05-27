from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.lexicon.lexicon import LEVEL_BUTTONS


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboad to select language after the /start command."""
    english_button = InlineKeyboardButton(text='English', callback_data='select_en')
    russian_button = InlineKeyboardButton(text='Русский', callback_data='select_ru')

    buttons = [[english_button, russian_button]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_contact_developer_keyboard(text: str, user_id: str) -> InlineKeyboardMarkup:
    """Create a keyboard with developer's Telegram account button."""
    buttons = [[InlineKeyboardButton(
        text=text,
        url=f'tg://user?id={user_id}'
    )]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_settings_keyboard(keyboard_buttons: dict[str, str]) -> InlineKeyboardMarkup:
    """Create a keyboard for /account command."""
    language_button = InlineKeyboardButton(text=keyboard_buttons['language'], callback_data='select_language')
    level_button = InlineKeyboardButton(text=keyboard_buttons['level'], callback_data='select_level')
    topic_button = InlineKeyboardButton(text=keyboard_buttons['topic'], callback_data='select_topic')
    close_button = InlineKeyboardButton(text=keyboard_buttons['close'], callback_data='remove_message')

    buttons: list = [language_button, level_button, topic_button, close_button]
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=1)

    return kb_builder.as_markup()


def get_settings_language_keyboard(keyboard_buttons: dict[str, str]) -> InlineKeyboardMarkup:
    """Create a keyboard to select language in /settings."""
    english_lang_button = InlineKeyboardButton(text='English', callback_data='select_english')
    russian_lang_button = InlineKeyboardButton(text='Русский', callback_data='select_russian')
    back_button = InlineKeyboardButton(text=keyboard_buttons['back'], callback_data='back_to_settings')

    buttons = [[english_lang_button, russian_lang_button], [back_button]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_settings_level_keyboard(keyboard_buttons: dict[str, str]) -> InlineKeyboardMarkup:
    """Create a keyboard to select English level in /settings."""
    buttons: list[InlineKeyboardButton] = []

    kb_builder = InlineKeyboardBuilder()
    for button in LEVEL_BUTTONS:
        buttons.append(InlineKeyboardButton(
            text=button,
            callback_data=button))

    buttons.append(InlineKeyboardButton(text=keyboard_buttons['back'], callback_data='back_to_settings'))
    kb_builder.row(*buttons, width=2)

    return kb_builder.as_markup()


def get_settings_topic_keyboard(keyboard_buttons: dict[str, str]) -> InlineKeyboardMarkup:
    """Create a keyboard to select topic in /settings."""
    topic_buttons = {k: v for k, v in keyboard_buttons.items() if
                     k != 'back'}

    buttons: list[InlineKeyboardButton] = []
    kb_builder = InlineKeyboardBuilder()

    for button, text in topic_buttons.items():
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))

    buttons.append(InlineKeyboardButton(text=keyboard_buttons['back'], callback_data='back_to_settings'))
    kb_builder.row(*buttons, width=1)

    return kb_builder.as_markup()


def get_new_word_idiom_keyboard(keyboard_buttons: dict[str, str], cambridge_url: str) -> InlineKeyboardMarkup:
    """Create a keyboard for new vocabulary message with a link to Cambridge website and 'Next' button if applicable."""
    cambridge_button = InlineKeyboardButton(text='Cambridge dictionary', url=cambridge_url)
    buttons: list = [cambridge_button]
    if keyboard_buttons:
        next_button = InlineKeyboardButton(text=keyboard_buttons['text'], callback_data=keyboard_buttons['callback'])
        buttons.append(next_button)

    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2)

    return kb_builder.as_markup()


